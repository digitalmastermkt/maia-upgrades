---
name: skill-docx
description: "Gera documentos Word .docx configurados com a identidade visual da marca central (paleta teal/dourado default, fontes Plus Jakarta + Playfair, header com nome da marca, footer com contato/site, capa estilizada, sumario automatico). Marca, nome, autor e site vem de /opt/MAIA/brand/brand.json via brand_loader. Recebe markdown como input. Use quando o usuario pedir 'entrega em docx', 'gera em Word', 'formata esse documento', 'faz versao Word'."
triggers:
  - "entrega em docx"
  - "gera em word"
  - "gera em docx"
  - "formata em docx"
  - "faz versao word"
  - "versao word"
  - "documento em word"
  - "transforma em docx"
  - "exporta em docx"
  - "/docx"
  - "skill-docx"
---

# skill-docx — Documentos Word configurados

## IDENTITY

Voce e a fabrica de DOCX da marca. Cada arquivo .docx que sai daqui carrega a
identidade visual configurada no sistema central (`/opt/MAIA/brand/brand.json`
via `brand_loader`): capa estilizada, sumario automatico, header com o nome da
marca, footer com contato/site, paleta teal e dourado sobre off-white,
tipografia Plus Jakarta + Playfair Display.

A marca, o nome do autor, o site e o handle nunca ficam hardcoded: o motor
(`build_docx.py`) puxa `brand_name()`, `owner_name()`, `website_or_blank()` etc.
do `brand_loader`. Se algum valor estiver vazio, o documento simplesmente omite
aquele trecho.

Documento Word entregue por essa skill nao e markdown convertido por Pandoc cru
— e um arquivo Word configurado, com estilos definidos via XML python-docx,
pronto pra ser aberto no Word/LibreOffice/Google Docs e ja parecer entrega
profissional.

## QUANDO USAR

Use sempre que o usuario pedir:

- "gera em docx"
- "entrega em Word"
- "faz versao Word desse markdown"
- "formata em docx"
- "transforma esse MD em Word"

E sempre que voce for entregar um arquivo `.md` que o usuario vai abrir no Word
ou enviar pra um cliente — entrega DUAS versoes: o `.md` cru pra editar e o
`.docx` configurado pra apresentar.

## QUANDO NAO USAR

- Pagina HTML: use a skill de pagina de vendas
- Carrossel Instagram: use a skill de cards de Q&A
- PDF: gere o .docx com essa skill e converta com `libreoffice --convert-to pdf`
  ou solicite conversao em outro passo

## INPUT

Recebe um arquivo markdown (.md) com sintaxe padrao:

- `# H1 ... ## H2 ... ### H3 ... #### H4`
- Paragrafos
- Listas `- item` e `1. item`
- Blockquotes `> citacao`
- Code blocks com triple backtick
- Tabelas pipe `| col | col |`
- Horizontal rule `---`
- Inline `**bold**`, `*italic*`, `` `code` ``

Auto-detecta titulo e subtitulo do MD:
- Primeiro `# H1` vira o titulo da capa
- Primeiro paragrafo apos esse H1 vira o subtitulo (se for curto)

## OUTPUT

Arquivo .docx com:

**Pagina 1 — CAPA:** nome da marca (brand_name), titulo Playfair italic dourado 36pt, subtitulo teal, autor (owner_name) + data.

**Pagina 2 — SUMARIO:** campo TOC do Word (auto-atualiza ao abrir).

**Paginas 3+ — CONTEUDO:**
- Header: "[Marca]  -  [Titulo]" em teal + linha teal
- Footer: "email  -  site  -  Pagina X" em cinza (campos vazios sao omitidos)
- H1: Playfair 22pt dourado bold; H2: Plus Jakarta 16pt teal; H3/H4: Plus Jakarta preto
- Body: Plus Jakarta 11pt preto justificado, line-height 1.5
- Bullets: simbolo dourado + texto preto
- Tabelas: header teal + branco bold, zebra rows off-white
- Quotes: borda esquerda dourada + fundo off-white + italic
- Code: JetBrains Mono 10pt fundo cinza claro

## COMO RODAR

CLI:

```bash
/opt/MAIA/bot/venv/bin/python \
  /opt/MAIA/.claude/skills/skill-docx/scripts/render_docx.py \
  --input /caminho/origem.md \
  --output /caminho/saida.docx \
  --title "Titulo Opcional" \
  --subtitle "Subtitulo Opcional"
```

Sem `--author/--brand/--email/--site` a skill puxa os valores da marca central
(`brand_loader`). Passe os flags so para sobrescrever pontualmente.

API Python:

```python
import sys
sys.path.insert(0, "/opt/MAIA/.claude/skills/skill-docx/scripts")
from build_docx import DocxBuilder

# autor, marca, site e contato vem do brand_loader se nao forem passados
b = DocxBuilder(title="Estrategia Q3", subtitle="Roadmap")
b.add_heading(1, "Diagnostico")
b.add_paragraph("O cenario atual...")
b.add_bullet("Foco em LTV")
b.add_quote("Texto de destaque.")
b.save("/tmp/saida.docx")
```

## ENTREGAS

| Caso | Destino | Retencao |
|------|---------|----------|
| Documento descartavel | MinIO briefs/ | infinita |
| Pacote bonus / brief | MinIO briefs/ | infinita |

URL MinIO: `http://SEU_IP_OU_HOST:9001/browser/seu-bucket/briefs%2F<categoria>%2F`

## REGRAS CRITICAS

- NUNCA usar Pandoc puro pra DOCX da marca - resultado fica sem identidade
- SEMPRE manter o .md ao lado do .docx
- Marca/autor/site vem do `brand_loader` — nao hardcode esses valores nos scripts
- Sumario vazio ao abrir: clicar direito > "Atualizar campo"
- Imagens inline ignoradas - se precisar, embute manual via `b.doc.add_picture()`

## MANUTENCAO

- `SKILL.md` - especificacao + triggers
- `README.md` - quickstart
- `scripts/render_docx.py` - CLI orquestrador
- `scripts/build_docx.py` - motor python-docx
- `assets/` - reservado pra logo PNG futuro
- `templates/` - reservado pra reference-doc opcional

Dependencia: `python-docx` (em `/opt/MAIA/bot/venv`)

Fontes em `/opt/MAIA/assets/fonts/`: playfair_display, plus_jakarta, jetbrains_mono, inter

## CHANGELOG

- 2026-05-08: skill criada. MD->DOCX com capa, TOC, header, footer, paleta teal/dourado.
- 2026-06-18: parametrizada para a marca central (brand_loader) — marca/autor/site/contato deixaram de ser hardcoded.
