"""
Render 10 carrosseis 1:1 (1080x1080) - Imersao Maquina de Vendas com IA.
Adaptado do template das stories (story_NN.png) pra formato FEED quadrado.

Uso:
    python3 /opt/MAIA/workspace/carrosseis-mv-2026-05-17/render_carrosseis.py
    python3 .../render_carrosseis.py --only 10        # so o carrossel 10
    python3 .../render_carrosseis.py --only 10,4,3   # multiplos

Saida:
    /opt/MAIA/workspace/carrosseis-mv-2026-05-17/artes/carrossel_NN/slide_M.png

Identidade visual (igual stories):
    BG: foto desfocada da marca (banco_fotos/2026-05) + gradient escuro
    Tag superior: "// CAPA", "// SLIDE 2/6" em monospace ciano/teal
    Headline: Plus Jakarta ExtraBold, cor de destaque (DOURADO_BRILHANTE = #F0C882)
    Corpo: Inter SemiBold/Medium, off-white
    Footer: handle + nome da marca (brand_loader.footer_handle / brand_name)
    CTA flutuante alinhado a direita acima do footer
    Slide CTA final: fundo dourado solido com texto preto (oferta dura)
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, "/opt/MAIA")
from brand_loader import footer_handle, brand_name, slogan_or_blank, website_or_blank, owner_name, get, colors

# ============= PATHS =============
BASE = Path("/opt/MAIA")
BANCO = BASE / "assets/brand/banco_fotos/2026-05"
OUT_BASE = BASE / "workspace/carrosseis-mv-2026-05-17/artes"
OUT_BASE.mkdir(parents=True, exist_ok=True)

# ============= FONTES =============
JAKARTA = BASE / "assets/fonts/plus_jakarta"
INTER = BASE / "assets/fonts/inter"
JETBRAINS = BASE / "assets/fonts/jetbrains_mono"

F_HEADLINE = str(JAKARTA / "PlusJakartaSans-ExtraBold.ttf")
F_BODY_BOLD = str(INTER / "Inter-Bold.ttf")
F_BODY_SEMI = str(INTER / "Inter-SemiBold.ttf")
F_BODY = str(INTER / "Inter-Medium.ttf")
F_CTA = str(JAKARTA / "PlusJakartaSans-Bold.ttf")
F_KICKER = str(JETBRAINS / "JetBrainsMono-Variable.ttf")

# ============= PALETA (mesma das stories) =============
PRETO = (10, 10, 10)
PRETO_PURO = (0, 0, 0)
OFFWHITE = (245, 243, 238)
BRANCO = (255, 255, 255)
DOURADO = (201, 169, 110)
DOURADO_BRILHANTE = (240, 200, 130)
AMARELO_NEON = (255, 215, 0)
TEAL_GLOW = (90, 220, 215)
VERMELHO = (255, 68, 68)
CINZA_CLARO = (180, 180, 180)

# ============= LAYOUT 1080x1080 =============
W, H = 1080, 1080
PAD = 64                # margem lateral
SAFE_TOP = 90           # topo (espaco do kicker)
SAFE_BOTTOM = 130       # rodape (footer + CTA)


# ====================================================================
# HELPERS
# ====================================================================
def load_photo(name: str) -> Image.Image:
    return Image.open(BANCO / name).convert("RGB")


def cover_resize(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    src_ratio = img.width / img.height
    dst_ratio = target_w / target_h
    if src_ratio > dst_ratio:
        new_h = target_h
        new_w = int(new_h * src_ratio)
    else:
        new_w = target_w
        new_h = int(new_w / src_ratio)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def darken(img: Image.Image, factor: float = 0.55) -> Image.Image:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, int(255 * (1 - factor))))
    base = img.convert("RGBA")
    return Image.alpha_composite(base, overlay).convert("RGB")


def gradient_overlay(base: Image.Image, top_color=(0, 0, 0, 0), bottom_color=(0, 0, 0, 200)) -> Image.Image:
    w, h = base.size
    grad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = grad.load()
    for y in range(h):
        t = y / h
        r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
        g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
        b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
        a = int(top_color[3] * (1 - t) + bottom_color[3] * t)
        for x in range(w):
            px[x, y] = (r, g, b, a)
    return Image.alpha_composite(base.convert("RGBA"), grad).convert("RGB")


def apply_blur(img: Image.Image, radius: int = 6) -> Image.Image:
    return img.filter(ImageFilter.GaussianBlur(radius))


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def text_size(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.FreeTypeFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=fnt)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_text(text: str, fnt: ImageFont.FreeTypeFont, draw: ImageDraw.ImageDraw, max_w: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    lines = []
    cur = words[0]
    for w in words[1:]:
        test = f"{cur} {w}"
        if text_size(draw, test, fnt)[0] <= max_w:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def draw_text_with_shadow(draw, pos, text, fnt, fill, shadow=(0, 0, 0, 220), offset: int = 3):
    x, y = pos
    draw.text((x + offset, y + offset), text, font=fnt, fill=shadow)
    draw.text((x, y), text, font=fnt, fill=fill)


# ====================================================================
# COMPONENTES VISUAIS
# ====================================================================
def make_background(photo_name: str, escurece: float = 0.32, blur: int = 6) -> Image.Image:
    photo = load_photo(photo_name)
    bg = cover_resize(photo, W, H)
    if blur > 0:
        bg = apply_blur(bg, blur)
    if escurece < 1.0:
        bg = darken(bg, escurece)
    return bg


def add_kicker(draw: ImageDraw.ImageDraw, text: str, color=TEAL_GLOW, y: int = SAFE_TOP - 20) -> int:
    """Tag superior monospace estilo '// SLIDE 3/6'. Retorna y abaixo."""
    fnt = font(F_KICKER, 22)
    draw.text((PAD, y), text.upper(), font=fnt, fill=color)
    tw, _ = text_size(draw, text.upper(), fnt)
    draw.line([(PAD, y + 32), (PAD + tw, y + 32)], fill=color, width=2)
    return y + 44


def add_footer_and_cta(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    cta_text: str | None = None,
    color=DOURADO_BRILHANTE,
    show_cta: bool = True,
):
    """Footer + (opcional) CTA acima.
    Layout fixo:
      H-70: handle da marca (brand_loader.footer_handle)
      H-44: nome da marca (brand_loader.brand_name)
      divisor dourado
      CTA acima do divisor, alinhado a direita
    """
    fnt_kick = font(F_KICKER, 20)
    fnt_handle = font(F_BODY_SEMI, 22)
    handle_y = H - 80
    draw.text((PAD, handle_y), footer_handle().upper(), font=fnt_handle, fill=OFFWHITE)
    draw.text((PAD, handle_y + 30), brand_name().upper(), font=fnt_kick, fill=DOURADO)

    # divisor sobre o footer
    div_y = handle_y - 22
    draw.line([(PAD, div_y), (W - PAD, div_y)], fill=color, width=2)

    if not show_cta or not cta_text:
        return

    fnt_cta = font(F_CTA, 24)
    arrow_w = 28
    max_cta_w = W - PAD * 2 - arrow_w - 10
    lines = wrap_text(cta_text.upper(), fnt_cta, draw, max_cta_w)
    if len(lines) > 2:
        fnt_cta = font(F_CTA, 20)
        lines = wrap_text(cta_text.upper(), fnt_cta, draw, max_cta_w)

    line_h = int(fnt_cta.size * 1.18)
    total_h = line_h * len(lines)
    y_cta_top = div_y - 14 - total_h

    for i, line in enumerate(lines):
        tw, _ = text_size(draw, line, fnt_cta)
        is_last = i == len(lines) - 1
        if is_last:
            x = W - PAD - tw - arrow_w - 6
            draw.text((x, y_cta_top + i * line_h), line, font=fnt_cta, fill=color)
            ay = y_cta_top + i * line_h + (fnt_cta.size - 20) // 2
            _draw_arrow_right(draw, W - PAD - arrow_w + 4, ay, color)
        else:
            x = W - PAD - tw
            draw.text((x, y_cta_top + i * line_h), line, font=fnt_cta, fill=color)


def _draw_arrow_right(draw, x, y, color, size: int = 22):
    draw.polygon([(x, y), (x, y + size), (x + size, y + size // 2)], fill=color)


def add_slide_indicator(draw: ImageDraw.ImageDraw, idx: int, total: int, color=DOURADO_BRILHANTE):
    """Indicador 'X / Y' no canto superior direito."""
    fnt = font(F_KICKER, 22)
    txt = f"{idx:02d} / {total:02d}"
    tw, _ = text_size(draw, txt, fnt)
    x = W - PAD - tw
    y = SAFE_TOP - 20
    draw.text((x, y), txt, font=fnt, fill=color)


def add_swipe_hint(draw, y_pos: int, color=DOURADO_BRILHANTE):
    """Texto 'ARRASTA ->' no rodape."""
    fnt = font(F_KICKER, 20)
    txt = "ARRASTA"
    tw, _ = text_size(draw, txt, fnt)
    arrow_w = 22
    total_w = tw + 8 + arrow_w
    x = W - PAD - total_w
    draw.text((x, y_pos), txt, font=fnt, fill=color)
    _draw_arrow_right(draw, x + tw + 8, y_pos, color, size=18)


# ====================================================================
# TEMPLATES DE SLIDE
# ====================================================================
def render_capa(
    headline: str,
    slide_idx: int,
    total_slides: int,
    photo_name: str,
    kicker: str = "// CAPA",
    accent=DOURADO_BRILHANTE,
    cta_text: str = "ARRASTA PRA VER",
) -> Image.Image:
    """Capa: hook gigante em accent, gradient pesado pra leitura, indicador 1/N."""
    bg = make_background(photo_name, escurece=0.30, blur=8)
    bg = gradient_overlay(bg, (0, 0, 0, 80), (0, 0, 0, 235))
    canvas = bg.convert("RGB")
    draw = ImageDraw.Draw(canvas)

    add_kicker(draw, kicker, color=accent)
    add_slide_indicator(draw, slide_idx, total_slides, color=accent)

    # Headline gigante centralizado verticalmente
    hook_fnt = font(F_HEADLINE, 78)
    lines = wrap_text(headline, hook_fnt, draw, W - PAD * 2)
    if len(lines) > 4:
        hook_fnt = font(F_HEADLINE, 64)
        lines = wrap_text(headline, hook_fnt, draw, W - PAD * 2)
    if len(lines) > 5:
        hook_fnt = font(F_HEADLINE, 54)
        lines = wrap_text(headline, hook_fnt, draw, W - PAD * 2)

    line_h = int(hook_fnt.size * 1.05)
    total_h = line_h * len(lines)
    y = (H - total_h) // 2 - 40
    for line in lines:
        draw_text_with_shadow(draw, (PAD, y), line, hook_fnt, accent, offset=5)
        y += line_h

    # tarja decorativa
    draw.rectangle([PAD, y + 20, PAD + 160, y + 28], fill=accent)

    add_footer_and_cta(canvas, draw, cta_text, color=accent)
    return canvas


def render_corpo(
    body_lines: list[str],
    slide_idx: int,
    total_slides: int,
    photo_name: str,
    kicker: str | None = None,
    accent=DOURADO_BRILHANTE,
    cta_text: str = "ARRASTA",
    headline: str | None = None,
) -> Image.Image:
    """Slide de corpo: headline opcional + paragrafos."""
    bg = make_background(photo_name, escurece=0.28, blur=8)
    bg = gradient_overlay(bg, (0, 0, 0, 100), (0, 0, 0, 235))
    canvas = bg.convert("RGB")
    draw = ImageDraw.Draw(canvas)

    if kicker is None:
        kicker = f"// SLIDE {slide_idx:02d}"
    add_kicker(draw, kicker, color=accent)
    add_slide_indicator(draw, slide_idx, total_slides, color=accent)

    y = SAFE_TOP + 50

    # headline opcional (ex: 'FRASE 1:', 'ANTES:')
    if headline:
        hl_fnt = font(F_HEADLINE, 60)
        hl_lines = wrap_text(headline, hl_fnt, draw, W - PAD * 2)
        if len(hl_lines) > 2:
            hl_fnt = font(F_HEADLINE, 50)
            hl_lines = wrap_text(headline, hl_fnt, draw, W - PAD * 2)
        for line in hl_lines:
            draw_text_with_shadow(draw, (PAD, y), line, hl_fnt, accent, offset=4)
            y += int(hl_fnt.size * 1.08)
        # divisor curto
        draw.rectangle([PAD, y + 18, PAD + 140, y + 24], fill=accent)
        y += 56

    # corpo
    body_fnt = font(F_BODY_SEMI, 38)

    def _measure_height(fnt):
        lh = int(fnt.size * 1.42)
        total = 0
        for para in body_lines:
            if not para.strip():
                total += int(lh * 0.55)  # linha em branco = meio gap
                continue
            ws = wrap_text(para, fnt, draw, W - PAD * 2)
            total += lh * len(ws) + int(lh * 0.25)
        return total

    max_available = H - y - SAFE_BOTTOM - 100
    for sz in (38, 34, 32, 30, 28):
        body_fnt = font(F_BODY_SEMI, sz)
        if _measure_height(body_fnt) < max_available:
            break

    line_h = int(body_fnt.size * 1.42)
    for para in body_lines:
        if not para.strip():
            y += int(line_h * 0.55)
            continue
        ws = wrap_text(para, body_fnt, draw, W - PAD * 2)
        for sub in ws:
            draw_text_with_shadow(draw, (PAD, y), sub, body_fnt, OFFWHITE, offset=2)
            y += line_h
        y += int(line_h * 0.25)

    add_footer_and_cta(canvas, draw, cta_text, color=accent)
    return canvas


def render_cta_final(
    headline: str,
    body_lines: list[str],
    slide_idx: int,
    total_slides: int,
    accent=DOURADO_BRILHANTE,
) -> Image.Image:
    """Slide CTA: fundo dourado solido + texto preto. Pesado, centralizado."""
    canvas = Image.new("RGB", (W, H), accent)
    draw = ImageDraw.Draw(canvas)

    # textura sutil (linhas diagonais escuras)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for i in range(-H, W, 32):
        od.line([(i, 0), (i + H, H)], fill=(0, 0, 0, 14), width=1)
    canvas = Image.alpha_composite(canvas.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(canvas)

    # ============ Topo: kicker + indicador ============
    fnt_kick = font(F_KICKER, 22)
    draw.text((PAD, SAFE_TOP - 20), "// CTA", font=fnt_kick, fill=PRETO_PURO)
    tw, _ = text_size(draw, "// CTA", fnt_kick)
    draw.line([(PAD, SAFE_TOP - 20 + 32), (PAD + tw, SAFE_TOP - 20 + 32)], fill=PRETO_PURO, width=2)

    txt_ind = f"{slide_idx:02d} / {total_slides:02d}"
    tw, _ = text_size(draw, txt_ind, fnt_kick)
    draw.text((W - PAD - tw, SAFE_TOP - 20), txt_ind, font=fnt_kick, fill=PRETO_PURO)

    # ============ Caixa preta central com toda a info ============
    # mede tudo primeiro pra centralizar verticalmente
    hook_fnt = font(F_HEADLINE, 86)
    hook_lines = wrap_text(headline, hook_fnt, draw, W - PAD * 2 - 80)
    if len(hook_lines) > 2:
        hook_fnt = font(F_HEADLINE, 72)
        hook_lines = wrap_text(headline, hook_fnt, draw, W - PAD * 2 - 80)
    if len(hook_lines) > 3:
        hook_fnt = font(F_HEADLINE, 60)
        hook_lines = wrap_text(headline, hook_fnt, draw, W - PAD * 2 - 80)
    hook_line_h = int(hook_fnt.size * 1.05)
    hook_h = hook_line_h * len(hook_lines)

    # Corpo: ajusta tamanho ate caber dentro do box previsto
    body_fnt = font(F_BODY_BOLD, 38)
    max_box_h = H - SAFE_TOP - SAFE_BOTTOM - 80
    def _measure(fnt):
        lh = int(fnt.size * 1.38)
        total = 0
        for para in body_lines:
            if not para.strip():
                total += int(lh * 0.5)
                continue
            ws = wrap_text(para, fnt, draw, W - PAD * 2 - 80)
            total += lh * len(ws) + int(lh * 0.2)
        return total

    for sz in (38, 34, 32, 30, 28):
        body_fnt = font(F_BODY_BOLD, sz)
        body_h_est = _measure(body_fnt)
        if hook_h + 80 + body_h_est < max_box_h:
            break

    body_h = _measure(body_fnt)
    box_h = hook_h + 60 + body_h + 80
    box_h = min(box_h, max_box_h)
    box_w = W - PAD * 2
    box_x = PAD
    box_y = (H - box_h) // 2

    # box preto com borda dourada interna
    box_rgba = Image.new("RGBA", (box_w, box_h), (8, 8, 8, 245))
    canvas_rgba = canvas.convert("RGBA")
    canvas_rgba.paste(box_rgba, (box_x, box_y), box_rgba)
    canvas = canvas_rgba.convert("RGB")
    draw = ImageDraw.Draw(canvas)

    # borda dourada esquerda (peso visual)
    draw.rectangle([box_x, box_y, box_x + 10, box_y + box_h], fill=accent)
    # canto superior direito: tag '#13/06' decorativa
    tag_fnt = font(F_KICKER, 20)
    tag_txt = "// 13 . 06 . 2026"
    tw_tag, _ = text_size(draw, tag_txt, tag_fnt)
    draw.text((box_x + box_w - 40 - tw_tag, box_y + 30), tag_txt, font=tag_fnt, fill=accent)

    # ============ Conteudo dentro do box ============
    inner_pad_x = 50
    y = box_y + 70

    # Headline em dourado
    for line in hook_lines:
        draw_text_with_shadow(
            draw,
            (box_x + inner_pad_x, y),
            line,
            hook_fnt,
            accent,
            shadow=(0, 0, 0, 200),
            offset=3,
        )
        y += hook_line_h

    # divisor curto dourado
    draw.rectangle([box_x + inner_pad_x, y + 20, box_x + inner_pad_x + 140, y + 28], fill=accent)
    y += 60

    # corpo branco
    line_h_body = int(body_fnt.size * 1.38)
    for para in body_lines:
        if not para.strip():
            y += int(line_h_body * 0.5)
            continue
        ws = wrap_text(para, body_fnt, draw, box_w - inner_pad_x * 2)
        for sub in ws:
            draw.text((box_x + inner_pad_x, y), sub, font=body_fnt, fill=OFFWHITE)
            y += line_h_body
        y += int(line_h_body * 0.2)

    # ============ Footer preto no rodape (texto preto sobre dourado) ============
    fnt_handle = font(F_BODY_SEMI, 22)
    handle_y = H - 80
    draw.text((PAD, handle_y), footer_handle().upper(), font=fnt_handle, fill=PRETO_PURO)
    draw.text((PAD, handle_y + 30), brand_name().upper(), font=fnt_kick, fill=PRETO_PURO)
    draw.line([(PAD, handle_y - 22), (W - PAD, handle_y - 22)], fill=PRETO_PURO, width=2)

    # selo "LINK NA BIO ->" canto direito
    fnt_cta = font(F_CTA, 30)
    cta_txt = "LINK NA BIO"
    tw, _ = text_size(draw, cta_txt, fnt_cta)
    arrow_w = 28
    x = W - PAD - tw - arrow_w - 10
    cta_y = handle_y - 22 - 16 - 32
    draw.text((x, cta_y), cta_txt, font=fnt_cta, fill=PRETO_PURO)
    _draw_arrow_right(draw, W - PAD - arrow_w + 4, cta_y + 8, PRETO_PURO, size=22)

    return canvas


# ====================================================================
# DEFINICAO DOS CARROSSEIS (parseado da copy)
# ====================================================================
# Estrutura: cada slide = dict com tipo (capa/corpo/cta) + conteudo
# Para corpo: pode ter 'headline' opcional + 'body' (lista de paragrafos)
# Acento por carrossel = mood (DOURADO p/ caso real, AMARELO p/ pergunta, etc)

CARROSSEIS = {
    1: {
        "tema": "Tá vendendo ou apagando incêndio?",
        "accent": AMARELO_NEON,
        "kicker_capa": "// PERGUNTA",
        "foto": "foto_01.png",
        "slides": [
            {
                "tipo": "capa",
                "headline": "TÁ VENDENDO OU APAGANDO INCÊNDIO?",
                "cta": "ARRASTA",
            },
            {
                "tipo": "corpo",
                "headline": None,
                "body": [
                    "R$50k, R$500k ou R$2M/mês:",
                    "se o dia é apagar incêndio,",
                    "o jogo é o mesmo.",
                    "6h da manhã respondendo cliente.",
                    "22h fechando caixa.",
                    "Final de semana? Boleto e dor de cabeça.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "TU NÃO TEM UMA EMPRESA",
                "body": [
                    "Tu tem um trabalho que te paga mais.",
                    "Trabalho você escolhe largar.",
                    "Empresa que depende de ti, tu é refém.",
                    "Vale pra PME e pra dono com 80 funcionários.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "EMPRESA DE VERDADE",
                "body": [
                    "Roda sem o dono no operacional.",
                    "Vendedor IA prospecta.",
                    "WhatsApp IA qualifica.",
                    "Follow-up automático fecha.",
                    "Tu cuida do que só tu pode: estratégia.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "13/06 EU INSTALO COM TU",
                "body": [
                    "Ao vivo. 6h de imersão.",
                    "Tu sai com o funil rodando no mesmo dia.",
                    "Garantia: não rodou, devolvo o dinheiro.",
                ],
            },
            {
                "tipo": "cta",
                "headline": "LINK NA BIO",
                "body": [
                    "Imersão Máquina de Vendas com IA",
                    "13 de junho — Online ao vivo",
                    "Lote 1 Fundadores: R$47",
                    "15 vagas",
                ],
            },
        ],
    },
    2: {
        "tema": "Tua empresa para se tu sumir 7 dias?",
        "accent": VERMELHO,
        "kicker_capa": "// TESTE BRUTAL",
        "foto": "foto_02.png",
        "slides": [
            {
                "tipo": "capa",
                "headline": "TUA EMPRESA PARA SE TU SUMIR 7 DIAS?",
                "cta": "ARRASTA",
            },
            {
                "tipo": "corpo",
                "headline": None,
                "body": [
                    "Empresário que é gargalo não tem empresa.",
                    "Tem emprego com camisa de dono.",
                    "A folha de pagamento é tua.",
                    "Mas o chefe ainda é o cliente que liga às 21h.",
                    "Vale pra dono de 2 funcionários e pra dono de 80.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "3 SINAIS DE REFÉM",
                "body": [
                    "1. Vendedor (ou time) só fecha quando tu entra no Whats",
                    "2. Operacional trava se tu viajar",
                    "3. Agenda refém de urgência, não de prioridade",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "NÃO É CONTRATAR MAIS GENTE",
                "body": [
                    "Gente custa folha, INSS, férias, treinamento.",
                    "Quanto maior a empresa, maior o custo da contratação errada.",
                    "A saída é processo + IA.",
                    "Máquina que roda 24h sem reclamar,",
                    "sem ficar doente, sem pedir aumento.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "CASO REAL",
                "body": [
                    "Dono de distribuidora instalou IA no Whats.",
                    "Viajou 10 dias.",
                    "Voltou com 23 vendas fechadas.",
                    "Sem responder UMA mensagem.",
                    "Mesma lógica funciona pra clínica com 20 unidades.",
                ],
            },
            {
                "tipo": "cta",
                "headline": "INSTALA NO TEU NEGÓCIO",
                "body": [
                    "Imersão 13/06 — Online ao vivo",
                    "6h práticas",
                    "Lote 1: R$47",
                    "Link na bio",
                ],
            },
        ],
    },
    3: {
        "tema": "73% das empresas vão usar IA em 2026",
        "accent": TEAL_GLOW,
        "kicker_capa": "// DADO 2026",
        "foto": "foto_03.png",
        "slides": [
            {
                "tipo": "capa",
                "headline": "73% DAS EMPRESAS VÃO USAR IA EM 2026",
                "cta": "VEJA O DADO",
            },
            {
                "tipo": "corpo",
                "headline": "DADO NÃO MENTE",
                "body": [
                    "Pesquisa Sebrae + McKinsey 2026.",
                    "Em 6 meses, 7 em cada 10 empresas do teu setor",
                    "vão ter IA rodando vendas.",
                    "De PME a empresa de médio porte.",
                    "Diferença de preço fica irrelevante.",
                    "Diferença de velocidade DECIDE.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "QUEM VAI TE QUEBRAR",
                "body": [
                    "Não é o novato.",
                    "É o cara da TUA idade, do TEU setor,",
                    "do TEU porte, que aprendeu IA antes de tu.",
                    "Ele responde lead em 30s.",
                    "Tu em 4h. Quem fecha?",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "O PERIGO REAL",
                "body": [
                    "Não é IA substituir tua empresa.",
                    "É o EMPRESÁRIO com IA",
                    "substituir o empresário sem IA.",
                    "Aconteceu com loja de bairro",
                    "E com rede de 50 unidades em 2015.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "JANELA ABERTA",
                "body": [
                    "Quem não foi pro Instagram em 2015",
                    "hoje paga R$3 por lead.",
                    "Quem não usar IA em 2026",
                    "vai pagar 4x mais caro pra fechar metade.",
                    "Por enquanto.",
                ],
            },
            {
                "tipo": "cta",
                "headline": "ENTRA NESSES 73%",
                "body": [
                    "Imersão Máquina de Vendas com IA",
                    "13/06 — Online ao vivo",
                    "Sai com funil rodando no mesmo dia",
                    "Lote 1: R$47",
                ],
            },
        ],
    },
    4: {
        "tema": "Ele faturou R$140k sem contratar ninguém",
        "accent": DOURADO_BRILHANTE,
        "kicker_capa": "// CASO REAL",
        "foto": "foto_04.png",
        "slides": [
            {
                "tipo": "capa",
                "headline": "R$80K SOZINHO. 90 DIAS DEPOIS: R$140K.",
                "cta": "VEJA COMO",
            },
            {
                "tipo": "corpo",
                "headline": "DIAGNÓSTICO",
                "body": [
                    "Cidade interior.",
                    "1 atendente (a esposa).",
                    "~300 leads/semana no Whats.",
                    "Conseguia responder ~80. Resto: morria.",
                    "Mesmo gargalo trava R$80k e R$800k:",
                    "lead não atendido vira venda perdida.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "SOLUÇÃO INSTALADA",
                "body": [
                    "Agente IA no WhatsApp Business.",
                    "Qualifica os 300 leads em 5 min cada.",
                    "Marca lead quente.",
                    "Só passa pro dono (ou time comercial)",
                    "os que já querem comprar.",
                    "Escala de 1 atendente a 50, mesma lógica.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "RESULTADO 90 DIAS",
                "body": [
                    "Lead respondido em 30s (era 4h)",
                    "Conversão subiu de 8% pra 19%",
                    "Faturamento: R$80k → R$140k",
                    "Horas trabalhadas: 12/dia → 6/dia",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "QUANTO CUSTOU?",
                "body": [
                    "R$80/mês em ferramentas.",
                    "Sem contratar funcionário.",
                    "Sem agência. Sem milagre.",
                    "ROI escala com o volume de lead:",
                    "mais lead, mais ganho na mesma máquina.",
                ],
            },
            {
                "tipo": "cta",
                "headline": "INSTALA O MESMO FUNIL",
                "body": [
                    "Imersão 13/06 — Online ao vivo",
                    "Prática: do zero ao funcionando",
                    "Lote 1: R$47",
                    "Link na bio",
                ],
            },
        ],
    },
    5: {
        "tema": "3 frases que custam dinheiro",
        "accent": VERMELHO,
        "kicker_capa": "// ANTI-CONSELHO",
        "foto": "foto_05.png",
        "slides": [
            {
                "tipo": "capa",
                "headline": "3 FRASES QUE TE CUSTARAM CLIENTE ESSA SEMANA",
                "cta": "QUAIS?",
            },
            {
                "tipo": "corpo",
                "headline": "FRASE 1",
                "body": [
                    "“IA é coisa do futuro.”",
                    "",
                    "ERRADO.",
                    "IA hoje responde Whats em 30s",
                    "e fecha venda enquanto tu dorme.",
                    "Da loja de bairro à rede de 30 unidades:",
                    "concorrente já tá usando.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "FRASE 2",
                "body": [
                    "“No meu nicho/porte isso não funciona.”",
                    "",
                    "ERRADO.",
                    "Distribuidora, clínica, escola, loja,",
                    "advocacia, oficina, indústria, franquia:",
                    "tem caso real em TODOS. PME e médio/grande.",
                    "O que não funciona é resistência disfarçada.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "FRASE 3",
                "body": [
                    "“Quando ficar mais madura, eu vejo.”",
                    "",
                    "ERRADO.",
                    "Quando ficar madura, custa 10x mais caro.",
                    "Quem entra cedo paga R$47 numa imersão.",
                    "Quem entra tarde paga R$15k correndo atrás.",
                    "Grande empresa paga muito mais.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "CADA VEZ QUE TU REPETE",
                "body": [
                    "Perde:",
                    "1 lead que já era do concorrente",
                    "1 hora do dia que IA resolveria",
                    "R$X de faturamento que nunca volta",
                ],
            },
            {
                "tipo": "cta",
                "headline": "PARA DE ADIAR",
                "body": [
                    "13/06 eu te ensino na prática",
                    "Imersão Máquina de Vendas com IA",
                    "Online ao vivo",
                    "Lote 1: R$47",
                ],
            },
        ],
    },
    6: {
        "tema": "A ferramenta que tu instala hoje",
        "accent": TEAL_GLOW,
        "kicker_capa": "// APLICA HOJE",
        "foto": "foto_06.png",
        "slides": [
            {
                "tipo": "capa",
                "headline": "1 FERRAMENTA QUE DOBRA TUA TAXA DE FECHAMENTO",
                "cta": "TUTORIAL",
            },
            {
                "tipo": "corpo",
                "headline": "O QUE PRECISA",
                "body": [
                    "1. WhatsApp Business (grátis)",
                    "2. Conta OpenAI ou Anthropic (~R$50/mês)",
                    "3. Plataforma de conexão",
                    "    (Z-API, Evolution) ~R$80/mês",
                    "",
                    "Total: <R$150/mês.",
                    "Mesmo custo pra qualquer porte.",
                    "ROI escala com volume de lead.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "AGENTE IA FAZ 3 PERGUNTAS",
                "body": [
                    "Antes de tu (ou teu vendedor) entrar:",
                    "1. Qual é tua dor específica?",
                    "2. Qual é teu orçamento aproximado?",
                    "3. Quando tu precisa resolver?",
                    "",
                    "3 respostas batem = lead QUENTE.",
                    "Tu (ou time) só atende quem tá pronto.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "RESULTADO MENSURADO",
                "body": [
                    "Tu (e teu time) não perde tempo com curioso",
                    "Lead chega já aquecido",
                    "Taxa de conversão dobra (em média)",
                    "Economiza 2h/dia de atendimento bruto",
                    "Time comercial fecha mais sem contratar",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "LIMITE DA SETUP CASEIRA",
                "body": [
                    "Tu instala sozinho? Sim.",
                    "Vai gastar 2 semanas pra acertar o prompt?",
                    "Também.",
                    "",
                    "Na imersão 13/06 tu sai com tudo PRONTO.",
                    "Em 1 dia.",
                ],
            },
            {
                "tipo": "cta",
                "headline": "INSTALA COMIGO AO VIVO",
                "body": [
                    "Imersão Máquina de Vendas com IA",
                    "13/06 — Online ao vivo",
                    "Lote 1: R$47",
                    "Link na bio",
                ],
            },
        ],
    },
    7: {
        "tema": "Antes da IA / Depois da IA",
        "accent": DOURADO_BRILHANTE,
        "kicker_capa": "// ANTES X DEPOIS",
        "foto": "foto_01.png",
        "slides": [
            {
                "tipo": "capa",
                "headline": "MESMO ESFORÇO. RESULTADO 4X MAIOR.",
                "cta": "VEJA",
            },
            {
                "tipo": "corpo",
                "headline": "ANTES",
                "body": [
                    "12h/dia respondendo Whats (tu ou teu time)",
                    "Fechava ~3 vendas por atendente",
                    "Sábado e domingo trabalhando",
                    "Esposa reclamando",
                    "Folha pesando, resultado não escala",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "DEPOIS",
                "body": [
                    "IA qualifica 100 leads enquanto tu toma café",
                    "Tu (ou teu time) só fala com os 10 QUENTES",
                    "Fecha 10 de 10 (ou perto)",
                    "6h de trabalho efetivo",
                    "Final de semana livre",
                    "Mesmo time produz 4x mais sem hora extra",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "O SEGREDO",
                "body": [
                    "Não é trabalhar mais (nem contratar mais).",
                    "É trabalhar nos leads CERTOS.",
                    "IA elimina o curioso, o turista,",
                    "o pesquisador de preço.",
                    "Tu (e teu time) só atende quem decidiu comprar.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "COMPARATIVO DIRETO",
                "body": [
                    "Esforço: igual",
                    "Tempo: −50%",
                    "Faturamento: +300% (média dos casos)",
                    "Stress: −90% (tu sente)",
                    "Necessidade de contratação: −70%",
                ],
            },
            {
                "tipo": "cta",
                "headline": "MIGRA EM 1 DIA",
                "body": [
                    "Imersão 13/06 — Online ao vivo",
                    "6h instalando contigo",
                    "Lote 1: R$47",
                    "Link na bio",
                ],
            },
        ],
    },
    8: {
        "tema": "Fórmula mágica não existe. Máquina existe.",
        "accent": AMARELO_NEON,
        "kicker_capa": "// SEM MIMIMI",
        "foto": "foto_02.png",
        "slides": [
            {
                "tipo": "capa",
                "headline": "COACH DE “7 DÍGITOS” É PIADA. MÁQUINA É REAL.",
                "cta": "ARRASTA",
            },
            {
                "tipo": "corpo",
                "headline": "FÓRMULA MÁGICA PROMETE",
                "body": [
                    "R$1M em 90 dias sem trabalhar",
                    "Mindset milionário",
                    "“Manifestação” de clientes",
                    "",
                    "Não funciona pra quem paga boleto dia 10.",
                    "Nem pra quem tem folha de R$300k pra fechar.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "MÁQUINA DE VENDAS PROMETE",
                "body": [
                    "1 funil que prospecta, qualifica e fecha",
                    "Resultado mensurado em leads/vendas",
                    "Setup em 1 dia, rodando em 7",
                    "",
                    "Diferença: não depende de “energia”.",
                    "Depende de execução.",
                    slogan_or_blank(),
                ],
            },
            {
                "tipo": "corpo",
                "headline": "IA NÃO É SONHO",
                "body": [
                    "É INSTALAÇÃO.",
                    "Tu não “acredita” que vai funcionar.",
                    "Tu CONFIGURA, testa, ajusta.",
                    "Vira ferramenta concreta.",
                    "Igual ar-condicionado: ou esfria, ou não.",
                    "Empresa pequena e grande: mesmo princípio.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "ESCOLHA É TUA",
                "body": [
                    "Quem promete milagre",
                    "cobra R$15k e entrega PDF.",
                    "",
                    "Quem entrega máquina",
                    "cobra R$47 numa imersão",
                    "e entrega FUNCIONANDO.",
                    "R$50k ou R$1,5M: método é o mesmo.",
                ],
            },
            {
                "tipo": "cta",
                "headline": "SÓ FUNIL RODANDO",
                "body": [
                    "Imersão Máquina de Vendas com IA",
                    "Sem mística. Só execução.",
                    "13/06 online ao vivo",
                    "Lote 1: R$47",
                ],
            },
        ],
    },
    9: {
        "tema": "O que empresário fala depois da imersão",
        "accent": DOURADO_BRILHANTE,
        "kicker_capa": "// DEPOIMENTOS",
        "foto": "foto_03.png",
        "slides": [
            {
                "tipo": "capa",
                "headline": "3 FRASES QUE EU MAIS OUÇO DEPOIS DA IMERSÃO",
                "cta": "VEJA",
            },
            {
                "tipo": "corpo",
                "headline": "FRASE 1",
                "body": [
                    "“Saí com o vendedor IA",
                    "rodando no mesmo dia.”",
                    "",
                    "Não é promessa de marketing.",
                    "É método: 6h de imersão,",
                    "4 peças do funil instaladas,",
                    "tu sai com setup ATIVO.",
                    "Vale pra quem atende sozinho e pra quem tem time.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "FRASE 2",
                "body": [
                    "“Em 30 dias paguei a imersão 10x.”",
                    "",
                    "Conta básica pra PME:",
                    "tu paga R$47 (lote 1).",
                    "Fecha 1 venda extra/mês via IA: R$500.",
                    "Pagou 10x no primeiro mês.",
                    "Operação maior: 1 lead enterprise paga o ano.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "FRASE 3",
                "body": [
                    "“Era isso que tava faltando.",
                    "Parei de remar sozinho.”",
                    "",
                    "A dor maior não é dinheiro.",
                    "É remar contra a corrente sozinho",
                    "(ou liderando time sobrecarregado),",
                    "sem saber se vai dar certo.",
                    "Sistema rodando tira esse peso.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "BÔNUS QUE NINGUÉM FALA",
                "body": [
                    "Mas todo mundo sente:",
                    "",
                    "Voltar a almoçar com calma",
                    "Dormir antes da meia-noite",
                    "1 sábado inteiro fora do celular",
                    "Parar de ser quem tudo trava se some",
                ],
            },
            {
                "tipo": "cta",
                "headline": "SER O PRÓXIMO",
                "body": [
                    "Imersão Máquina de Vendas com IA",
                    "13/06 — Online ao vivo",
                    "Lote 1 Fundadores: R$47",
                    "Link na bio",
                ],
            },
        ],
    },
    10: {
        "tema": "Próxima turma tá abrindo",
        "accent": DOURADO_BRILHANTE,
        "kicker_capa": "// TURMA ABRINDO",
        "foto": "foto_04.png",
        "slides": [
            {
                "tipo": "capa",
                "headline": "PRÓXIMA TURMA TÁ ABRINDO. 15 VAGAS A R$47.",
                "cta": "LEIA ATÉ O FIM",
            },
            {
                "tipo": "corpo",
                "headline": "O QUE É",
                "body": [
                    "1 dia. 6h. Online ao vivo.",
                    "(Não é gravado depois assistido.)",
                    "",
                    "Tu instala 4 peças do funil COMIGO",
                    "em tela compartilhada:",
                    "• Prospecção IA",
                    "• Vendedor WhatsApp 24h",
                    "• Follow-up automático",
                    "• Biblioteca de scripts",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "PRA QUEM É",
                "body": [
                    "Dono de PME faturando R$50k–R$500k/mês.",
                    "Loja, clínica, escola, distribuidora,",
                    "advocacia, oficina, agência, e-commerce.",
                    "Quem já tentou tudo e quer parar de testar.",
                    "",
                    "NÃO É: quem não tem produto validado",
                    "ou espera milagre sem executar.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "OS LOTES",
                "body": [
                    "Lote 1 Fundadores: R$47 — 15 vagas",
                    "Lote 2: R$97 — 20 vagas",
                    "Lote 3: R$147 — 25 vagas",
                    "Lote 4 final: R$197 — sem limite",
                    "",
                    "Quem entra primeiro paga menos.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "GARANTIA",
                "body": [
                    "Tu participa do dia inteiro.",
                    "Aplica o método.",
                    "A máquina não roda em 30 dias?",
                    "",
                    "Devolvo TODO o investimento.",
                    "Risco zero.",
                ],
            },
            {
                "tipo": "corpo",
                "headline": "QUANDO E ONDE",
                "body": [
                    "DATA: 13 de junho de 2026",
                    "HORÁRIO: na confirmação da inscrição",
                    "ONDE: 100% online",
                    "CERTIFICADO: sim, ao final",
                ],
            },
            {
                "tipo": "cta",
                "headline": "LINK NA BIO",
                "body": [
                    slogan_or_blank(),
                    "Imersão Máquina de Vendas com IA",
                    "13/06 — Lote 1: R$47",
                    "15 vagas",
                ],
            },
        ],
    },
}


# ====================================================================
# DISPATCHER DE SLIDE
# ====================================================================
def render_slide(carrossel: dict, slide_idx: int, total: int) -> Image.Image:
    s = carrossel["slides"][slide_idx - 1]
    accent = carrossel["accent"]
    photo = carrossel["foto"]
    kicker_capa = carrossel.get("kicker_capa", "// CAPA")

    if s["tipo"] == "capa":
        return render_capa(
            s["headline"],
            slide_idx,
            total,
            photo,
            kicker=kicker_capa,
            accent=accent,
            cta_text=s.get("cta", "ARRASTA"),
        )
    if s["tipo"] == "cta":
        return render_cta_final(
            s["headline"],
            s["body"],
            slide_idx,
            total,
            accent=accent,
        )
    # corpo
    kicker = s.get("kicker") or f"// SLIDE {slide_idx:02d}/{total:02d}"
    return render_corpo(
        s["body"],
        slide_idx,
        total,
        photo,
        kicker=kicker,
        accent=accent,
        cta_text="ARRASTA",
        headline=s.get("headline"),
    )


def render_carrossel(carrossel_id: int) -> list[Path]:
    c = CARROSSEIS[carrossel_id]
    total = len(c["slides"])
    out_dir = OUT_BASE / f"carrossel_{carrossel_id:02d}"
    out_dir.mkdir(parents=True, exist_ok=True)

    paths = []
    print(f"\n=== Carrossel {carrossel_id:02d}: {c['tema']} ({total} slides) ===")
    for i in range(1, total + 1):
        img = render_slide(c, i, total)
        out = out_dir / f"slide_{i}.png"
        img.save(out, "PNG", optimize=True)
        sz = out.stat().st_size // 1024
        print(f"  slide_{i}.png  {sz}KB  ({c['slides'][i-1]['tipo']})")
        paths.append(out)
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="lista de carrosseis (ex: 10 ou 10,4,3)")
    args = ap.parse_args()

    if args.only:
        ids = [int(x.strip()) for x in args.only.split(",")]
    else:
        ids = sorted(CARROSSEIS.keys())

    total_imgs = 0
    for cid in ids:
        if cid not in CARROSSEIS:
            print(f"[WARN] carrossel {cid} nao definido, pulando")
            continue
        paths = render_carrossel(cid)
        total_imgs += len(paths)

    print(f"\nOK. {total_imgs} slides renderizados em {OUT_BASE}")


if __name__ == "__main__":
    main()
