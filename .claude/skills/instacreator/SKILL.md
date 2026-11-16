---
name: instacreator
version: "1.0.0"
description: Engenharia reversa de conteudo do Instagram. Descobre os reels de melhor desempenho de um perfil (via instaloader logado na SUA conta), extrai frames + transcricao + legenda de cada um (via skill watch), decodifica a ESTRUTURA que faz o video bombar e entrega um relatorio + um roteiro modelado pronto pra gravar. Se voce preencher seu perfil estrategico, ainda compara a estrategia do perfil-alvo contra a sua.
argument-hint: "<@perfil> [--top N] [--por likes|engajamento]"
allowed-tools: Bash, Read, AskUserQuestion, Write
homepage: https://github.com/equinho/instacreator
repository: https://github.com/equinho/instacreator
license: MIT
user-invocable: true
---

# /instacreator

Faz o trabalho de pesquisa de referencia: entra num perfil, acha o que esta
bombando, disseca a estrutura (frames + transcricao + legenda) e entrega
**(1) um relatorio de estrutura** e **(2) um roteiro modelado** pronto pra gravar.
Se existir um `perfil-do-usuario.md` preenchido, entrega tambem **(3) uma comparacao**
entre a estrategia do perfil-alvo e a sua.

Divisao de trabalho:
- `scripts/coletar.py` — instaloader (SUA conta logada) descobre e baixa os top reels + legenda + metricas.
- skill **watch** — cada video local -> frames (scene-aware) + transcricao.
- `scripts/transcrever.py` — transcricao local (faster-whisper) como fallback sem chave.
- **voce (o modelo)** — le frames + transcricao + legenda e produz relatorio + roteiro (+ comparacao).

## Pre-requisitos (instale uma vez)

- **Python 3.10+**, com: `pip install instaloader faster-whisper browser_cookie3`
- **yt-dlp** e **ffmpeg** no PATH.
- **skill watch** (extrai frames+transcricao): `npx skills add https://github.com/bradautomates/claude-video --skill watch`

## Resolva os caminhos (faca antes de tudo)

- `SKILL_DIR` = pasta absoluta que contem ESTE SKILL.md (o harness te deu no Read).
- `WATCH` = script da skill watch. Descubra com:
  ```bash
  ls ~/.agents/skills/watch/scripts/watch.py 2>/dev/null || \
  ls ~/.claude/plugins/cache/claude-video/*/skills/watch/scripts/watch.py 2>/dev/null
  ```
- **Interpretador Python:** no **Windows** use `python`; no macOS/Linux use `python3`.

## Passo 0 — Preflight (silencioso se tudo ok)

```bash
python -c "import instaloader, faster_whisper; print('deps ok')"
yt-dlp --version >/dev/null && ffmpeg -version >/dev/null && echo "bins ok"
```
Faltando algo -> instale conforme "Pre-requisitos".

**Sessao do Instagram.** A coleta exige uma sessao logada. Verifique:
```bash
ls "$LOCALAPPDATA/Instaloader/session-"* 2>/dev/null || ls ~/.config/instaloader/session-* 2>/dev/null
```
Se nao existir, o usuario precisa conectar a conta dele UMA vez. Ofereca as opcoes
(ver README, secao "Conectando sua conta"):
1. **Login normal:** `python -m instaloader --login=SEU_USUARIO` (pode cair em checkpoint).
2. **Cookies (recomendado, contorna checkpoint):** exportar cookies do navegador logado e rodar
   `python "${SKILL_DIR}/scripts/sessao_de_json.py" cookies.json` (JSON do Cookie-Editor) ou
   `python "${SKILL_DIR}/scripts/sessao_de_cookies.py" cookies.txt` (Netscape).

> ⚠️ Recomende uma **conta secundaria**: automacao pode gerar bloqueio temporario na conta.
> Guarde o `--conta` (username logado) para os comandos abaixo.

## Passo 1 — Coletar os top videos

```bash
python "${SKILL_DIR}/scripts/coletar.py" "<@perfil>" --conta <USUARIO> \
    --top <N> --scan 50 --por <criterio> --out "<pasta_saida>"
```
- Default: `--top 5 --scan 50 --por likes`. O Instagram parou de expor `views` na API;
  o script auto-cai pra **likes** quando views vem zerado. Prefira `--por likes` ou `engajamento`.
- O stdout e um JSON com `{perfil, pasta, criterio, videos:[{shortcode,url,likes,comments,engajamento,legenda,video_path}]}`.
- Mostre ao usuario a tabela rankeada antes de processar.

## Passo 2 — Frames + transcricao de cada video

Para CADA `video_path`, aponte a skill watch pro arquivo LOCAL (assim ela nao rebaixa do IG):
```bash
python "${WATCH}" "<video_path>" --detail efficient --no-whisper --max-frames 12 --out-dir "<pasta>/w_<shortcode>"
```
- `--no-whisper` = frames sem depender de chave. Transcricao via Whisper local:
  ```bash
  python "${SKILL_DIR}/scripts/transcrever.py" "<video_path>" --idioma pt --modelo small
  ```
- **Upgrade opcional:** se houver chave Groq gratis em `~/.config/watch/.env`, rode watch SEM
  `--no-whisper` e ele devolve frames + transcricao juntos.
- Depois, **Read** os caminhos de frame que o watch listou (em paralelo). Alinhe pelos timestamps `t=MM:SS`.
- Economia de token: ~10-15 frames por video costuma bastar; a transcricao carrega a estrutura.

## Passo 3 — Decodificar e entregar

**Se existir `${SKILL_DIR}/perfil-do-usuario.md`, LEIA antes de escrever** — e a estrategia
do usuario e filtra toda a analise. Se nao existir, pule a Parte C.

Cruze frames + transcricao + legenda. Produza:

### Parte A — Relatorio de estrutura (por video)
Ficha (url, likes, comentarios, duracao) + **Hook (0-3s)** + **retencao/ritmo** (cortes, texto na tela)
+ **desenvolvimento** + **CTA/fechamento** + **formula da legenda** + **padrao replicavel em 1 frase**.
Ao cobrir varios videos, feche com **padroes em comum** do perfil.

### Parte B — Roteiro modelado (pronto pra gravar)
Modele EM CIMA da estrutura vencedora, **sem copiar** o conteudo — adapte ao nicho do usuario
(pergunte se nao souber). Entregue: tema, **hook (0-3s)** com fala exata + visual, roteiro por blocos
com tempo, CTA, **legenda pronta** (gancho + hashtags) e notas de gravacao/edicao.
Se houver `perfil-do-usuario.md`, respeite o posicionamento, o mix e as fronteiras dele.

### Parte C — Comparacao com a estrategia do usuario *(so se `perfil-do-usuario.md` existir)*
Cruze o perfil-alvo contra as dimensoes da secao "COMO USAR ISTO PARA COMPARAR PERFIS" do doc.
Entregue sempre os **3 baldes**:
- 🟢 **ROUBAR** — encaixa direto (dizer qual audiencia / qual fatia do mix).
- 🟡 **ADAPTAR** — funciona, mas traduzir pro nicho do usuario (dizer *como*).
- 🔴 **IGNORAR** — bomba pro alvo mas conflita com a marca do usuario (dizer *por que*).

Grave o resultado num `.md` (Write) na pasta de saida e mostre um resumo no chat.

## Passo 4 — Limpeza
As pastas `w_<shortcode>` (frames/audio) sao temporarias; ofereca apagar. Videos e manifest ficam.

## Etica e limites
- Use **conta secundaria**; a principal pode levar bloqueio por automacao.
- Analise de referencia sobre conteudo publico — modelar estrutura e ok, **copiar/plagiar nao**.
  A Parte B sempre ADAPTA ao nicho do usuario.
- Respeite rate-limit (pausas ja embutidas). Automatizar o Instagram pode violar os Termos de Uso
  da plataforma; o usuario e responsavel pelo uso da propria conta.
