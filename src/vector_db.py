"""
Motor de Búsqueda Vectorial y Embeddings para Siemens RAG Expert.
Utiliza sentence-transformers (o fallback nativo en PyTorch/TF-IDF) y persistencia en ChromaDB/JSON.
"""

from pathlib import Path
from typing import List, Dict, Any
import json
import numpy as np


class VectorDatabase:
    """
    Gestor de base de datos vectorial local.
    Almacena vectores densos y metadatos de los chunks documentales.
    """
    def __init__(self, storage_dir: str | Path = "data/vectorstore"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "chunks_index.json"
        self.vectors_file = self.storage_dir / "embeddings.npy"
        
        self.chunks: List[Dict[str, Any]] = []
        self.embeddings: np.ndarray | None = None
        self._load_if_exists()
        
    def _load_if_exists(self):
        if self.index_file.exists() and self.vectors_file.exists():
            with open(self.index_file, "r", encoding="utf-8") as f:
                self.chunks = json.load(f)
            self.embeddings = np.load(self.vectors_file)
            print(f"Index cargado: {len(self.chunks)} chunks indexados.")
            
    def add_chunks_with_embeddings(self, chunks: List[Dict[str, Any]], embeddings: np.ndarray):
        """
        Guarda los chunks y su matriz de embeddings normalizada.
        """
        self.chunks = chunks
        # Normalizar para que el producto punto equivalga a similitud coseno
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1e-10
        self.embeddings = embeddings / norms
        
        with open(self.index_file, "w", encoding="utf-8") as f:
            json.dump(self.chunks, f, ensure_ascii=False, indent=2)
        np.save(self.vectors_file, self.embeddings)
        print(f"Base vectorial guardada exitosamente en {self.storage_dir}")

    def search_top_k(self, query_vector: np.ndarray, top_k: int = 4) -> List[Dict[str, Any]]:
        """
        Búsqueda por similitud coseno del vector de consulta frente a toda la base.
        """
        if self.embeddings is None or len(self.chunks) == 0:
            raise ValueError("La base de datos vectorial está vacía.")
            
        q_norm = np.linalg.norm(query_vector)
        if q_norm > 0:
            query_vector = query_vector / q_norm
            
        similarities = np.dot(self.embeddings, query_vector)
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "score": float(similarities[idx]),
                "chunk": self.chunks[idx]
            })
        return results
