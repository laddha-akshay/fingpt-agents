from sentence_transformers import SentenceTransformer
import numpy as np


class Embedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", normalize: bool = True):
        # Small, fast sentence embedding model suitable for local demos
        self.model = SentenceTransformer(model_name)
        self.normalize = normalize

    def embed_texts(self, texts):
        # Returns a numpy array of shape (n, dim). When normalize=True, vectors are L2-normalized.
        vecs = self.model.encode(texts, normalize_embeddings=self.normalize)
        return np.asarray(vecs, dtype=np.float32)