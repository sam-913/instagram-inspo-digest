# src/summarizer.py
from typing import List

_PIPE = None

def _normalize(texts: List[str]) -> str:
    return " ".join(t.strip() for t in texts if isinstance(t, str) and t.strip())

def _load_pipeline():
    global _PIPE
    if _PIPE is not None:
        return _PIPE
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
    import torch
    model_id = "sshleifer/distilbart-cnn-12-6"
    tok = AutoTokenizer.from_pretrained(model_id)
    mdl = AutoModelForSeq2SeqLM.from_pretrained(model_id)
    try:
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            mdl.to("mps")
    except Exception:
        pass
    _PIPE = pipeline("summarization", model=mdl, tokenizer=tok, device=-1)
    return _PIPE

def summarize_texts(texts: List[str], min_length: int = 20, max_length: int = 130) -> str:
    combined = _normalize(texts)
    if not combined:
        return "No text available to summarize."
    pipe = _load_pipeline()

    # heuristic: scale to input size (tokens-ish)
    n_chars = len(combined)
    # very short input? keep summary short
    if n_chars < 80:
        max_length, min_length = 24, 8
    elif n_chars < 240:
        max_length, min_length = 60, 20
    else:
        max_length, min_length = 130, 30

    out = pipe(combined, max_length=max_length, min_length=min_length, do_sample=False)
    return out[0]["summary_text"].strip()
