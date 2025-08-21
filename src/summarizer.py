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

    model_id = "sshleifer/distilbart-cnn-12-6"  # public, no token required

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id)

    # Try Apple MPS; CPU otherwise
    try:
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            model.to("mps")
    except Exception:
        pass

    # device=-1 means CPU; if model is on MPS it will still work
    _PIPE = pipeline("summarization", model=model, tokenizer=tokenizer, device=-1)
    return _PIPE

def summarize_texts(texts: List[str], min_length: int = 20, max_length: int = 130) -> str:
    combined = _normalize(texts)
    if not combined:
        return "No text available to summarize."
    pipe = _load_pipeline()
    out = pipe(combined, max_length=max_length, min_length=min_length, do_sample=False)
    return out[0]["summary_text"].strip()

