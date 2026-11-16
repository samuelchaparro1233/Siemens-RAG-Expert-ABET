"""
Pipeline de indexación documental optimizado para Siemens RAG Expert.
Extrae el texto de los manuales en docs/, realiza el chunking con metadatos
y genera la base vectorial persistente en data/vectorstore/.
Para manuales masivos (>1000 páginas), extrae de forma eficiente los capítulos
fundamentales o indexa con límite configurable para mantener un rendimiento óptimo.
"""

import sys
import os
import site
import time
from pathlib import Path
from typing import List, Dict, Any

user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.append(user_site)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from sentence_transformers import SentenceTransformer
import chromadb
import pypdf

from src.chunking import split_text_into_chunks
from src.pdf_loader import clean_extracted_text


EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
DB_DIR = PROJECT_ROOT / "data" / "vectorstore" / "chroma"
DOCS_DIR = PROJECT_ROOT / "docs"

# Límite de páginas para manuales gigantescos (ej. bibliotecas de 8.000 páginas)
MAX_PAGES_PER_DOC = 600


def extract_pages_optimized(pdf_path: Path) -> List[Dict[str, Any]]:
    reader = pypdf.PdfReader(str(pdf_path))
    total_pages = len(reader.pages)
    limit = min(total_pages, MAX_PAGES_PER_DOC)
    
    docs = []
    print(f"    Procesando {limit} páginas (de {total_pages} totales)...", flush=True)
    for idx in range(limit):
        try:
            raw_text = reader.pages[idx].extract_text() or ""
            clean_text = clean_extracted_text(raw_text)
            if clean_text.strip():
                docs.append({
                    "text": clean_text,
                    "page_number": idx + 1,
                    "source_doc": pdf_path.name,
                    "total_pages": total_pages
                })
        except Exception:
            continue
    return docs


def build_knowledge_base():
    print("=" * 60)
    print("Siemens RAG Expert — Indexador Optimizado Multidocumental")
    print("=" * 60)
    
    # 1. Cargar modelo de embeddings
    print(f"\n[1/4] Cargando modelo de embeddings: {EMBEDDING_MODEL_NAME}...")
    embedder = SentenceTransformer(EMBEDDING_MODEL_NAME, local_files_only=True)
    
    # 2. Ingesta de PDFs
    print("\n[2/4] Extrayendo páginas de documentos técnicos en docs/...")
    pdf_files = list(DOCS_DIR.glob("*.pdf"))
    if not pdf_files:
        print("ERROR: No se encontraron PDFs en docs/.")
        sys.exit(1)
        
    all_chunks: List[Dict[str, Any]] = []
    for pdf_path in pdf_files:
        print(f" -> Procesando: {pdf_path.name} ({pdf_path.stat().st_size / (1024*1024):.1f} MB)")
        pages = extract_pages_optimized(pdf_path)
        chunks = split_text_into_chunks(pages, chunk_size=700, chunk_overlap=120)
        print(f"    Páginas útiles: {len(pages)} | Chunks: {len(chunks)}")
        all_chunks.extend(chunks)
        
    print(f"\nTotal de chunks a indexar: {len(all_chunks)}")
    
    # 3. Inicializar ChromaDB persistente
    print(f"\n[3/4] Inicializando ChromaDB en {DB_DIR}...")
    client = chromadb.PersistentClient(path=str(DB_DIR))
    
    try:
        client.delete_collection("siemens_knowledge")
    except Exception:
        pass
        
    collection = client.create_collection(
        name="siemens_knowledge",
        metadata={"hnsw:space": "cosine"}
    )
    
    # 4. Generación de Embeddings e Inserción por lotes
    print("\n[4/4] Generando embeddings vectoriales e insertando en la base...")
    batch_size = 128
    start_time = time.time()
    
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        texts = [c["content"] for c in batch]
        ids = [c["chunk_id"] for c in batch]
        metadatas = [c["metadata"] for c in batch]
        
        vectors = embedder.encode(texts, show_progress_bar=False, normalize_embeddings=True)
        collection.add(
            ids=ids,
            documents=texts,
            embeddings=vectors.tolist(),
            metadatas=metadatas
        )
        print(f" -> Insertados {min(i + batch_size, len(all_chunks))}/{len(all_chunks)} chunks...", flush=True)
        
    elapsed = time.time() - start_time
    print(f"\n¡Indexación completada con éxito en {elapsed:.2f} segundos!")
    print(f"Colección 'siemens_knowledge' contiene: {collection.count()} registros indexados.")


if __name__ == "__main__":
    build_knowledge_base()
