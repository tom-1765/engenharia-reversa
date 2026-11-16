#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
logar_cookies.py — Cria a sessao do instaloader importando os cookies do navegador
onde voce JA esta logado no Instagram. Contorna o "Checkpoint required" e nao
pede senha (a senha nunca passa por aqui).

Uso:
    python logar_cookies.py <usuario> [--navegador chrome|firefox|edge|auto]

Ex.:
    python logar_cookies.py seu_usuario --navegador chrome
"""
import argparse
import sys


def carregar_cookies(nav):
    import browser_cookie3 as bc
    ordem = [nav] if nav != "auto" else ["chrome", "edge", "firefox", "brave", "opera"]
    erros = []
    for n in ordem:
        try:
            fn = getattr(bc, n, None)
            if fn is None:
                continue
            cj = fn(domain_name="instagram.com")
            if len(cj):
                print(f"[ok] cookies do {n}: {len(cj)} encontrados", file=sys.stderr)
                return cj, n
            erros.append(f"{n}: 0 cookies")
        except Exception as e:
            erros.append(f"{n}: {e}")
    raise SystemExit("ERRO: nao consegui ler cookies do Instagram de nenhum navegador.\n  "
                     + "\n  ".join(erros)
                     + "\nAbra o Instagram e logue no navegador, depois tente de novo.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("usuario", help="username da conta logada no navegador")
    ap.add_argument("--navegador", default="auto",
                    choices=["auto", "chrome", "firefox", "edge", "brave", "opera"])
    args = ap.parse_args()

    try:
        import instaloader
    except ImportError:
        sys.exit("ERRO: instaloader nao instalado.")

    cj, nav = carregar_cookies(args.navegador)

    L = instaloader.Instaloader(quiet=True)
    L.context._session.cookies.update(cj)

    quem = L.test_login()
    if not quem:
        sys.exit(f"ERRO: os cookies do {nav} nao estao autenticados no Instagram.\n"
                 f"Confirme que voce esta logado no Instagram nesse navegador e tente de novo.")

    if quem.lower() != args.usuario.lower():
        print(f"[aviso] cookies logados como '{quem}', nao '{args.usuario}'. "
              f"Salvando a sessao de '{quem}'.", file=sys.stderr)

    L.context.username = quem
    L.save_session_to_file()  # salva em %LOCALAPPDATA%\Instaloader\session-<quem>
    print(f"[ok] sessao salva para '{quem}'. Pronto pra usar em coletar.py --conta {quem}")


if __name__ == "__main__":
    main()
