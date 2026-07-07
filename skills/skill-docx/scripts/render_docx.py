#!/usr/bin/env python3
"""
render_docx.py - Orquestrador CLI da skill-docx.

Parseia um arquivo markdown e gera um .docx configurado com a identidade visual
da marca definida no sistema central (/opt/MAIA/brand/brand.json via
brand_loader): paleta teal/dourado default, capa estilizada, sumario automatico,
header/footer com nome/site/handle da marca.

Uso:
    python3 render_docx.py \
        --input /path/to/input.md \
        --output /path/to/output.docx \
        --title "Titulo do Documento" \
        --subtitle "Subtitulo opcional" \
        [--author "Nome do Autor"] \
        [--date "08/05/2026"]

    Sem --author/--brand/--email/--site a skill puxa os valores da marca
    central (brand_loader). Passe os flags so para sobrescrever pontualmente.

Notas de parser:
    - Extrai title/subtitle automaticamente do MD se presente:
        primeiro H1 vira title (se --title nao foi passado)
        primeiro paragrafo bold/italico apos o H1 vira subtitle (se --subtitle vazio)
    - Suporta: H1-H4, paragrafo, listas (- ou *), listas numeradas (1.),
      blockquotes (>), code fences (```), tabelas pipe (| a | b |), horizontal
      rule (---), inline **bold**, *italic*, `code`.
    - Imagens (![alt](url)) sao ignoradas (DOCX inline embutido fica fora do
      escopo desta versao - facil de adicionar depois).
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import datetime

# Garantir que o build_docx.py do mesmo diretorio seja importavel
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

# Tentar importar python-docx via venv da MAIA se disponivel
VENV_SP = "/opt/MAIA/bot/venv/lib/python3.12/site-packages"
if os.path.isdir(VENV_SP) and VENV_SP not in sys.path:
    sys.path.insert(0, VENV_SP)

from build_docx import DocxBuilder  # noqa: E402


# ============================================================================
# Markdown parser - simples mas funcional
# ============================================================================
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")
TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$")


def parse_markdown(text):
    """Retorna lista de blocos: dicts {type: ..., ...}."""
    lines = text.splitlines()
    blocks = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            i += 1
            continue

        # Code fence
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            i += 1
            code_lines = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < n:
                i += 1  # consome o ``` final
            blocks.append({"type": "code", "lang": lang, "content": "\n".join(code_lines)})
            continue

        # Horizontal rule
        if stripped in ("---", "***", "___") or re.match(r"^-{3,}$", stripped):
            blocks.append({"type": "hr"})
            i += 1
            continue

        # Headings ATX
        m = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", stripped)
        if m:
            level = len(m.group(1))
            blocks.append({"type": "heading", "level": min(level, 4), "text": m.group(2).strip()})
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            quote_lines = []
            while i < n and lines[i].lstrip().startswith(">"):
                quote_lines.append(lines[i].lstrip().lstrip(">").strip())
                i += 1
            blocks.append({"type": "quote", "text": " ".join(quote_lines).strip()})
            continue

        # Tabela pipe (precisa de linha de separacao na 2a)
        if TABLE_ROW_RE.match(line) and i + 1 < n and TABLE_SEP_RE.match(lines[i + 1]):
            header = _split_table_row(line)
            i += 2  # pula header e separador
            rows = []
            while i < n and TABLE_ROW_RE.match(lines[i]):
                rows.append(_split_table_row(lines[i]))
                i += 1
            blocks.append({"type": "table", "headers": header, "rows": rows})
            continue

        # Lista nao ordenada
        m_ul = re.match(r"^(\s*)[-*+]\s+(.+)$", line)
        if m_ul:
            items = []
            while i < n:
                m2 = re.match(r"^(\s*)[-*+]\s+(.+)$", lines[i])
                if not m2:
                    # checa se eh continuacao indentada
                    if (
                        items
                        and lines[i].strip()
                        and lines[i].startswith(" ")
                        and not re.match(r"^\s*\d+\.\s", lines[i])
                    ):
                        items[-1]["text"] += " " + lines[i].strip()
                        i += 1
                        continue
                    break
                indent = len(m2.group(1))
                level = indent // 2
                items.append({"level": level, "text": m2.group(2).strip()})
                i += 1
            blocks.append({"type": "ul", "items": items})
            continue

        # Lista ordenada
        m_ol = re.match(r"^(\s*)(\d+)\.\s+(.+)$", line)
        if m_ol:
            items = []
            while i < n:
                m2 = re.match(r"^(\s*)(\d+)\.\s+(.+)$", lines[i])
                if not m2:
                    if (
                        items
                        and lines[i].strip()
                        and lines[i].startswith(" ")
                        and not re.match(r"^\s*[-*+]\s", lines[i])
                    ):
                        items[-1]["text"] += " " + lines[i].strip()
                        i += 1
                        continue
                    break
                items.append({"number": int(m2.group(2)), "text": m2.group(3).strip()})
                i += 1
            blocks.append({"type": "ol", "items": items})
            continue

        # Paragrafo (junta linhas ate vazio ou bloco especial)
        para_lines = [stripped]
        i += 1
        while i < n:
            nxt = lines[i]
            if not nxt.strip():
                break
            if re.match(r"^#{1,6}\s", nxt.strip()):
                break
            if nxt.strip().startswith("```"):
                break
            if nxt.strip().startswith(">"):
                break
            if re.match(r"^(\s*)[-*+]\s+", nxt):
                break
            if re.match(r"^(\s*)\d+\.\s+", nxt):
                break
            if TABLE_ROW_RE.match(nxt):
                break
            if nxt.strip() in ("---", "***", "___"):
                break
            para_lines.append(nxt.strip())
            i += 1
        blocks.append({"type": "paragraph", "text": " ".join(para_lines)})

    return blocks


def _split_table_row(line):
    """Splita uma linha de tabela pipe em celulas."""
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


# ============================================================================
# Render
# ============================================================================
def extract_title_subtitle(blocks):
    """Detecta title e subtitle no inicio do MD se nao foram passados.

    Heuristica:
        - primeiro heading H1 -> title
        - primeiro paragraph apos esse H1 que parece ser subtitulo
          (linha curta com bold/italic ou frase descritiva) -> subtitle
        - REMOVE esses blocos do array original
    """
    title = None
    subtitle = None

    if not blocks:
        return title, subtitle

    if blocks[0]["type"] == "heading" and blocks[0]["level"] == 1:
        title = blocks[0]["text"].strip()
        consumed = 1
        # se proximo bloco for paragrafo "subtitulo" curto (<200 chars + bold/italic ou frase) usa
        if len(blocks) > 1 and blocks[1]["type"] == "paragraph":
            txt = blocks[1]["text"].strip()
            if len(txt) < 240:
                # remove asteriscos do subtitulo se vier todo bold/italico
                cleaned = re.sub(r"\*+", "", txt).strip()
                subtitle = cleaned
                consumed = 2
        del blocks[:consumed]

    return title, subtitle


def render_blocks_to_docx(builder, blocks):
    for blk in blocks:
        t = blk["type"]
        if t == "heading":
            builder.add_heading(blk["level"], blk["text"])
        elif t == "paragraph":
            builder.add_paragraph(blk["text"])
        elif t == "ul":
            for item in blk["items"]:
                builder.add_bullet(item["text"], level=item.get("level", 0))
        elif t == "ol":
            for item in blk["items"]:
                builder.add_numbered(item["text"], item["number"])
        elif t == "quote":
            builder.add_quote(blk["text"])
        elif t == "code":
            builder.add_code_block(blk["content"], blk.get("lang", ""))
        elif t == "table":
            builder.add_table(blk["headers"], blk["rows"])
        elif t == "hr":
            builder.add_horizontal_rule()


# ============================================================================
# CLI
# ============================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Gera DOCX configurado com a identidade visual da marca central (brand_loader)"
    )
    parser.add_argument("--input", "-i", required=True, help="Caminho do .md de entrada")
    parser.add_argument("--output", "-o", required=True, help="Caminho do .docx de saida")
    parser.add_argument("--title", default=None, help="Titulo do documento (auto-detecta H1 do MD se omitido)")
    parser.add_argument("--subtitle", default=None, help="Subtitulo (auto-detecta paragrafo apos H1)")
    parser.add_argument("--author", default=None, help="Autor (default: owner_name() do brand_loader)")
    parser.add_argument("--date", default=None, help="Data (default: hoje no formato dd/mm/yyyy)")
    parser.add_argument(
        "--brand",
        default=None,
        help="Texto da marca no header (default: brand_name() do brand_loader)",
    )
    parser.add_argument(
        "--email",
        default=None,
        help="Email no footer (default: do brand_loader; vazio se nao definido)",
    )
    parser.add_argument(
        "--site",
        default=None,
        help="Site no footer (default: website_or_blank() do brand_loader)",
    )
    args = parser.parse_args()

    if not os.path.isfile(args.input):
        print("ERRO: arquivo de entrada nao encontrado: " + args.input, file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        md_text = f.read()

    blocks = parse_markdown(md_text)
    auto_title, auto_subtitle = extract_title_subtitle(blocks)

    title = args.title or auto_title or os.path.splitext(os.path.basename(args.input))[0]
    subtitle = args.subtitle if args.subtitle is not None else (auto_subtitle or "")

    date_str = args.date or datetime.now().strftime("%d/%m/%Y")

    builder = DocxBuilder(
        title=title,
        subtitle=subtitle,
        author=args.author,
        date_str=date_str,
        contact_email=args.email,
        contact_site=args.site,
        brand_label=args.brand,
    )

    render_blocks_to_docx(builder, blocks)

    out_path = builder.save(args.output)
    size_kb = os.path.getsize(out_path) / 1024
    print("OK -> " + out_path + " (" + str(round(size_kb, 1)) + " KB)")


if __name__ == "__main__":
    main()
