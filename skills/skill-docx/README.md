# skill-docx — Quickstart

Skill que gera documentos Word .docx com a identidade visual da marca central
(definida em `/opt/MAIA/brand/brand.json` via `brand_loader`) a partir de markdown.

## Uso rapido

```bash
/opt/MAIA/bot/venv/bin/python \
  /opt/MAIA/.claude/skills/skill-docx/scripts/render_docx.py \
  --input /caminho/origem.md \
  --output /caminho/saida.docx
```

Vai detectar titulo/subtitulo automaticamente do primeiro H1 e do paragrafo seguinte.
Marca, autor, site e contato vem do `brand_loader` (use `--brand/--author/--site/--email`
apenas para sobrescrever pontualmente).

## Identidade aplicada

- Capa estilizada com o nome da marca (`brand_name()` do brand_loader)
- Sumario automatico (campo TOC do Word)
- Header com a marca + linha teal
- Footer com email/site + numero de pagina (campos vazios sao omitidos)
- Paleta default: preto #0a0a0a, teal #3A9E9C, dourado #c9a96e, off-white #f5f3ee
  (pode ser sobrescrita por `colors()` do brand_loader)
- Fontes: Playfair Display (display), Plus Jakarta Sans (body), JetBrains Mono (code)

## Dependencias

- python-docx (instalado em /opt/MAIA/bot/venv)
- Fontes em /opt/MAIA/assets/fonts/{playfair_display,plus_jakarta,jetbrains_mono,inter}

## Documentacao completa

Ver SKILL.md neste mesmo diretorio.
