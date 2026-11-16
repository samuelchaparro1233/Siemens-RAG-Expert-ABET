"""
Retriever Híbrido Avanzado para Siemens RAG Expert.
Combina Búsqueda Léxica Exacta (BM25) con Búsqueda Semántica Densa (ChromaDB)
usando Reciprocal Rank Fusion (RRF) para máxima precisión en manuales técnicos.
"""

import sys
import os
import site
import re
from pathlib import Path
from typing import List, Dict, Any

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.append(user_site)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from sentence_transformers import SentenceTransformer
import chromadb
from rank_bm25 import BM25Okapi


DB_DIR = PROJECT_ROOT / "data" / "vectorstore" / "chroma"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def tokenize_text(text: str) -> List[str]:
    """Tokenizador técnico que preserva códigos alfanuméricos como F07900, p1082, S7-1500."""
    return re.findall(r'[a-zA-Z0-9_\-]+', text.lower())


class SiemensRetriever:
    """
    Retriever Híbrido:
    - Búsqueda Densa (Dense Retrieval): all-MiniLM-L6-v2 + ChromaDB Cosine
    - Búsqueda Léxica (Sparse Retrieval): BM25 Okapi sobre corpus completo
    - Fusión: Reciprocal Rank Fusion (RRF) con peso balanceado
    """
    def __init__(self, db_path: Path = DB_DIR):
        self.db_path = db_path
        self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME, local_files_only=True)
        self.client = chromadb.PersistentClient(path=str(self.db_path))
        
        # Cargar todos los fragmentos para el índice léxico BM25
        self._init_bm25_index()

    def _init_bm25_index(self):
        """Inicializa el índice BM25 a partir de los fragmentos almacenados en ChromaDB."""
        collection = self.client.get_collection("siemens_knowledge")
        all_data = collection.get(include=["documents", "metadatas"])
        
        self.all_docs = all_data["documents"]
        self.all_metas = all_data["metadatas"]
        self.all_ids = all_data["ids"]
        
        # Tokenizar todo el corpus
        tokenized_corpus = [tokenize_text(doc) for doc in self.all_docs]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
        source_filter: str | None = None,
        dense_weight: float = 0.6,
        sparse_weight: float = 0.4
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta búsqueda híbrida combinando puntuaciones densas y léxicas mediante RRF.
        """
        collection = self.client.get_collection("siemens_knowledge")
        
        # 1. Búsqueda Densa (Semántica con Embeddings)
        query_vector = self.embedder.encode([query], normalize_embeddings=True).tolist()
        where_clause = {"source": source_filter} if source_filter else None
        
        # Consultamos un pool más amplio para la fusión
        candidate_k = min(top_k * 4, len(self.all_ids))
        dense_results = collection.query(
            query_embeddings=query_vector,
            n_results=candidate_k,
            where=where_clause
        )
        
        # Mapear ranking denso
        dense_ranks = {}
        dense_similarities = {}
        if dense_results and dense_results["ids"]:
            for rank, (cid, dist) in enumerate(zip(dense_results["ids"][0], dense_results["distances"][0])):
                dense_ranks[cid] = rank + 1
                dense_similarities[cid] = 1.0 - dist
                
        # 2. Búsqueda Léxica (BM25 para códigos exactos y parámetros)
        tokenized_query = tokenize_text(query)
        bm25_scores = self.bm25.get_scores(tokenized_query)
        top_bm25_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:candidate_k]
        
        sparse_ranks = {}
        for rank, idx in enumerate(top_bm25_indices):
            cid = self.all_ids[idx]
            # Si hay filtro de manual, ignorar los que no coincidan
            if source_filter and self.all_metas[idx].get("source") != source_filter:
                continue
            if bm25_scores[idx] > 0:
                sparse_ranks[cid] = rank + 1

        # 3. Fusión por Rangos Recíprocos (RRF - Reciprocal Rank Fusion)
        # Formula: RRF_Score = dense_weight / (60 + dense_rank) + sparse_weight / (60 + sparse_rank)
        rrf_constant = 60
        all_candidate_ids = set(dense_ranks.keys()).union(set(sparse_ranks.keys()))
        
        id_to_doc_idx = {cid: idx for idx, cid in enumerate(self.all_ids)}
        scored_candidates = []
        
        for cid in all_candidate_ids:
            d_rank = dense_ranks.get(cid, 999)
            s_rank = sparse_ranks.get(cid, 999)
            
            rrf_score = (dense_weight / (rrf_constant + d_rank)) + (sparse_weight / (rrf_constant + s_rank))
            
            idx = id_to_doc_idx[cid]
            sim = dense_similarities.get(cid, 0.40)
            
            scored_candidates.append({
                "id": cid,
                "content": self.all_docs[idx],
                "metadata": self.all_metas[idx],
                "similarity": round(float(sim), 4),
                "rrf_score": rrf_score,
                "dense_rank": d_rank,
                "sparse_rank": s_rank
            })
            
        # Ordenar por el score RRF final
        scored_candidates.sort(key=lambda x: x["rrf_score"], reverse=True)
        return scored_candidates[:top_k]


if __name__ == "__main__":
    retriever = SiemensRetriever()
    test_query = "PTI setpoint pulse train input wiring"
    print(f"Probando Retriever Híbrido con: '{test_query}'")
    results = retriever.retrieve(test_query, top_k=2)
    for r in results:
        print(f"\n[RRF Score: {r['rrf_score']:.5f} | Dense Rank: {r['dense_rank']} | Sparse Rank: {r['sparse_rank']}]")
        print(f"Doc: {r['metadata']['source']} | Pág: {r['metadata']['page']}")
        print(f"Texto: {r['content'][:200]}...")
