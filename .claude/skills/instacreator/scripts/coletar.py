#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
coletar.py — Descobre e baixa os reels/videos de melhor desempenho de um perfil
do Instagram, usando uma sessao ja logada do instaloader (conta "laranja").

Uso:
    python coletar.py <perfil> --conta <usuario_logado> [opcoes]

Exemplo:
    python coletar.py @cria.digital --conta minhalaranja --top 5 --scan 40

Saida:
    Cria uma pasta <out>/ com:
      - <shortcode>.mp4            (video baixado)
      - manifest.json             (lista rankeada com metricas + caminhos)
    E imprime o manifest.json no stdout (JSON) para o orquestrador ler.

NAO faz analise. So coleta. A analise (frames/transcricao) e feita depois
pela skill `watch` + Claude.
"""
import argparse
import itertools
import json
import sys
import time
from pathlib import Path

try:
    import instaloader
except ImportError:
    sys.exit("ERRO: instaloader nao instalado. Rode:  pip install instaloader")


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def main():
    ap = argparse.ArgumentParser(description="Coleta os top videos de um perfil do Instagram.")
    ap.add_argument("perfil", help="@usuario ou usuario do perfil-alvo")
    ap.add_argument("--conta", required=True,
                    help="username da conta logada (session salvo via 'instaloader --login=USER')")
    ap.add_argument("--top", type=int, default=5, help="quantos videos baixar (default 5)")
    ap.add_argument("--scan", type=int, default=30,
                    help="quantos posts recentes escanear para rankear (default 30)")
    ap.add_argument("--por", choices=["views", "likes", "engajamento"], default="views",
                    help="criterio de ranking (default views)")
    ap.add_argument("--out", default=None,
                    help="pasta de saida (default: ./coleta-<perfil>)")
    ap.add_argument("--min-views", type=int, default=0,
                    help="ignora videos abaixo desse numero de views")
    args = ap.parse_args()

    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

    alvo = args.perfil.lstrip("@").strip()
    out = Path(args.out) if args.out else Path.cwd() / f"coleta-{alvo}"
    out.mkdir(parents=True, exist_ok=True)

    L = instaloader.Instaloader(
        dirname_pattern=str(out),
        filename_pattern="{shortcode}",
        download_video_thumbnails=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=False,
        post_metadata_txt_pattern="",
        compress_json=False,
        quiet=True,
    )

    # Carrega a sessao logada (conta laranja)
    try:
        L.load_session_from_file(args.conta)
        log(f"[ok] sessao carregada: {args.conta}")
    except FileNotFoundError:
        sys.exit(
            f"ERRO: nao achei a sessao da conta '{args.conta}'.\n"
            f"Faca login uma vez no terminal:  instaloader --login={args.conta}\n"
            f"(vai pedir a senha e salvar o session; o Claude nunca ve a senha)."
        )

    # Carrega o perfil-alvo
    try:
        profile = instaloader.Profile.from_username(L.context, alvo)
    except Exception as e:
        sys.exit(f"ERRO ao abrir o perfil @{alvo}: {e}")

    log(f"[ok] perfil @{alvo} — {profile.mediacount} posts, "
        f"{profile.followers} seguidores. Escaneando {args.scan} posts...")

    videos = []
    for post in itertools.islice(profile.get_posts(), args.scan):
        if not post.is_video:
            continue
        views = post.video_view_count or 0
        if not views:  # Instagram removeu video_view_count; tenta play_count no node cru
            try:
                node = getattr(post, "_node", {}) or {}
                views = node.get("play_count") or node.get("ig_play_count") or 0
            except Exception:
                views = 0
        if views < args.min_views:
            continue
        likes = post.likes or 0
        comments = post.comments or 0
        videos.append({
            "shortcode": post.shortcode,
            "url": f"https://www.instagram.com/reel/{post.shortcode}/",
            "data": post.date_utc.isoformat(),
            "views": views,
            "likes": likes,
            "comments": comments,
            "engajamento": likes + comments,
            "taxa_engaj": round((likes + comments) / views, 4) if views else None,
            "duracao_s": round(getattr(post, "video_duration", 0) or 0, 1),
            "legenda": post.caption or "",
            "_post": post,
        })

    if not videos:
        sys.exit(f"ERRO: nenhum video encontrado nos {args.scan} posts mais recentes de @{alvo}.")

    chave = {"views": "views", "likes": "likes", "engajamento": "engajamento"}[args.por]
    if chave == "views" and all(v["views"] == 0 for v in videos):
        log("[aviso] Instagram nao expos views nesta coleta; rankeando por LIKES.")
        chave = "likes"
    videos.sort(key=lambda v: v[chave], reverse=True)
    top = videos[:args.top]

    log(f"[ok] {len(videos)} videos encontrados. Baixando top {len(top)} por '{args.por}':")

    manifest = []
    for i, v in enumerate(top, 1):
        post = v.pop("_post")
        log(f"  {i}. {v['shortcode']}  {v['views']:>9,} views  "
            f"{v['likes']:>7,} likes  ({v['duracao_s']}s)")
        try:
            L.download_post(post, target=out.name if out.parent == Path.cwd() else str(out))
        except Exception as e:
            log(f"     [falha download] {e}")
            v["video_path"] = None
            v["erro"] = str(e)
            manifest.append(v)
            time.sleep(2)
            continue

        # localiza o .mp4 baixado (filename_pattern = shortcode)
        cand = list(out.glob(f"{v['shortcode']}*.mp4"))
        v["video_path"] = str(cand[0]) if cand else None

        # grava legenda em txt separado (util pra leitura)
        (out / f"{v['shortcode']}.legenda.txt").write_text(v["legenda"], encoding="utf-8")

        manifest.append(v)
        time.sleep(2)  # respiro anti-bloqueio

    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    log(f"[ok] concluido. Pasta: {out}")
    # stdout = JSON puro (o orquestrador le isto)
    print(json.dumps({"perfil": alvo, "pasta": str(out), "criterio": args.por,
                      "videos": manifest}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
