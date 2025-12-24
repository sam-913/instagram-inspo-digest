# src/api.py
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, File, UploadFile, Query, HTTPException
from fastapi.responses import FileResponse
from pydantic import RootModel
from PIL import Image
import pytesseract
import os

from src.ocr import extract_and_clean, clean_text
from src.filters import ethical_check
from src.summarizer import summarize_texts
from src.db import init_db, save_digest, fetch_digest
from src.dedupe import dedupe_texts
from src.card import render_quote_card

# --- Tesseract path (macOS) ---
pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"


# --- Lifespan (DB init) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Instagram Inspo Digest API",
    lifespan=lifespan,
)

# --- Pydantic body model ---
class ImageURLs(RootModel[List[str]]):
    pass


# ---------------- ROUTES ---------------- #

@app.get("/")
def root():
    return {"message": "🚀 Instagram Inspo Digest API is running!"}


# --- OCR from URL ---
@app.get("/ocr")
def ocr_endpoint(url: str = Query(..., description="Image URL to OCR")):
    try:
        text = extract_and_clean(url)
        return {"url": url, "extracted_text": text}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- OCR from upload ---
@app.post("/ocr-upload")
async def ocr_upload(file: UploadFile = File(...)):
    try:
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        img = Image.open(temp_path)
        text = pytesseract.image_to_string(img)
        cleaned = clean_text(text)
        os.remove(temp_path)

        return {"filename": file.filename, "extracted_text": cleaned}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- DIGEST PIPELINE ---
@app.post("/digest")
async def digest_endpoint(urls: ImageURLs):
    results = []
    valid_texts = []

    # Step 1: OCR + Ethics
    for url in urls.root:
        entry = {
            "url": url,
            "text": None,
            "passed_ethics": False,
            "is_duplicate": False,
            "used_in_digest": False,
            "error": None,
        }

        try:
            raw = extract_and_clean(url)

            if not raw or raw.startswith("[OCR_ERROR]"):
                entry["error"] = raw or "Empty OCR result"
                results.append(entry)
                continue

            ok, reason = ethical_check(raw)
            entry["passed_ethics"] = ok

            if not ok:
                entry["error"] = f"Ethics filter: {reason}"
                results.append(entry)
                continue

            entry["text"] = raw
            valid_texts.append(raw)
            results.append(entry)

        except Exception as e:
            entry["error"] = str(e)
            results.append(entry)

    if not valid_texts:
        raise HTTPException(
            status_code=400,
            detail="No valid content after OCR and ethics filtering",
        )

    # Step 2: Deduplication
    uniq_texts, dropped = dedupe_texts(valid_texts, sim_threshold=0.90)

    for keep_idx, drop_idx, sim in dropped:
        dropped_text = valid_texts[drop_idx]
        for r in results:
            if r["text"] == dropped_text:
                r["is_duplicate"] = True
                r["error"] = f"Duplicate (similarity={round(sim,2)})"

    if not uniq_texts:
        raise HTTPException(
            status_code=400,
            detail="All texts were duplicates",
        )

    # Step 3: Summarize
    digest = summarize_texts(uniq_texts)
    digest_id = save_digest(urls.root, digest)

    for r in results:
        if r["text"] in uniq_texts:
            r["used_in_digest"] = True

    # Step 4: Return structured output
    return {
        "id": digest_id,
        "digest": digest,
        "items": results,
        "stats": {
            "input_urls": len(urls.root),
            "passed_ethics": sum(r["passed_ethics"] for r in results),
            "duplicates_removed": sum(r["is_duplicate"] for r in results),
            "used_in_digest": sum(r["used_in_digest"] for r in results),
            "errors": sum(1 for r in results if r["error"]),
        },
    }


# --- Retrieve digest ---
@app.get("/digest/{digest_id}")
def get_digest(digest_id: int):
    row = fetch_digest(digest_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Digest not found")

    urls_str, digest = row
    return {
        "id": digest_id,
        "urls": urls_str.split(","),
        "digest": digest,
    }


# --- Render Instagram-ready quote card ---
@app.get("/digest/{digest_id}/card")
def get_digest_card(digest_id: int):
    row = fetch_digest(digest_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Digest not found")

    _, digest = row
    out_path = f"card_{digest_id}.png"
    render_quote_card(digest, author="", out_path=out_path)

    return FileResponse(
        out_path,
        media_type="image/png",
        filename=out_path,
    )
