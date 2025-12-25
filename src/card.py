# src/card.py
from PIL import Image, ImageDraw, ImageFont
import textwrap
import os

CANVAS_SIZE = (1080, 1350)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
FONT_PATH = os.path.join(ASSETS_DIR, "SourceSerifPro-Regular.ttf")

TEXT_COLOR = (0, 0, 0)
START_FONT_SIZE = 64
MIN_FONT_SIZE = 36
LINE_SPACING = 10
MAX_CHARS_PER_LINE = 28


def _fit_font(draw, text, font_path, max_width, max_height):
    """Reduce font size until text fits"""
    font_size = START_FONT_SIZE

    while font_size >= MIN_FONT_SIZE:
        font = ImageFont.truetype(font_path, font_size)
        wrapped = textwrap.fill(text, MAX_CHARS_PER_LINE)
        bbox = draw.multiline_textbbox(
            (0, 0),
            wrapped,
            font=font,
            spacing=LINE_SPACING,
            align="center",
        )
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]

        if w <= max_width and h <= max_height:
            return font, wrapped, w, h

        font_size -= 2

    return font, wrapped, w, h


def render_quote_card(
    text: str,
    template_name: str,
    out_path: str,
):
    template_path = os.path.join(ASSETS_DIR, template_name)

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    img = Image.open(template_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    max_text_width = int(CANVAS_SIZE[0] * 0.75)
    max_text_height = int(CANVAS_SIZE[1] * 0.45)

    font, wrapped, w, h = _fit_font(
        draw,
        text,
        FONT_PATH,
        max_text_width,
        max_text_height,
    )

    x = (CANVAS_SIZE[0] - w) // 2
    y = (CANVAS_SIZE[1] - h) // 2

    draw.multiline_text(
        (x, y),
        wrapped,
        fill=TEXT_COLOR,
        font=font,
        spacing=LINE_SPACING,
        align="center",
    )

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path)

    return out_path
