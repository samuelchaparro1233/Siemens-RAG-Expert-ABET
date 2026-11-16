"""
Módulo de ingesta y extracción de texto de documentos PDF técnicos de Siemens.
Soporta PyMuPDF y pypdf con preservación de metadatos (página, documento).
"""

from pathlib import Path
from typing import List, Dict, Any
import pypdf


def extract_pages_from_pdf(pdf_path: str | Path) -> List[Dict[str, Any]]:
    """
    Extrae el texto de cada página de un archivo PDF junto con sus metadatos.
    
    Args:
        pdf_path: Ruta al archivo PDF.
        
    Returns:
        Lista de diccionarios con keys: 'text', 'page_number', 'source_doc', 'total_pages'
    """
    path = Path(pdf_path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {pdf_path}")
        
    reader = pypdf.PdfReader(str(path))
    total_pages = len(reader.pages)
    documents = []
    
    for idx, page in enumerate(reader.pages):
        raw_text = page.extract_text() or ""
        clean_text = clean_extracted_text(raw_text)
        
        # Filtramos páginas que estén completamente vacías
        if clean_text.strip():
            documents.append({
                "text": clean_text,
                "page_number": idx + 1,
                "source_doc": path.name,
                "total_pages": total_pages
            })
            
    return documents


def clean_extracted_text(text: str) -> str:
    """
    Normaliza espacios y caracteres especiales preservando saltos de línea y tablas.
    """
    lines = [line.strip() for line in text.splitlines()]
    # Eliminar líneas consecutivas vacías
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        if not line:
            if not prev_empty:
                cleaned_lines.append("")
                prev_empty = True
        else:
            cleaned_lines.append(line)
            prev_empty = False
            
    return "\n".join(cleaned_lines)
