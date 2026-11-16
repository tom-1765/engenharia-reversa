#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sessao_de_cookies.py — Converte um cookies.txt (formato Netscape, exportado do
navegador) numa sessao valida do instaloader. Contorna a criptografia do Chrome
(app-bound encryption) que impede a leitura automatica dos cookies.

Como exportar o cookies.txt:
  1. Instale a extensao "Get cookies.txt LOCALLY" no Chrome (open-source, roda local).
  2. Abra instagram.com (logado), clique na extensao, "Export" -> salva cookies.txt.

Uso:
    python sessao_de_cookies.py <caminho_cookies.txt> [--usuario seu_usuario]

Salva a sessao em %LOCALAPPDATA%\\Instaloader\\session-<usuario>.
"""
import argparse
import sys
from http.cookiejar import MozillaCookieJar
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cookies", help="caminho do cookies.txt exportado do navegador")
    ap.add_argument("--usuario", default=None,
                    help="username esperado (opcional; detectado pelo login)")
    args = ap.parse_args()

    p = Path(args.cookies)
    if not p.exists():
        sys.exit(f"ERRO: cookies.txt nao encontrado: {p}")

    try:
        import instaloader
    except ImportError:
        sys.exit("ERRO: instaloader nao instalado.")

    cj = MozillaCookieJar()
    try:
        cj.load(str(p), ignore_discard=True, ignore_expires=True)
    except Exception as e:
        sys.exit(f"ERRO ao ler o cookies.txt: {e}\n"
                 f"Confirme que e o formato Netscape (extensao 'Get cookies.txt LOCALLY').")

    ig = [c for c in cj if "instagram.com" in (c.domain or "")]
    if not ig:
        sys.exit("ERRO: nenhum cookie de instagram.com no arquivo. "
                 "Exporte estando logado em instagram.com.")

    L = instaloader.Instaloader(quiet=True)
    for c in ig:
        L.context._session.cookies.set(c.name, c.value, domain=c.domain, path=c.path or "/")

    print(f"[ok] {len(ig)} cookies do Instagram carregados. Testando login...", file=sys.stderr)
    quem = L.test_login()
    if not quem:
        sys.exit("ERRO: cookies nao autenticam (sessao expirada?). "
                 "Refaca o login no navegador e exporte de novo.")

    if args.usuario and quem.lower() != args.usuario.lower():
        print(f"[aviso] logado como '{quem}', nao '{args.usuario}'.", file=sys.stderr)

    L.context.username = quem
    L.save_session_to_file()
    print(f"[ok] sessao salva para '{quem}'. Use:  coletar.py <@perfil> --conta {quem}")


if __name__ == "__main__":
    main()
