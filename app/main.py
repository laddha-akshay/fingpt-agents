from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse
import os
import json
import numpy as np
from pathlib import Path

# existing imports for your agents should remain
# from agents.scraper import ...
# from agents.sentiment import ...
# from agents.aggregator import ...
# from agents.reporter import ...

app = FastAPI()
static_dir = os.path.join(os.path.dirname(__file__), 'static')
app.mount('/static', StaticFiles(directory=static_dir), name='static')

UPLOAD_DIR = Path("/tmp/fingpt_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Simple in-memory store for uploaded items or indexed data
INDEXED_DATA_PATH = UPLOAD_DIR / "indexed_data.jsonl"

@app.post("/upload-news")
async def upload_news(file: UploadFile = File(...)):
    # Save uploaded file contents to a standard location and optionally parse
    saved = UPLOAD_DIR / f"uploaded_{file.filename}"
    content = await file.read()
    saved.write_bytes(content)

    # For demo, convert to line separated JSON objects if necessary
    # Here we just count lines as items
    try:
        text = content.decode('utf-8')
    except:
        text = ""
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    # create a simple JSONL representation
    with open(INDEXED_DATA_PATH, "w", encoding="utf-8") as f:
        for i, line in enumerate(lines):
            obj = {"id": f"up_{i}", "text": line}
            f.write(json.dumps(obj) + "\n")

    return JSONResponse({"status": "ok", "count": len(lines)})

@app.post("/run-pipeline")
def run_pipeline():
    """
    Demo pipeline runner. If INDEXED_DATA_PATH exists it uses uploaded data.
    Otherwise uses sample_data/news_sample.jsonl from repo.
    Return JSON with the final report and top signals.
    """
    # decide source
    if INDEXED_DATA_PATH.exists():
        source_path = INDEXED_DATA_PATH
    else:
        source_path = Path(__file__).parents[1] / "sample_data" / "news_sample.jsonl"

    # Load articles
    articles = []
    if source_path.exists():
        with open(source_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except:
                    # plain text line fallback
                    obj = {"id": f"line_{len(articles)}", "text": line.strip()}
                articles.append(obj)
    else:
        return JSONResponse({"error": "No data available", "source": str(source_path)})

    # Demo sentiment and aggregation steps - replace with your agents
    # For demo use naive sentiment: occurrence of 'up' 'down' 'gain' 'loss' etc
    def simple_sentiment(text):
        low = text.lower()
        score = 0
        for w in ["gain", "up", "bull", "positive"]:
            if w in low:
                score += 1
        for w in ["loss", "down", "bear", "negative", "drop"]:
            if w in low:
                score -= 1
        return score

    signals = {}
    for a in articles:
        txt = a.get("text", "")
        s = simple_sentiment(txt)
        # naive entity extraction: look for $TICKER or uppercase words length 2-5
        words = [w.strip(".,") for w in txt.split() if w.isupper() and 1 < len(w) <= 5]
        tickers = words if words else ["GENERIC"]
        for t in tickers:
            if t not in signals:
                signals[t] = {"score": 0, "count": 0, "examples": []}
            signals[t]["score"] += s
            signals[t]["count"] += 1
            if len(signals[t]["examples"]) < 2:
                signals[t]["examples"].append(txt[:200])

    # Prepare sorted list
    ranked = sorted(signals.items(), key=lambda x: x[1]["score"], reverse=True)
    report = {
        "top_signals": [{"ticker": t, **meta} for t, meta in ranked[:10]],
        "article_count": len(articles),
        "source": str(source_path)
    }

    return JSONResponse(report)
