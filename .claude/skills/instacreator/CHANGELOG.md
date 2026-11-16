# Changelog

Todas as mudanças relevantes deste projeto são documentadas aqui.
O formato segue o [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e o projeto adota [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [1.0.0] - 2026-07-30

### Adicionado
- **Skill `instacreator`** (`SKILL.md`): orquestra coleta → frames/transcrição → análise, entregando
  relatório de estrutura (Parte A), roteiro modelado (Parte B) e comparação estratégica opcional (Parte C).
- **`scripts/coletar.py`**: descobre e baixa os top reels de um perfil via `instaloader` logado,
  com métricas (likes, comentários, engajamento) e legenda. Ranqueia por likes/engajamento e
  auto-cai pra likes quando o Instagram não expõe `views`. Saída em JSON + `manifest.json`.
- **`scripts/transcrever.py`**: transcrição local, grátis e offline via `faster-whisper` (fallback sem chave de API).
- **`scripts/sessao_de_json.py`**: cria a sessão do instaloader a partir de cookies exportados em JSON
  (Cookie-Editor) — contorna a criptografia de cookies do Chrome.
- **`scripts/sessao_de_cookies.py`**: idem, a partir de `cookies.txt` no formato Netscape.
- **`scripts/logar_cookies.py`**: tentativa de importar cookies direto do navegador (Chrome/Edge/Firefox/Brave/Opera)
  via `browser_cookie3` (pode falhar em Chrome com app-bound encryption; use os conversores acima).
- **`perfil-do-usuario.template.md`**: template de perfil estratégico que ativa a Parte C (comparação
  🟢 roubar / 🟡 adaptar / 🔴 ignorar) quando copiado para `perfil-do-usuario.md`.
- **README** com instalação, conexão de conta (login e cookies), uso e aviso de Termos de Uso.
- Integração com a skill [`watch`](https://github.com/bradautomates/claude-video) para extração de
  frames scene-aware e transcrição.

### Notas
- O Instagram removeu `video_view_count` de boa parte das respostas de API; o ranking usa likes+comentários.
- Suporte a Windows (`python`) e macOS/Linux (`python3`).

[1.0.0]: https://github.com/equinho/instacreator/releases/tag/v1.0.0
