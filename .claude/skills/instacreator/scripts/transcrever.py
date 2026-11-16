#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
transcrever.py — Transcricao LOCAL (gratis, offline, sem chave) via faster-whisper.
Fallback para quando nao houver chave Groq/OpenAI configurada na skill `watch`.

Uso:
    python transcrever.py <video_ou_audio> [--modelo small] [--idioma pt]

Imprime a transcricao com timestamps no stdout.
"""
import argparse
import sys
from pathlib import Path


def fmt(t):
    m, s = divmod(int(t), 60)
    return f"{m:02d}:{s:02d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("arquivo", help="caminho do video/audio")
    ap.add_argument("--modelo", default="small",
                    help="tiny|base|small|medium|large-v3 (default small)")
    ap.add_argument("--idioma", default="pt", help="codigo do idioma (default pt)")
    args = ap.parse_args()

    if not Path(args.arquivo).exists():
        sys.exit(f"ERRO: arquivo nao encontrado: {args.arquivo}")

    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("ERRO: faster-whisper nao instalado. Rode:  pip install faster-whisper")

    print(f"[carregando modelo {args.modelo} (CPU/int8)...]", file=sys.stderr, flush=True)
    model = WhisperModel(args.modelo, device="cpu", compute_type="int8")

    segments, info = model.transcribe(args.arquivo, language=args.idioma, vad_filter=True)
    print(f"[idioma detectado: {info.language} p={info.language_probability:.2f}]",
          file=sys.stderr, flush=True)

    linhas = []
    for seg in segments:
        linhas.append(f"[{fmt(seg.start)}] {seg.text.strip()}")

    print("\n".join(linhas))


if __name__ == "__main__":
    main()
