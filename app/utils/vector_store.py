import faiss
import os
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer

VECTOR_DIR = "data/vectors"
os.makedirs(VECTOR_DIR, exist_ok=True)

class VectorStore:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index_path = f"{VECTOR_DIR}/faiss.index"
        self.meta_path = f"{VECTOR_DIR}/meta.pkl"

        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
            with open(self.meta_path, "rb") as f:
                self.meta = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(384)
            self.meta = []

    def add(self, text: str, metadata: dict):
        embedding = self.model.encode([text])[0]
        self.index.add(np.array([embedding], dtype="float32"))
        self.meta.append(metadata)
        self._save()

    def _save(self):
        faiss.write_index(self.index, self.index_path)
        with open(self.meta_path, "wb") as f:
            pickle.dump(self.meta, f)
