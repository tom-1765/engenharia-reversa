#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sessao_de_json.py — Cria a sessao do instaloader a partir de cookies exportados
em JSON (formato Cookie-Editor / EditThisCookie). Contorna a criptografia do Chrome.

Uso:
    python sessao_de_json.py <cookies.json> [--usuario seu_usuario]
"""
import argparse
import json
import sys
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cookies", help="caminho do JSON de cookies")
    ap.add_argument("--usuario", default=None)
    args = ap.parse_args()

    p = Path(args.cookies)
    if not p.exists():
        sys.exit(f"ERRO: arquivo nao encontrado: {p}")

    data = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "cookies" in data:
        data = data["cookies"]
    ig = [c for c in data if "instagram.com" in (c.get("domain", ""))]
    if not any(c.get("name") == "sessionid" for c in ig):
        sys.exit("ERRO: nao ha 'sessionid' nos cookies. Exporte estando logado em instagram.com.")

    import instaloader
    L = instaloader.Instaloader(quiet=True)
    for c in ig:
        L.context._session.cookies.set(
            c["name"], c["value"],
            domain=c.get("domain", ".instagram.com"),
            path=c.get("path", "/"),
        )

    print(f"[ok] {len(ig)} cookies carregados. Testando login...", file=sys.stderr)
    quem = L.test_login()
    if not quem:
        sys.exit("ERRO: cookies nao autenticam (sessao expirada?). Refaca e exporte de novo.")

    if args.usuario and quem.lower() != args.usuario.lower():
        print(f"[aviso] logado como '{quem}', nao '{args.usuario}'.", file=sys.stderr)

    L.context.username = quem
    L.save_session_to_file()
    print(f"[ok] sessao salva para '{quem}'. Use:  coletar.py <@perfil> --conta {quem}")


if __name__ == "__main__":
    main()
