from fastapi import FastAPI, UploadFile, File, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import os
from pathlib import Path
from .ingestion import load_logs
from .embeddings import Embedder
from .indexer import FaissIndexer
from .query_agent import explain_incidents
import numpy as np

# compute static dir relative to this file
static_dir = Path(__file__).resolve().parent / "static"

app = FastAPI()
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


embedder = Embedder()
dim = embedder.model.get_sentence_embedding_dimension()
indexer = FaissIndexer(dim=dim)
indexer.load()

@app.post("/upload-logs")
async def upload_logs(file: UploadFile = File(...)):
    path = f"/tmp/temp_{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())
    df = load_logs(path)
    if df.empty:
        return JSONResponse({"status": "ok", "count": 0, "message": "no parsable lines found"})
    texts = df["message"].tolist()
    vecs = embedder.embed_texts(texts)
    vecs = np.array(vecs).astype("float32")
    metas = df.to_dict(orient="records")
    indexer.add(vecs, metas)
    indexer.save()
    return {"status": "ok", "count": len(metas)}

@app.get("/query")
def query(q: str):
    qv = embedder.embed_texts([q]).astype("float32")
    results = indexer.search(qv, k=5)
    explanation = explain_incidents(results, q)
    return {"results": results, "explanation": explanation}

@app.get("/")
def root():
    return HTMLResponse(open(os.path.join(static_dir, "index.html")).read())
