"""
Templates de slide pra carrossel premium - importa carousel_design_system.
4 templates: render_capa, render_corpo, render_cta_final + render_slide (dispatcher).

render_bullet TODO (extender render_corpo com prefixo > em accent).
"""
from __future__ import annotations
from PIL import Image, ImageDraw

import sys
sys.path.insert(0, "/opt/MAIA")
from brand_loader import footer_handle, brand_name, slogan_or_blank, website_or_blank, owner_name, get, colors

from carousel_design_system import (
    W, H, PAD, SAFE_TOP, SAFE_BOTTOM,
    PRETO, PRETO_PURO, OFFWHITE, BRANCO,
    DOURADO, DOURADO_BRILHANTE, AMARELO_NEON, TEAL_GLOW, VERMELHO, CINZA_CLARO,
    F_HEADLINE, F_BODY_BOLD, F_BODY_SEMI, F_BODY, F_CTA, F_KICKER,
    font, text_size, wrap_text, draw_text_with_shadow,
    make_background, gradient_overlay,
    add_kicker, add_slide_indicator, add_footer_and_cta, draw_arrow_right,
)

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
    draw_arrow_right(draw, W - PAD - arrow_w + 4, cta_y + 8, PRETO_PURO, size=22)

    return canvas

# ====================================================================
# DISPATCHER
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

