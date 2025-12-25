# src/card.py
from PIL import Image, ImageDraw, ImageFont
import os
import textwrap

CANVAS_SIZE = (1080, 1350)
TEXT_COLOR = (0, 0, 0)

ASSETS_DIR = "src/assets"
TEMPLATES = {
    "A": os.path.join(ASSETS_DIR, "template A.png"),
    "B": os.path.join(ASSETS_DIR, "template B.png"),
}

FONT_PATH = os.path.join(ASSETS_DIR, "SourceSerifPro-Regular.ttf")
FONT_SIZE = 64

OUTPUT_DIR = "cards"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def render_quote_card(text: str, out_path: str, template: str = "A") -> str:
    if template not in TEMPLATES:
        raise ValueError("Invalid template")

    img = Image.open(TEMPLATES[template]).convert("RGB")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    except Exception:
        font = ImageFont.load_default()

    wrapped = textwrap.fill(text, width=28)

    bbox = draw.multiline_textbbox(
        (0, 0),
        wrapped,
        font=font,
        spacing=14,
        align="center"
    )

    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]

    x = (CANVAS_SIZE[0] - w) // 2
    y = (CANVAS_SIZE[1] - h) // 2

    draw.multiline_text(
        (x, y),
        wrapped,
        fill=TEXT_COLOR,
        font=font,
        align="center",
        spacing=14
    )

    img.save(out_path)
    return out_path
