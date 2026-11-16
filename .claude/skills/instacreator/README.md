# 📸 instacreator

> Engenharia reversa de conteúdo do Instagram — pra criador que quer modelar o que já está bombando.

`instacreator` é uma [skill](https://skills.sh) que faz o trabalho braçal de pesquisa de referência:
entra num perfil, descobre os reels que mais performam, **disseca a estrutura** de cada um
(frames + transcrição + legenda) e te entrega **um relatório do que faz aquilo bombar + um roteiro
modelado pronto pra gravar** — adaptado ao seu nicho, sem copiar.

E o pulo do gato: se você preencher seu **perfil estratégico**, ela ainda compara a estratégia do
perfil-alvo contra a sua e te diz o que **🟢 roubar / 🟡 adaptar / 🔴 ignorar**.

```
@perfil  →  coletar (instaloader logado)  →  top reels + legenda + métricas
         →  watch (frames scene-aware)    →  transcrição (Whisper local, grátis)
         →  análise                        →  📄 relatório + 🎬 roteiro (+ 🎯 comparação)
```

---

## ✨ O que ela entrega

- **Parte A — Relatório de estrutura:** hook (0-3s), ritmo/cortes, texto na tela, desenvolvimento, CTA e a *fórmula da legenda* de cada top vídeo, + os padrões em comum do perfil.
- **Parte B — Roteiro modelado:** tema, hook com fala exata, roteiro por blocos com tempo, CTA, legenda pronta e notas de gravação — modelado **em cima** da estrutura vencedora, adaptado ao seu nicho.
- **Parte C — Comparação (opcional):** com seu `perfil-do-usuario.md` preenchido, os 3 baldes 🟢🟡🔴.

## 🧰 Como funciona (stack)

| Peça | Papel |
|---|---|
| [`instaloader`](https://instaloader.github.io/) | descobre e baixa os top reels + legenda + métricas (logado na SUA conta) |
| [`watch`](https://github.com/bradautomates/claude-video) | vídeo local → frames scene-aware (+ transcrição via Whisper API opcional) |
| [`faster-whisper`](https://github.com/SYSTRAN/faster-whisper) | transcrição **local, grátis, offline** (fallback sem chave) |
| `yt-dlp` + `ffmpeg` | download e processamento de mídia |

## 📦 Instalação

```bash
# 1) a skill
npx skills add https://github.com/equinho/instacreator --skill instacreator

# 2) a skill watch (frames + transcrição)
npx skills add https://github.com/bradautomates/claude-video --skill watch

# 3) dependências Python
pip install instaloader faster-whisper browser_cookie3

# 4) binários (precisam estar no PATH)
#    - ffmpeg:  https://ffmpeg.org/download.html
#    - yt-dlp:  pip install yt-dlp   (ou binário oficial)
```

> **Windows:** use `python`; **macOS/Linux:** use `python3`.

## 🔑 Conectando sua conta

A coleta precisa de uma sessão logada do Instagram. **Use uma conta secundária** — automação pode
gerar bloqueio temporário. Duas formas:

### Opção 1 — Login normal
```bash
python -m instaloader --login=SEU_USUARIO
```
Se cair em **"Checkpoint required"**, aprove no navegador e tente de novo. Se ficar em loop, use a Opção 2.

### Opção 2 — Cookies do navegador (recomendado, contorna o checkpoint)
O Chrome moderno criptografa os cookies (app-bound encryption), então a leitura automática falha.
Exporte manualmente:

1. Instale a extensão **Cookie-Editor** (ou "Get cookies.txt LOCALLY") — open-source, roda local.
2. Abra `instagram.com` logado → exporte os cookies.
3. Converta em sessão:
   ```bash
   # JSON (Cookie-Editor):
   python scripts/sessao_de_json.py cookies.json --usuario SEU_USUARIO
   # ou Netscape (Get cookies.txt LOCALLY):
   python scripts/sessao_de_cookies.py cookies.txt --usuario SEU_USUARIO
   ```

A sessão fica salva em `%LOCALAPPDATA%\Instaloader\` (Windows) ou `~/.config/instaloader/` (Linux/Mac).
**Nenhum cookie ou senha é enviado pra lugar nenhum** — tudo local.

## 🚀 Uso

No seu agente (Claude Code, etc.):
```
/instacreator @perfil_alvo --top 5 --por likes
```

Ou os scripts direto:
```bash
# coleta os 5 mais curtidos dos últimos 50 posts
python scripts/coletar.py "@perfil_alvo" --conta SEU_USUARIO --top 5 --scan 50 --por likes --out ./coleta

# transcrição local de um vídeo
python scripts/transcrever.py ./coleta/XXXX.mp4 --idioma pt --modelo small
```

## 🎯 Ativando a comparação com a sua estratégia (Parte C)

Copie o template e preencha com o SEU jogo:
```bash
cp perfil-do-usuario.template.md perfil-do-usuario.md
```
Preencha posicionamento, fluxos de receita, audiências, mix editorial e fronteiras de marca.
A partir daí, toda análise ganha a Parte C filtrada pela sua estratégia. Esse arquivo é **pessoal**
e já está no `.gitignore` — não vai pro repositório.

## ⚠️ Aviso

Ferramenta de **pesquisa de referência** sobre conteúdo público. Modelar estrutura é ok; **copiar/plagiar
conteúdo não**. Automatizar o Instagram pode violar os Termos de Uso da plataforma — você é responsável
pelo uso da sua própria conta. Prefira conta secundária e respeite os limites de requisição.

## 📄 Licença

MIT — veja [LICENSE](LICENSE).
