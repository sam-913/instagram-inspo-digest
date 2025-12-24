from PIL import Image, ImageDraw, ImageFont
import textwrap

CANVAS_SIZE = (1080, 1350)   # Instagram post size
FONT_PATH = "/System/Library/Fonts/Supplemental/Georgia.ttf"  # change if missing

def render_quote_card(quote: str, author: str = "", out_path: str = "card.png"):
    # Gradient background (simple vertical fade)
    img = Image.new("RGB", CANVAS_SIZE, (255, 255, 255))
    pixels = img.load()
    for y in range(CANVAS_SIZE[1]):
        r = int(120 + (255 - 120) * (y / CANVAS_SIZE[1]))
        g = int(80 + (180 - 80) * (y / CANVAS_SIZE[1]))
        b = int(150 + (200 - 150) * (y / CANVAS_SIZE[1]))
        for x in range(CANVAS_SIZE[0]):
            pixels[x, y] = (r, g, b)

    draw = ImageDraw.Draw(img)

    # Load fonts
    font = ImageFont.truetype(FONT_PATH, 64)
    author_font = ImageFont.truetype(FONT_PATH, 48)

    # Wrap text
    wrapped = textwrap.fill(quote, width=28)

    # Center quote
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=10, align="center")
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (CANVAS_SIZE[0] - w) // 2
    y = (CANVAS_SIZE[1] - h) // 2 - 100

    draw.multiline_text(
        (x, y),
        wrapped,
        font=font,
        fill=(255, 255, 255),
        align="center",
        spacing=10
    )

    # Author (optional)
    if author:
        text = f"— {author}"
        bbox2 = draw.textbbox((0, 0), text, font=author_font)
        w2, h2 = bbox2[2] - bbox2[0], bbox2[3] - bbox2[1]
        draw.text(
            ((CANVAS_SIZE[0] - w2) // 2, y + h + 60),
            text,
            font=author_font,
            fill=(230, 230, 230)
        )

    img.save(out_path)
    return out_path