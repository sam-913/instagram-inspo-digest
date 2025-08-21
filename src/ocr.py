from PIL import Image
import pytesseract
import requests
from io import BytesIO
import re

# common headers
UA = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0 Safari/537.36"
    )
}

def extract_text_from_url(img_url: str, lang: str = "eng") -> str:
    """
    Fetch image from a URL (with UA + referer headers),
    OCR it via Tesseract, return cleaned text.
    """
    try:
        resp = requests.get(
            img_url,
            timeout=20,
            headers={**UA, "Referer": "https://www.pinterest.com/"},
            allow_redirects=True,
        )
        resp.raise_for_status()

        if not resp.headers.get("Content-Type", "").startswith("image/"):
            return f"[OCR_ERROR]: URL did not return an image (got {resp.headers.get('Content-Type')})"

        img = Image.open(BytesIO(resp.content))
        text = pytesseract.image_to_string(img, lang=lang)
        return text.strip()
    except Exception as e:
        return f"[OCR_ERROR]: {e}"

def clean_text(text: str) -> str:
    if not text:
        return ""
    # remove emojis & weird unicode
    text = text.encode("ascii", "ignore").decode()
    # remove hashtags & mentions
    text = re.sub(r"[@#]\w+", "", text)
    # remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)
    # normalize whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

def extract_and_clean(img_url: str, lang: str = "eng") -> str:
    """Convenience wrapper for OCR + cleaning."""
    raw = extract_text_from_url(img_url, lang)
    return clean_text(raw)

# at top
from src.db import get_cached_ocr, set_cached_ocr

def extract_and_clean(img_url: str, lang: str = "eng") -> str:
    # 1) cache check
    cached = get_cached_ocr(img_url)
    if cached:
        return clean_text(cached)

    # 2) do OCR
    raw = extract_text_from_url(img_url, lang=lang)

    # 3) cache the raw OCR (store pre-clean so you can re-clean differently later if needed)
    if raw and not raw.startswith("[OCR_ERROR]"):
        set_cached_ocr(img_url, raw)

    # 4) return cleaned text
    return clean_text(raw)