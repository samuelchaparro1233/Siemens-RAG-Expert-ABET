"""
Módulo de segmentación de texto (Chunking) para documentos de ingeniería.
Divide el contenido preservando solapamiento (overlap) e inyectando metadatos.
"""

from typing import List, Dict, Any


def split_text_into_chunks(
    pages: List[Dict[str, Any]],
    chunk_size: int = 700,
    chunk_overlap: int = 120
) -> List[Dict[str, Any]]:
    """
    Divide las páginas extraídas en fragmentos (chunks) más pequeños con solapamiento,
    preservando el número de página y origen documental para la trazabilidad ABET.
    
    Args:
        pages: Lista de diccionarios con texto y metadatos por página.
        chunk_size: Tamaño aproximado en caracteres/palabras de cada fragmento.
        chunk_overlap: Solapamiento entre fragmentos consecutivos para no cortar contexto.
        
    Returns:
        Lista de chunks con 'content' y 'metadata'.
    """
    chunks = []
    chunk_id = 0
    
    for page in pages:
        text = page["text"]
        source_doc = page["source_doc"]
        page_num = page["page_number"]
        
        # Estrategia por párrafos primero para preservar tablas y bloques de código
        paragraphs = text.split("\n\n")
        current_chunk = ""
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            if len(current_chunk) + len(para) <= chunk_size:
                current_chunk += ("\n\n" + para if current_chunk else para)
            else:
                if current_chunk:
                    chunks.append({
                        "chunk_id": f"{source_doc}_p{page_num}_c{chunk_id}",
                        "content": current_chunk.strip(),
                        "metadata": {
                            "source": source_doc,
                            "page": page_num,
                            "chunk_index": chunk_id
                        }
                    })
                    chunk_id += 1
                    
                    # Conservamos solapamiento del final del chunk anterior
                    overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else ""
                    current_chunk = (overlap_text + "\n\n" + para).strip()
                else:
                    # El párrafo por sí solo excede chunk_size: división forzada por bloques
                    start = 0
                    while start < len(para):
                        sub_para = para[start:start + chunk_size]
                        chunks.append({
                            "chunk_id": f"{source_doc}_p{page_num}_c{chunk_id}",
                            "content": sub_para.strip(),
                            "metadata": {
                                "source": source_doc,
                                "page": page_num,
                                "chunk_index": chunk_id
                            }
                        })
                        chunk_id += 1
                        start += (chunk_size - chunk_overlap)
                    current_chunk = ""
                    
        if current_chunk:
            chunks.append({
                "chunk_id": f"{source_doc}_p{page_num}_c{chunk_id}",
                "content": current_chunk.strip(),
                "metadata": {
                    "source": source_doc,
                    "page": page_num,
                    "chunk_index": chunk_id
                }
            })
            chunk_id += 1
            
    return chunks
