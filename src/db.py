# src/db.py
import sqlite3
from typing import List, Tuple, Optional  # 👈 use Optional for 3.9

DB_PATH = "digests.db"

DDL = """
CREATE TABLE IF NOT EXISTS digests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    urls TEXT NOT NULL,         -- comma-separated list
    digest TEXT NOT NULL,       -- summary text
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(DDL)
        conn.commit()
    finally:
        conn.close()

def save_digest(urls: List[str], digest: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO digests (urls, digest) VALUES (?, ?)",
            (",".join(urls), digest),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def fetch_digest(digest_id: int) -> Optional[Tuple[str, str]]:  # 👈 3.9-safe
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("SELECT urls, digest FROM digests WHERE id = ?", (digest_id,))
        row = cur.fetchone()
        if row is None:
            return None
        return row[0], row[1]  # urls_str, digest
    finally:
        conn.close()

# --- add below your existing DDL and functions in src/db.py ---

OCR_CACHE_DDL = """
CREATE TABLE IF NOT EXISTS ocr_cache (
    url TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def init_db() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(DDL)
        conn.execute(OCR_CACHE_DDL)     # <- create cache table too
        conn.commit()
    finally:
        conn.close()

def get_cached_ocr(url: str) -> Optional[str]:
    conn = sqlite3.connect(DB_PATH)
    try:
        cur = conn.cursor()
        cur.execute("SELECT text FROM ocr_cache WHERE url = ?", (url,))
        row = cur.fetchone()
        return row[0] if row else None
    finally:
        conn.close()

def set_cached_ocr(url: str, text: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            "INSERT OR REPLACE INTO ocr_cache(url, text) VALUES (?, ?)",
            (url, text),
        )
        conn.commit()
    finally:
        conn.close()
