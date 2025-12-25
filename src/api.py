# src/api.py

import os
import uuid
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.db import init_db, save_digest, fetch_digest
from src.ocr import extract_and_clean
from src.summarizer import summarize_texts
from src.dedupe import dedupe_texts
from src.filters import ethical_check
from src.card import render_quote_card


# ---------- Lifespan ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Instagram Inspo Digest API", lifespan=lifespan)


# ---------- Models ----------
class DigestInput(BaseModel):
    urls: List[str]


class RenderRequest(BaseModel):
    digest_id: int


# ---------- Health ----------
@app.get("/")
def root():
    return {"status": "ok"}


# ---------- Step 1: Create Digest ----------
@app.post("/digest")
def create_digest(urls: List[str]):
    results = []
    approved_texts = []

    for idx, url in enumerate(urls):
        entry = {
            "index": idx,
            "url": url,
            "text": None,
            "passed_ethics": False,
            "used_in_digest": False,
            "error": None,
        }

        try:
            text = extract_and_clean(url)

            if not text:
                entry["error"] = "Empty OCR result"
                results.append(entry)
                continue

            ok, reason = ethical_check(text)
            entry["passed_ethics"] = ok

            if not ok:
                entry["error"] = reason
                results.append(entry)
                continue

            entry["text"] = text
            entry["used_in_digest"] = True
            approved_texts.append(text)
            results.append(entry)

        except Exception as e:
            entry["error"] = str(e)
            results.append(entry)

    if not approved_texts:
        raise HTTPException(status_code=400, detail="No valid texts")

    unique_texts, _ = dedupe_texts(approved_texts, sim_threshold=0.9)
    digest_text = summarize_texts(unique_texts)

    digest_id = save_digest(",".join(urls), digest_text)

    return {
        "id": digest_id,
        "digest": digest_text,
        "sources": unique_texts,
        "stats": {
            "total_urls": len(urls),
            "passed_ethics": sum(1 for r in results if r["passed_ethics"]),
            "failed_ethics": sum(1 for r in results if not r["passed_ethics"]),
            "deduplicated": len(approved_texts) - len(unique_texts),
        },
        "details": results,
    }


# ---------- Step 4: Render Cards ----------
@app.post("/render-cards")
def render_cards(payload: RenderRequest):
    row = fetch_digest(payload.digest_id)

    if row is None:
        raise HTTPException(status_code=404, detail="Digest not found")

    urls_str, digest_text = row

    sentences = [
        s.strip()
        for s in digest_text.split(".")
        if len(s.strip()) > 8
    ]

    if not sentences:
        raise HTTPException(status_code=400, detail="No usable sentences")

    os.makedirs("cards", exist_ok=True)
    outputs = []

    for i, sentence in enumerate(sentences):
        template = "A" if i % 2 == 0 else "B"
        filename = f"cards/card_{payload.digest_id}_{template}_{i}.png"

        render_quote_card(
            sentence,
            out_path=filename,
            template=template
        )

        outputs.append(filename)

    return {
        "status": "ok",
        "generated": len(outputs),
        "files": outputs,
    }
