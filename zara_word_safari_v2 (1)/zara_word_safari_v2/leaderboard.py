# ============================================
# leaderboard.py
# Persist and load top player scores
# ============================================
import json
import os
import datetime

_FILE = "leaderboard.json"
_MAX  = 10


def save_score(name: str, stars: int,
               accuracy: int, streak: int) -> list:
    entries = _load()
    entries.append({
        "name"    : name,
        "stars"   : stars,
        "accuracy": accuracy,
        "streak"  : streak,
        "date"    : datetime.date.today().isoformat(),
    })
    entries.sort(key=lambda e: (
        -e["stars"], -e.get("accuracy", 0)))
    entries = entries[:_MAX]
    try:
        with open(_FILE, "w", encoding="utf-8") as f:
            json.dump(entries, f,
                      ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[Leaderboard] Save failed: {e}")
    return entries


def load_top(n: int = 5) -> list:
    return _load()[:n]


def _load() -> list:
    try:
        with open(_FILE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []
