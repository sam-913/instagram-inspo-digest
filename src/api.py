# src/api.py
import warnings
warnings.filterwarnings("ignore")

from fastapi import FastAPI, HTTPException, Body
from pydantic import RootModel
from contextlib import asynccontextmanager
from typing import List
from datetime import date
import os

from src.ocr import extract_and_clean
from src.filters import ethical_check
from src.dedupe import dedupe_texts
from src.summarizer import summarize_texts
from src.card import render_quote_card
from src.db import init_db, save_digest

CARDS_DIR = "cards"
TEMPLATES = ["template_A.png", "template_B.png"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Instagram Inspo Digest API", lifespan=lifespan)


class ImageURLs(RootModel[List[str]]):
    pass


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/digest")
async def digest_endpoint(urls: ImageURLs):
    texts = []

    for url in urls.root:
        raw = extract_and_clean(url)
        ok, _ = ethical_check(raw)
        if ok and raw:
            texts.append(raw)

    if not texts:
        raise HTTPException(status_code=400, detail="No valid text")

    uniq, _ = dedupe_texts(texts)
    digest = summarize_texts(uniq)
    digest_id = save_digest(",".join(urls.root), digest)

    return {
        "id": digest_id,
        "digest": digest,
        "sources": uniq,
    }


@app.post("/daily-pack")
async def daily_pack(urls: List[str] = Body(...)):
    texts = []

    for url in urls:
        raw = extract_and_clean(url)
        ok, _ = ethical_check(raw)
        if ok and raw:
            texts.append(raw)

    uniq, _ = dedupe_texts(texts)

    if len(uniq) < 1:
        raise HTTPException(status_code=400, detail="No valid quotes")

    quotes = uniq[:4]
    today = date.today().isoformat()
    out_dir = os.path.join(CARDS_DIR, today)

    results = []

    for i, quote in enumerate(quotes):
        cards = []
        for template in TEMPLATES:
            filename = f"quote_{i+1}_{template.replace('.png','')}.png"
            path = os.path.join(out_dir, filename)
            render_quote_card(
                text=quote,
                template_name=template,
                out_path=path,
            )
            cards.append(path)

        results.append({
            "quote": quote,
            "cards": cards,
        })

    return {
        "date": today,
        "count": len(results),
        "editor_pack": results,
    }
