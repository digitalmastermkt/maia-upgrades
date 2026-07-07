"""
compose_card_v5.py - Arquitetura final v3 cards Instagram Q&A
Naia, 2026-05-05.

5 perguntas 5 respostas (era 10).

STORIES (1080x1920, 5 cards): cada card = 1 pergunta + 1 resposta no MESMO card.
FEED (1080x1350, 10 cards = carrossel):
  card  1 -> CAPA (titulo imersao + tagline + setinha)
  cards 2,4,6,8 -> 4 perguntas
  cards 3,5,7,9 -> 4 respostas
  card 10 -> CTA (proxima edicao + link bio + setinha perfil)

Tipografia: TYPOGRAPHY_GUIDELINES.md v1.0 (Juliana).
"""
import os
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys
sys.path.insert(0, "/opt/MAIA")
from brand_loader import footer_handle, brand_name, slogan_or_blank, website_or_blank, owner_name, get, colors

STORIES_SIZE = (1080, 1920)
FEED_SIZE = (1080, 1350)

# Cores
BG_DARK = (10, 10, 26, 255)
BG_DARKER = (4, 4, 12, 255)
ACCENT_TEAL = (90, 226, 220, 255)
WHITE_FULL = (255, 255, 255, 255)
WHITE_85 = (255, 255, 255, 217)
WHITE_70 = (255, 255, 255, 178)
WHITE_60 = (255, 255, 255, 153)
INK = (26, 26, 46, 255)
INK_BODY = (28, 28, 28, 255)
EYEBROW_DARK = (91, 91, 122, 255)
ANSWER_BG = (255, 255, 255, 247)
SHADOW_COLOR = (0, 0, 0, 38)

# Layout
MARGIN_PX = 64
PADDING_ANSWER = 48
CORNER_R = 24
SHADOW_BLUR = 24
SHADOW_OFFSET_Y = 8

# Fontes
FONTS_DIR = Path(os.environ.get("QA_FONTS_DIR", "/opt/MAIA/assets/fonts"))
FONT_HEADING_PATH = str(FONTS_DIR / "plus_jakarta" / "PlusJakartaSans-ExtraBold.ttf")
FONT_HEADING_BOLD_PATH = str(FONTS_DIR / "plus_jakarta" / "PlusJakartaSans-Bold.ttf")
FONT_BODY_VAR_PATH = str(FONTS_DIR / "inter" / "Inter-Variable.ttf")
FONT_MONO_VAR_PATH = str(FONTS_DIR / "jetbrains_mono" / "JetBrainsMono-Variable.ttf")
FONT_FALLBACK_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_FALLBACK_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_FALLBACK_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def _load_inter(weight, size):
    try:
        f = ImageFont.truetype(FONT_BODY_VAR_PATH, size)
        f.set_variation_by_name(weight)
        return f
    except Exception:
        path = FONT_FALLBACK_BOLD if weight in ("Bold", "ExtraBold", "Black") else FONT_FALLBACK_REG
        return ImageFont.truetype(path, size)


def _load_jetbrains(weight, size):
    try:
        f = ImageFont.truetype(FONT_MONO_VAR_PATH, size)
        f.set_variation_by_name(weight)
        return f
    except Exception:
        return ImageFont.truetype(FONT_FALLBACK_MONO, size)


def _load_jakarta(static_path, size):
    try:
        return ImageFont.truetype(static_path, size)
    except Exception:
        return ImageFont.truetype(FONT_FALLBACK_BOLD, size)


def load_fonts():
    return {
        "story_q": _load_jakarta(FONT_HEADING_PATH, 78),
        "story_a_lead": _load_inter("SemiBold", 44),
        "story_a_body": _load_inter("Regular", 42),
        "story_a_bold": _load_inter("Bold", 42),
        "feed_q": _load_jakarta(FONT_HEADING_PATH, 88),
        "ans_lead": _load_inter("SemiBold", 56),
        "ans_body": _load_inter("Regular", 50),
        "ans_bold": _load_inter("Bold", 50),
        "capa_kicker": _load_inter("SemiBold", 36),
        "capa_titulo": _load_jakarta(FONT_HEADING_PATH, 132),
        "capa_data": _load_inter("Medium", 44),
        "capa_tagline": _load_inter("Regular", 40),
        "capa_arrow": _load_inter("Bold", 32),
        "cta_kicker": _load_inter("SemiBold", 36),
        "cta_titulo": _load_jakarta(FONT_HEADING_BOLD_PATH, 96),
        "cta_destaque": _load_jakarta(FONT_HEADING_PATH, 88),
        "cta_link": _load_inter("SemiBold", 44),
        "eyebrow": _load_inter("Medium", 36),
        "ans_eyebrow": _load_inter("Medium", 32),
        "handle": _load_inter("SemiBold", 30),
        "tagline": _load_inter("Medium", 26),
        "num_mono": _load_jetbrains("Medium", 32),
    }


def fit_photo(photo, target_w, target_h):
    photo = photo.convert("RGBA")
    src_ratio = photo.width / photo.height
    tgt_ratio = target_w / target_h
    if src_ratio > tgt_ratio:
        new_h = target_h
        new_w = int(target_h * src_ratio)
    else:
        new_w = target_w
        new_h = int(target_w / src_ratio)
    photo = photo.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top_crop = (new_h - target_h) // 2
    return photo.crop((left, top_crop, left + target_w, top_crop + target_h))


def add_gradient(canvas, start_ratio=0.50, max_alpha=191, direction="bottom"):
    w, h = canvas.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    if direction == "bottom":
        start_y = int(h * start_ratio)
        end_y = h
        for y in range(start_y, end_y):
            t = (y - start_y) / max(1, end_y - start_y)
            alpha = int(max_alpha * (t ** 0.7))
            draw.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
    else:
        end_y = int(h * start_ratio)
        for y in range(0, end_y):
            t = 1 - (y / max(1, end_y))
            alpha = int(max_alpha * (t ** 0.7))
            draw.line([(0, y), (w, y)], fill=(0, 0, 0, alpha))
    return Image.alpha_composite(canvas, overlay)


def draw_text_with_tracking(draw, xy, text, font, fill, tracking=0):
    x, y = xy
    if tracking == 0:
        draw.text((x, y), text, font=font, fill=fill)
        return
    cursor_x = x
    for ch in text:
        draw.text((cursor_x, y), ch, font=font, fill=fill)
        bbox = font.getbbox(ch)
        cursor_x += (bbox[2] - bbox[0]) + tracking


def measure_text_with_tracking(text, font, tracking=0):
    if not text:
        return 0
    if tracking == 0:
        bbox = font.getbbox(text)
        return bbox[2] - bbox[0]
    total = 0
    for ch in text:
        bbox = font.getbbox(ch)
        total += (bbox[2] - bbox[0]) + tracking
    return total - tracking


def wrap_text_to_width(text, font, max_width):
    words = text.split()
    if not words:
        return []
    lines = []
    cur = words[0]
    for w in words[1:]:
        test = cur + " " + w
        bbox = font.getbbox(test)
        if (bbox[2] - bbox[0]) <= max_width:
            cur = test
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def add_card_shadow(canvas, rect):
    x0, y0, x1, y1 = rect
    w, h = canvas.size
    shadow_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow_layer)
    sd.rounded_rectangle(
        [x0, y0 + SHADOW_OFFSET_Y, x1, y1 + SHADOW_OFFSET_Y],
        radius=CORNER_R, fill=SHADOW_COLOR,
    )
    shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=SHADOW_BLUR))
    return Image.alpha_composite(canvas, shadow_layer)


def render_answer_paragraph(draw, text, highlights, x, y, max_width,
                            font_lead, font_reg, font_bold,
                            color_lead=INK, color_body=INK_BODY, color_bold=INK):
    # Remove markdown bold (**texto**) deixado pelo Gemini -- destaques
    # ja vem em lista separada, asteriscos viram lixo visual.
    text = re.sub(r"\*+", "", text or "")
    m = re.search(r"[\.!?](?:\s|$)", text)
    if m:
        lead_end = m.end()
        lead = text[:lead_end].strip()
        rest = text[lead_end:].strip()
    else:
        lead = text.strip()
        rest = ""

    cursor_y = y
    if lead:
        line_h_lead = int(font_lead.size * 1.32)
        for line in wrap_text_to_width(lead, font_lead, max_width):
            draw.text((x, cursor_y), line, font=font_lead, fill=color_lead)
            cursor_y += line_h_lead
        cursor_y += int(font_lead.size * 0.25)

    if rest:
        line_h = int(font_reg.size * 1.45)
        cursor_x = x
        cursor_y_body = cursor_y
        words = rest.split()
        norm_h = [h.lower().strip() for h in (highlights or []) if h]
        for word in words:
            clean = re.sub(r"[^\wÀ-ÿ]+", "", word).lower()
            is_bold = any(h and (h in clean or clean in h) for h in norm_h)
            f = font_bold if is_bold else font_reg
            color = color_bold if is_bold else color_body
            bbox = f.getbbox(word + " ")
            word_w = bbox[2] - bbox[0]
            if cursor_x + word_w > x + max_width and cursor_x > x:
                cursor_x = x
                cursor_y_body += line_h
            draw.text((cursor_x, cursor_y_body), word + " ", font=f, fill=color)
            cursor_x += word_w
        cursor_y = cursor_y_body + line_h

    return cursor_y


def measure_answer_paragraph(text, highlights, max_width, font_lead, font_reg, font_bold):
    dummy = Image.new("RGBA", (max_width + 200, 4000), (0, 0, 0, 0))
    dummy_draw = ImageDraw.Draw(dummy)
    return render_answer_paragraph(
        dummy_draw, text, highlights, 0, 0, max_width,
        font_lead, font_reg, font_bold,
    )


# STORIES Q+A
def compose_stories_qa(pergunta, resposta, destaques, foto_path,
                       num_q, total_q=5,
                       handle=footer_handle()):
    W, H = STORIES_SIZE
    fonts = load_fonts()

    photo = Image.open(foto_path)
    canvas = fit_photo(photo, W, H)
    canvas = add_gradient(canvas, start_ratio=0.32, max_alpha=219, direction="bottom")
    draw = ImageDraw.Draw(canvas)

    eyebrow_text = f"PERGUNTA {num_q:02d} / {total_q:02d}"
    draw_text_with_tracking(
        draw, (MARGIN_PX, 80), eyebrow_text,
        fonts["eyebrow"], WHITE_85, tracking=4,
    )
    handle_w = measure_text_with_tracking(handle, fonts["handle"], tracking=2)
    draw_text_with_tracking(
        draw, (W - MARGIN_PX - handle_w, 84), handle,
        fonts["handle"], WHITE_70, tracking=2,
    )

    text_max_w = W - 2 * MARGIN_PX
    q_font = fonts["story_q"]
    q_lines = wrap_text_to_width(pergunta, q_font, text_max_w)[:4]
    line_h_q = int(q_font.size * 1.08)
    q_y = 820
    for line in q_lines:
        draw.text((MARGIN_PX, q_y), line, font=q_font, fill=WHITE_FULL)
        q_y += line_h_q

    sep_y = q_y + 24
    draw.line([(MARGIN_PX, sep_y), (MARGIN_PX + 120, sep_y)],
              fill=ACCENT_TEAL, width=4)

    resp_y = sep_y + 48
    render_answer_paragraph(
        draw, resposta, destaques, MARGIN_PX, resp_y, text_max_w,
        fonts["story_a_lead"], fonts["story_a_body"], fonts["story_a_bold"],
        color_lead=WHITE_FULL, color_body=WHITE_85, color_bold=ACCENT_TEAL,
    )

    footer_y = 1830
    draw_text_with_tracking(
        draw, (MARGIN_PX, footer_y), handle,
        fonts["handle"], WHITE_85, tracking=2,
    )
    tag = brand_name().upper()
    tag_w = measure_text_with_tracking(tag, fonts["tagline"], tracking=8)
    draw_text_with_tracking(
        draw, (W - MARGIN_PX - tag_w, footer_y + 4), tag,
        fonts["tagline"], WHITE_60, tracking=8,
    )

    return canvas


# FEED PERGUNTA
def compose_feed_pergunta(pergunta, foto_path, num_q, total_q=4,
                          handle=footer_handle()):
    W, H = FEED_SIZE
    fonts = load_fonts()

    photo = Image.open(foto_path)
    canvas = fit_photo(photo, W, H)
    canvas = add_gradient(canvas, start_ratio=0.30, max_alpha=224, direction="bottom")
    draw = ImageDraw.Draw(canvas)

    eyebrow_text = f"PERGUNTA {num_q:02d} / {total_q:02d}"
    draw_text_with_tracking(
        draw, (MARGIN_PX, 70), eyebrow_text,
        fonts["eyebrow"], WHITE_85, tracking=4,
    )

    text_max_w = W - 2 * MARGIN_PX
    q_font = fonts["feed_q"]
    q_lines = wrap_text_to_width(pergunta, q_font, text_max_w)[:4]
    line_h_q = int(q_font.size * 1.08)
    q_y = 720
    for line in q_lines:
        draw.text((MARGIN_PX, q_y), line, font=q_font, fill=WHITE_FULL)
        q_y += line_h_q

    sep_y = q_y + 16
    draw.line([(MARGIN_PX, sep_y), (MARGIN_PX + 100, sep_y)],
              fill=ACCENT_TEAL, width=4)
    proxima_label = "RESPOSTA NO PROXIMO  ->"
    draw_text_with_tracking(
        draw, (MARGIN_PX, sep_y + 32), proxima_label,
        fonts["eyebrow"], ACCENT_TEAL, tracking=4,
    )

    footer_y = 1290
    draw_text_with_tracking(
        draw, (MARGIN_PX, footer_y), handle,
        fonts["handle"], WHITE_85, tracking=2,
    )
    num_text = f"{2 * num_q:02d} / 10"
    num_w = measure_text_with_tracking(num_text, fonts["num_mono"], tracking=2)
    draw_text_with_tracking(
        draw, (W - MARGIN_PX - num_w, footer_y), num_text,
        fonts["num_mono"], WHITE_70, tracking=2,
    )

    return canvas


# FEED RESPOSTA
def compose_feed_resposta(resposta, destaques, foto_path, num_q, total_q=4,
                          handle=footer_handle()):
    W, H = FEED_SIZE
    fonts = load_fonts()

    photo = Image.open(foto_path)
    canvas = fit_photo(photo, W, H)

    card_x0 = MARGIN_PX
    card_x1 = W - MARGIN_PX
    inner_w = card_x1 - card_x0 - 2 * PADDING_ANSWER

    eyebrow_text = f"RESPOSTA {num_q:02d}"
    eyebrow_h = fonts["ans_eyebrow"].size + 4
    eyebrow_gap = 28

    body_h = measure_answer_paragraph(
        resposta, destaques, inner_w,
        fonts["ans_lead"], fonts["ans_body"], fonts["ans_bold"],
    )

    card_inner_h = eyebrow_h + eyebrow_gap + body_h
    card_h = card_inner_h + 2 * PADDING_ANSWER

    bottom_safe = H - 100
    card_y1 = bottom_safe
    card_y0 = card_y1 - card_h
    if card_y0 < 600:
        card_y0 = 600
        card_y1 = card_y0 + card_h

    canvas = add_card_shadow(canvas, (card_x0, card_y0, card_x1, card_y1))
    draw = ImageDraw.Draw(canvas)

    draw.rounded_rectangle(
        [card_x0, card_y0, card_x1, card_y1],
        radius=CORNER_R, fill=ANSWER_BG,
    )

    draw_text_with_tracking(
        draw, (card_x0 + PADDING_ANSWER, card_y0 + PADDING_ANSWER),
        eyebrow_text, fonts["ans_eyebrow"], EYEBROW_DARK, tracking=4,
    )

    body_x = card_x0 + PADDING_ANSWER
    body_y = card_y0 + PADDING_ANSWER + eyebrow_h + eyebrow_gap
    render_answer_paragraph(
        draw, resposta, destaques, body_x, body_y, inner_w,
        fonts["ans_lead"], fonts["ans_body"], fonts["ans_bold"],
        color_lead=INK, color_body=INK_BODY, color_bold=INK,
    )

    footer_y = 1290
    draw_text_with_tracking(
        draw, (MARGIN_PX, footer_y), handle,
        fonts["handle"], INK, tracking=2,
    )
    num_text = f"{2 * num_q + 1:02d} / 10"
    num_w = measure_text_with_tracking(num_text, fonts["num_mono"], tracking=2)
    draw_text_with_tracking(
        draw, (W - MARGIN_PX - num_w, footer_y), num_text,
        fonts["num_mono"], INK, tracking=2,
    )

    return canvas


# FEED CAPA
def compose_feed_capa(titulo_imersao, data, tagline,
                      handle=footer_handle()):
    """Capa minimalista: APENAS a headline (tagline) dominando o card.
    Os parametros titulo_imersao e data sao aceitos por compatibilidade do
    pipeline mas NAO sao desenhados (movidos pro CTA, card 10).
    """
    W, H = FEED_SIZE
    fonts = load_fonts()

    canvas = Image.new("RGBA", (W, H), BG_DARK)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(0, H):
        t = y / H
        r = int(20 + (4 - 20) * t)
        g = int(40 + (4 - 40) * t)
        b = int(80 + (12 - 80) * t)
        od.line([(0, y), (W, y)], fill=(r, g, b, 90))
    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    # Hairline acento topo (ancora visual + respiro)
    draw.line([(MARGIN_PX, 130), (MARGIN_PX + 160, 130)],
              fill=ACCENT_TEAL, width=4)

    # HEADLINE DOMINA O CARD: auto-fit pra caber em ate 5 linhas, ate 150pt.
    text_max_w = W - 2 * MARGIN_PX
    headline_text = (tagline or "").strip()

    chosen_size = 96
    chosen_lines = []
    chosen_font = None
    area_y0 = 210
    area_y1 = 1180
    area_h = area_y1 - area_y0
    for trial_size in (150, 140, 130, 120, 110, 100, 92, 84):
        trial_font = _load_jakarta(FONT_HEADING_PATH, trial_size)
        trial_lines = wrap_text_to_width(headline_text, trial_font, text_max_w)
        line_h = int(trial_size * 1.0)
        total_h = line_h * len(trial_lines)
        if len(trial_lines) <= 5 and total_h <= area_h:
            chosen_size = trial_size
            chosen_lines = trial_lines
            chosen_font = trial_font
            break
    if chosen_font is None:
        chosen_size = 84
        chosen_font = _load_jakarta(FONT_HEADING_PATH, chosen_size)
        chosen_lines = wrap_text_to_width(headline_text, chosen_font, text_max_w)[:5]

    line_h = int(chosen_size * 1.0)
    headline_h = line_h * len(chosen_lines)
    y_start = area_y0 + (area_h - headline_h) // 2
    cy = y_start
    for line in chosen_lines:
        draw.text((MARGIN_PX, cy), line, font=chosen_font, fill=WHITE_FULL)
        cy += line_h

    # Footer: setinha ARRASTE + numeracao
    footer_y = 1230
    arrow_text = "ARRASTE  ->"
    draw_text_with_tracking(
        draw, (MARGIN_PX, footer_y), arrow_text,
        fonts["capa_arrow"], ACCENT_TEAL, tracking=8,
    )
    num_text = "01 / 10"
    num_w = measure_text_with_tracking(num_text, fonts["num_mono"], tracking=2)
    draw_text_with_tracking(
        draw, (W - MARGIN_PX - num_w, footer_y), num_text,
        fonts["num_mono"], WHITE_60, tracking=2,
    )

    return canvas


# FEED CTA
def compose_feed_cta(titulo_imersao, data, link_bio_text,
                     handle=footer_handle()):
    W, H = FEED_SIZE
    fonts = load_fonts()

    canvas = Image.new("RGBA", (W, H), BG_DARKER)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    for y in range(0, H):
        t = y / H
        r = int(8 + (24 - 8) * (1 - abs(2 * t - 1)))
        g = int(12 + (40 - 12) * (1 - abs(2 * t - 1)))
        b = int(28 + (90 - 28) * (1 - abs(2 * t - 1)))
        od.line([(0, y), (W, y)], fill=(r, g, b, 110))
    canvas = Image.alpha_composite(canvas, overlay)
    draw = ImageDraw.Draw(canvas)

    kicker = "PROXIMA EDICAO"
    draw_text_with_tracking(
        draw, (MARGIN_PX, 130), kicker,
        fonts["cta_kicker"], ACCENT_TEAL, tracking=6,
    )
    draw.line([(MARGIN_PX, 190), (MARGIN_PX + 160, 190)],
              fill=ACCENT_TEAL, width=4)

    titulo_font = fonts["cta_titulo"]
    text_max_w = W - 2 * MARGIN_PX
    titulo_lines = wrap_text_to_width(titulo_imersao, titulo_font, text_max_w)
    line_h_t = int(titulo_font.size * 1.0)
    titulo_y = 250
    cy = titulo_y
    for line in titulo_lines:
        draw.text((MARGIN_PX, cy), line, font=titulo_font, fill=WHITE_FULL)
        cy += line_h_t

    data_font = fonts["cta_destaque"]
    data_y = cy + 50
    draw.text((MARGIN_PX, data_y), data, font=data_font, fill=ACCENT_TEAL)

    link_y = data_y + int(data_font.size * 1.1) + 80
    instr = "GARANTA SUA VAGA"
    draw_text_with_tracking(
        draw, (MARGIN_PX, link_y), instr,
        fonts["cta_kicker"], WHITE_70, tracking=6,
    )
    draw.text(
        (MARGIN_PX, link_y + 60), link_bio_text,
        font=fonts["cta_link"], fill=WHITE_FULL,
    )

    footer_y = 1240
    arrow = "TOQUE NO @ PRA IR AO PERFIL  ^"
    draw_text_with_tracking(
        draw, (MARGIN_PX, footer_y), arrow,
        fonts["capa_arrow"], ACCENT_TEAL, tracking=8,
    )
    handle_y = footer_y + 50
    draw_text_with_tracking(
        draw, (MARGIN_PX, handle_y), handle,
        fonts["handle"], WHITE_FULL, tracking=2,
    )
    num_text = "10 / 10"
    num_w = measure_text_with_tracking(num_text, fonts["num_mono"], tracking=2)
    draw_text_with_tracking(
        draw, (W - MARGIN_PX - num_w, footer_y), num_text,
        fonts["num_mono"], WHITE_60, tracking=2,
    )

    return canvas


def save_png(canvas, output_path):
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path, "PNG", quality=95)
    print(f"  OK: {output_path}")
