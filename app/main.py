from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import os
from pathlib import Path
import numpy as np

from .ingestion import load_news
from .embeddings import Embedder
from .indexer import FaissIndexer
from .query_agent import explain_incidents, financial_answer

from agents.scraper import load_sample_news
from agents.sentiment import sentiment_score
from agents.aggregator import aggregate_by_ticker
from agents.reporter import make_report

# compute static dir relative to this file
static_dir = Path(__file__).resolve().parent / "static"

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


embedder = Embedder()
dim = embedder.model.get_sentence_embedding_dimension()
indexer = FaissIndexer(dim=dim)
indexer.load()

@app.post("/upload-news")
async def upload_news(file: UploadFile = File(...)):
    path = f"/tmp/temp_{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())
    df = load_news(path)
    if df.empty:
        return JSONResponse({"status": "ok", "count": 0, "message": "no parsable items found"})
    texts = df["text"].tolist()
    vecs = embedder.embed_texts(texts)
    vecs = np.array(vecs).astype("float32")
    metas = df.to_dict(orient="records")
    indexer.add(vecs, metas)
    indexer.save()
    return {"status": "ok", "count": len(metas)}

@app.get("/query")
def query(q: str):
    if not q or not q.strip():
        return JSONResponse({"status": "error", "message": "Query cannot be empty"}, status_code=400)
    # simple RAG-like retrieval over uploaded news
    qv = embedder.embed_texts([q]).astype("float32")
    results = indexer.search(qv, k=5)
    explanation = explain_incidents(results, q)
    return {"results": results, "explanation": explanation}

@app.get("/financial-qa")
def financial_qa(q: str):
    # Structured financial answer: risks, opportunities, summary, confidence
    if not q or not q.strip():
        return JSONResponse({"status": "error", "message": "Query cannot be empty"}, status_code=400)
    qv = embedder.embed_texts([q]).astype("float32")
    results = indexer.search(qv, k=8)
    if not results:
        return JSONResponse({"status": "error", "message": "Index is empty. Upload news first."}, status_code=400)
    answer = financial_answer(results, q)
    return {"status": "ok", "answer": answer}

@app.post("/run-pipeline")
def run_pipeline():
    # Load sample news
    items = load_sample_news()
    if not items:
        return {"status": "error", "message": "No sample data found"}

    # Sentiment per item
    for it in items:
        txt = it.get("text") or it.get("title") or ""
        it["sentiment"] = float(sentiment_score(txt))

    # Aggregate signals by ticker
    agg = aggregate_by_ticker(items)
    top = agg[:3]  # top by most negative first per aggregator sorting
    headlines = [it.get("title", "") for it in items][:5]

    # Also populate retrieval index from sample items so Q&A works out-of-the-box
    texts = [(it.get("text") or it.get("title") or "") for it in items]
    if texts:
        vecs = embedder.embed_texts(texts).astype("float32")
        metas = [{"ticker": it.get("ticker", "UNKNOWN"), "title": it.get("title", ""), "text": it.get("text", "")} for it in items]
        indexer.add(vecs, metas)
        indexer.save()

    # Generate a short report (LLM if key present, else fallback)
    report = make_report(top, headlines)
    return {"status": "ok", "signals": agg, "top_signals": top, "headlines": headlines, "report": report}

@app.post("/reset-index")
def reset_index():
    indexer.reset()
    return {"status": "ok", "message": "Index reset. Re-upload or run pipeline to rebuild."}

@app.get("/")
def root():
    return HTMLResponse(open(os.path.join(static_dir, "index.html")).read())
