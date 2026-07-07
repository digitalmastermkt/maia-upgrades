"""
compose_card.py - Composicao de cards Instagram Q&A
Tipografia oficial Juliana (TYPOGRAPHY_GUIDELINES.md v1.0, 2026-04-30):

  Plus Jakarta Sans  -> headlines (perguntas)
  Inter              -> corpo (respostas + UI)
  JetBrains Mono     -> numeracao monoespacada
"""
import json
import argparse
import os
import re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys
sys.path.insert(0, "/opt/MAIA")
from brand_loader import footer_handle, brand_name, slogan_or_blank, website_or_blank, owner_name, get, colors

# ====================================================================
STORIES_SIZE = (1080, 1920)
FEED_SIZE = (1080, 1350)

# Cores
STICKER_BG = (26, 26, 46, 250)
STICKER_CAT_COLOR = (255, 255, 255, 217)
STICKER_Q_COLOR = (255, 255, 255, 255)
ANSWER_BG = (255, 255, 255, 247)
ANSWER_TEXT = (28, 28, 28, 255)
ANSWER_LEAD = (26, 26, 46, 255)
ANSWER_EYEBROW = (91, 91, 122, 255)
HANDLE_DARK = (26, 26, 46, 255)
HANDLE_LIGHT = (255, 255, 255, 217)
TAGLINE_LIGHT = (255, 255, 255, 166)
SHADOW_COLOR = (0, 0, 0, 38)

# Layout (Juliana)
MARGIN_PX = 64
PADDING_STICKER = 40
PADDING_ANSWER = 48
GAP = 32
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
        "q_stories": _load_jakarta(FONT_HEADING_PATH, 96),
        "q_feed": _load_jakarta(FONT_HEADING_BOLD_PATH, 72),
        "ans_body": _load_inter("Regular", 56),
        "ans_bold": _load_inter("Bold", 56),
        "ans_lead": _load_inter("SemiBold", 60),
        "ans_eyebrow": _load_inter("Medium", 32),
        "eyebrow": _load_inter("Medium", 36),
        "handle": _load_inter("SemiBold", 30),
        "tagline": _load_inter("Medium", 26),
        "cta": _load_inter("Bold", 32),
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


def add_gradient_bottom(canvas, start_ratio=0.50, max_alpha=191):
    w, h = canvas.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    start_y = int(h * start_ratio)
    if start_y >= h:
        return canvas
    for y in range(start_y, h):
        t = (y - start_y) / max(1, h - start_y)
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


def render_answer_body(draw, text, highlights, x, y, max_width, fonts):
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
        font_lead = fonts["ans_lead"]
        line_h_lead = int(font_lead.size * 1.4)
        for line in wrap_text_to_width(lead, font_lead, max_width):
            draw.text((x, cursor_y), line, font=font_lead, fill=ANSWER_LEAD)
            cursor_y += line_h_lead
        cursor_y += int(font_lead.size * 0.30)

    if rest:
        font_reg = fonts["ans_body"]
        font_bold = fonts["ans_bold"]
        line_h = int(font_reg.size * 1.5)
        cursor_x = x
        cursor_y_body = cursor_y
        words = rest.split()
        norm_highlights = [h.lower().strip() for h in (highlights or []) if h]
        for word in words:
            clean = re.sub(r"[^\wÀ-ÿ]+", "", word).lower()
            is_bold = any(h and (h in clean or clean in h) for h in norm_highlights)
            f = font_bold if is_bold else font_reg
            color = ANSWER_LEAD if is_bold else ANSWER_TEXT
            bbox = f.getbbox(word + " ")
            word_w = bbox[2] - bbox[0]
            if cursor_x + word_w > x + max_width and cursor_x > x:
                cursor_x = x
                cursor_y_body += line_h
            draw.text((cursor_x, cursor_y_body), word + " ", font=f, fill=color)
            cursor_x += word_w
        cursor_y = cursor_y_body + line_h

    return cursor_y


def measure_answer_body(text, highlights, max_width, fonts):
    dummy = Image.new("RGBA", (max_width + 200, 4000), (0, 0, 0, 0))
    dummy_draw = ImageDraw.Draw(dummy)
    return render_answer_body(dummy_draw, text, highlights, 0, 0, max_width, fonts)


def compose_card(photo_path, face_box, card_data, format_type, output_path,
                 card_index=1, total_cards=10,
                 handle=footer_handle(),
                 show_tagline=False, show_arrow=False):
    canvas_size = STORIES_SIZE if format_type == "stories" else FEED_SIZE
    W, H = canvas_size
    fonts = load_fonts()

    pergunta = card_data.get("pergunta", "")
    resposta = card_data.get("resposta", "")
    destaques = card_data.get("destaques", []) or []

    photo = Image.open(photo_path)
    canvas = fit_photo(photo, W, H)

    if format_type == "stories":
        canvas = _compose_stories(canvas, W, H, pergunta, fonts,
                                  card_index, total_cards, handle,
                                  show_tagline, show_arrow, face_box)
    else:
        canvas = _compose_feed(canvas, W, H, resposta, destaques, fonts,
                               card_index, total_cards, handle,
                               show_tagline, face_box)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path, "PNG", quality=95)
    print(f"  OK {format_type}: {output_path}")


def _compose_stories(canvas, W, H, pergunta, fonts, idx, total, handle,
                     show_tagline, show_arrow, face_box):
    canvas = add_gradient_bottom(canvas, start_ratio=0.50, max_alpha=191)
    draw = ImageDraw.Draw(canvas)

    eyebrow_text = f"PERGUNTA {idx:02d} / {total:02d}"
    draw_text_with_tracking(
        draw, (MARGIN_PX, 1180), eyebrow_text,
        fonts["eyebrow"], STICKER_CAT_COLOR, tracking=4,
    )

    q_font = fonts["q_stories"]
    text_max_w = W - 2 * MARGIN_PX
    q_lines = wrap_text_to_width(pergunta, q_font, text_max_w)[:4]
    line_h = int(q_font.size * 1.08)
    q_y = 1280
    for line in q_lines:
        draw.text((MARGIN_PX, q_y), line, font=q_font, fill=STICKER_Q_COLOR)
        q_y += line_h

    handle_y = 1830
    draw_text_with_tracking(
        draw, (MARGIN_PX, handle_y), handle,
        fonts["handle"], HANDLE_LIGHT, tracking=2,
    )

    if show_arrow:
        cta_text = "ARRASTE >"
        cta_w = measure_text_with_tracking(cta_text, fonts["cta"], tracking=12)
        draw_text_with_tracking(
            draw, (W - MARGIN_PX - cta_w, handle_y), cta_text,
            fonts["cta"], (255, 255, 255, 255), tracking=12,
        )
    elif show_tagline:
        tag_text = brand_name().upper()
        tag_w = measure_text_with_tracking(tag_text, fonts["tagline"], tracking=8)
        draw_text_with_tracking(
            draw, (W - MARGIN_PX - tag_w, handle_y + 4), tag_text,
            fonts["tagline"], TAGLINE_LIGHT, tracking=8,
        )

    return canvas


def _compose_feed(canvas, W, H, resposta, destaques, fonts, idx, total,
                  handle, show_tagline, face_box):
    card_x0 = MARGIN_PX
    card_x1 = W - MARGIN_PX
    inner_w = card_x1 - card_x0 - 2 * PADDING_ANSWER

    eyebrow_text = f"RESPOSTA {idx:02d}"
    eyebrow_h = fonts["ans_eyebrow"].size + 4
    eyebrow_gap = 32

    body_h = measure_answer_body(resposta, destaques, inner_w, fonts)

    card_inner_h = eyebrow_h + eyebrow_gap + body_h
    card_h = card_inner_h + 2 * PADDING_ANSWER
    card_y0 = 720
    card_y1 = card_y0 + card_h

    bottom_safe = H - 100
    if card_y1 > bottom_safe:
        overshoot = card_y1 - bottom_safe
        card_y0 = max(700, card_y0 - overshoot)
        card_y1 = card_y0 + card_h

    canvas = add_card_shadow(canvas, (card_x0, card_y0, card_x1, card_y1))
    draw = ImageDraw.Draw(canvas)

    draw.rounded_rectangle(
        [card_x0, card_y0, card_x1, card_y1],
        radius=CORNER_R, fill=ANSWER_BG,
    )

    draw_text_with_tracking(
        draw, (card_x0 + PADDING_ANSWER, card_y0 + PADDING_ANSWER),
        eyebrow_text, fonts["ans_eyebrow"], ANSWER_EYEBROW, tracking=4,
    )

    body_x = card_x0 + PADDING_ANSWER
    body_y = card_y0 + PADDING_ANSWER + eyebrow_h + eyebrow_gap
    render_answer_body(draw, resposta, destaques, body_x, body_y,
                       inner_w, fonts)

    footer_y = 1290
    draw_text_with_tracking(
        draw, (MARGIN_PX, footer_y), handle,
        fonts["handle"], HANDLE_DARK, tracking=2,
    )

    num_text = f"{idx:02d} / {total:02d}"
    num_w = measure_text_with_tracking(num_text, fonts["num_mono"], tracking=2)
    draw_text_with_tracking(
        draw, (W - MARGIN_PX - num_w, footer_y), num_text,
        fonts["num_mono"], HANDLE_DARK, tracking=2,
    )

    if show_tagline:
        tag_text = brand_name().upper()
        tag_w = measure_text_with_tracking(tag_text, fonts["tagline"], tracking=8)
        draw_text_with_tracking(
            draw, (W - MARGIN_PX - tag_w, footer_y - 38), tag_text,
            fonts["tagline"], (91, 91, 122, 200), tracking=8,
        )

    return canvas


def main():
    parser = argparse.ArgumentParser(description="Compoe card Instagram Q&A")
    parser.add_argument("photo")
    parser.add_argument("face_json")
    parser.add_argument("card_json")
    parser.add_argument("format", choices=["stories", "feed"])
    parser.add_argument("output")
    parser.add_argument("--idx", type=int, default=1)
    parser.add_argument("--total", type=int, default=10)
    parser.add_argument("--handle", default=footer_handle())
    parser.add_argument("--show-tagline", action="store_true")
    parser.add_argument("--show-arrow", action="store_true")
    args = parser.parse_args()

    with open(args.face_json) as f:
        face_box = json.load(f)
    with open(args.card_json) as f:
        card_data = json.load(f)

    compose_card(
        args.photo, face_box, card_data, args.format, args.output,
        card_index=args.idx, total_cards=args.total,
        handle=args.handle, show_tagline=args.show_tagline,
        show_arrow=args.show_arrow,
    )


if __name__ == "__main__":
    main()
