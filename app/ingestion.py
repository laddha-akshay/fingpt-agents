import os
import json
import pandas as pd


def load_news(path: str) -> pd.DataFrame:
    """Load a file of news/tweets into a DataFrame with columns:
    ticker, title, text.
    Supports JSONL with keys {ticker, title, text} or plain .txt (one line per item).
    """
    ext = os.path.splitext(path)[1].lower()
    rows = []
    if ext == ".jsonl":
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                rows.append({
                    "ticker": obj.get("ticker", "UNKNOWN"),
                    "title": obj.get("title", ""),
                    "text": obj.get("text") or obj.get("message") or ""
                })
    else:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                t = line.strip()
                if not t:
                    continue
                rows.append({"ticker": "UNKNOWN", "title": "", "text": t})

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(columns=["ticker", "title", "text"])
    return df