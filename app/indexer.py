import json
from pathlib import Path
import numpy as np

try:
    import faiss  # faiss-cpu
except Exception as e:
    faiss = None


class FaissIndexer:
    def __init__(self, dim: int, data_dir: Path | None = None):
        self.dim = dim
        self.data_dir = data_dir or Path(__file__).resolve().parent / "data"
        self.data_dir.mkdir(exist_ok=True)
        self.index_path = self.data_dir / "index.faiss"
        self.meta_path = self.data_dir / "meta.json"
        # Use inner product; for best results you might normalize embeddings
        if faiss is None:
            raise RuntimeError("faiss not available; install faiss-cpu")
        self.index = faiss.IndexFlatIP(dim)
        self.metas: list[dict] = []

    def load(self):
        if self.index_path.exists():
            self.index = faiss.read_index(str(self.index_path))
        if self.meta_path.exists():
            try:
                self.metas = json.loads(self.meta_path.read_text())
            except Exception:
                self.metas = []

    def save(self):
        faiss.write_index(self.index, str(self.index_path))
        self.meta_path.write_text(json.dumps(self.metas))

    def add(self, vecs, metas):
        arr = np.asarray(vecs, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr.reshape(1, -1)
        self.index.add(arr)
        self.metas.extend(metas)

    def search(self, qv, k: int = 5):
        q = np.asarray(qv, dtype=np.float32)
        if q.ndim == 1:
            q = q.reshape(1, -1)
        D, I = self.index.search(q, k)
        scores = D[0].tolist()
        indices = I[0].tolist()
        results = []
        for score, idx in zip(scores, indices):
            if idx < 0 or idx >= len(self.metas):
                continue
            item = dict(self.metas[idx])
            item["score"] = float(score)
            results.append(item)
        return results

    def reset(self):
        # Recreate a fresh index and clear metadata
        self.index = faiss.IndexFlatIP(self.dim)
        self.metas = []
        try:
            if self.index_path.exists():
                self.index_path.unlink()
            if self.meta_path.exists():
                self.meta_path.unlink()
        except Exception:
            pass
        # Persist empty structures
        self.save()