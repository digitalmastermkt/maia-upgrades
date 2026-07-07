"""
Design system Carrossel Instagram Premium.
Paleta + fontes + helpers visuais. Extraido do render real.
Marca (handle/nome no footer) vem do sistema central /opt/MAIA/brand/brand.json via brand_loader.
Mantenha 1:1 com o spec em SKILL.md.
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import sys
sys.path.insert(0, "/opt/MAIA")
from brand_loader import footer_handle, brand_name, slogan_or_blank, website_or_blank, owner_name, get, colors

# ============= PATHS =============
BASE = Path("/opt/MAIA")
BANCO = BASE / "assets/brand/banco_fotos/2026-05"

# ============= FONTES =============
JAKARTA = BASE / "assets/fonts/plus_jakarta"
INTER = BASE / "assets/fonts/inter"
JETBRAINS = BASE / "assets/fonts/jetbrains_mono"

F_HEADLINE = str(JAKARTA / "PlusJakartaSans-ExtraBold.ttf")
F_BODY_BOLD = str(INTER / "Inter-Bold.ttf")
F_BODY_SEMI = str(INTER / "Inter-SemiBold.ttf")
F_BODY = str(INTER / "Inter-Medium.ttf")
F_CTA = str(JAKARTA / "PlusJakartaSans-Bold.ttf")
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



BANCO_ENSAIO_05_18 = BASE / "assets/brand/banco_fotos/ensaio_2026-05-18"
ACCENTS_VALIDOS = {DOURADO_BRILHANTE, AMARELO_NEON, TEAL_GLOW, VERMELHO}

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
            draw_arrow_right(draw, W - PAD - arrow_w + 4, ay, color)
        else:
            x = W - PAD - tw
            draw.text((x, y_cta_top + i * line_h), line, font=fnt_cta, fill=color)


def draw_arrow_right(draw, x, y, color, size: int = 22):
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
    draw_arrow_right(draw, x + tw + 8, y_pos, color, size=18)
