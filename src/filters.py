# src/filters.py
import re
from typing import Dict

BAD_WORDS = [
    "kill", "hate", "die", "suicide", "violence",
    "abuse", "racist", "sex", "porn"
]

def ethical_check(text: str) -> Dict:
    """
    Very simple, explainable ethical checks.
    Returns:
    {
      "ok": bool,
      "reasons": list[str]
    }
    """

    reasons = []

    if not text or len(text.strip()) < 5:
        reasons.append("too_short")

    lower = text.lower()
    for word in BAD_WORDS:
        if word in lower:
            reasons.append(f"contains_sensitive_word:{word}")
            break

    # looks like random junk?
    if len(re.findall(r"[a-zA-Z]", text)) < 10:
        reasons.append("not_enough_language_content")

    return {
        "ok": len(reasons) == 0,
        "reasons": reasons
    }
