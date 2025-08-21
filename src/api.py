# src/api.py
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")

from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, File, UploadFile, Query, Body, HTTPException
from pydantic import RootModel
from PIL import Image
import pytesseract
import os

from src.ocr import extract_and_clean, clean_text
from src.summarizer import summarize_texts
from src.db import init_db, save_digest, fetch_digest

# Ensure Tesseract binary path for macOS (adjust if needed: run `which tesseract`)
pytesseract.pytesseract.tesseract_cmd = "/usr/local/bin/tesseract"

# ----- Lifespan (replaces deprecated on_event) -----
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()             # create SQLite tables on startup
    yield                  # (optional) teardown goes after this

app = FastAPI(title="Instagram Inspo Digest API", lifespan=lifespan)

# Pydantic v2 RootModel: POST body is just a raw list of strings
class ImageURLs(RootModel[List[str]]):
    pass

# ----- Routes -----
@app.get("/")
def root():
    return {"message": "🚀 Instagram Inspo Digest API is running!"}

# OCR via URL
@app.get("/ocr")
def ocr_endpoint(url: str = Query(..., description="Image URL to OCR")):
    try:
        text = extract_and_clean(url)
        return {"url": url, "extracted_text": text}
    except Exception as e:
        # Surface the reason (e.g., not an image / HTML page / decode error)
        raise HTTPException(status_code=400, detail=str(e))

# OCR via upload
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

# Digest: OCR + summarize + save
@app.post("/digest")
async def digest_endpoint(urls: ImageURLs):
    url_list = urls.root
    texts, errors = [], {}

    for u in url_list:
        try:
            t = extract_and_clean(u)
            if t and not t.startswith("[OCR_ERROR]"):
                texts.append(t)
            else:
                errors[u] = t or "Empty OCR result"
        except Exception as e:
            errors[u] = str(e)

    if not texts:
        raise HTTPException(status_code=400, detail={"message":"No valid images to summarize","errors":errors})

    digest = summarize_texts(texts)
    digest_id = save_digest(url_list, digest)
    return {"id": digest_id, "digest": digest, "sources": texts, "errors": errors}

# Retrieve digest by ID
@app.get("/digest/{digest_id}")
def get_digest(digest_id: int):
    row = fetch_digest(digest_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Digest not found")
    urls_str, digest = row
    return {"id": digest_id, "urls": urls_str.split(","), "digest": digest}
