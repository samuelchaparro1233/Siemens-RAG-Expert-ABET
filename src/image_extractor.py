"""
Módulo de extracción y caché de imágenes técnicas y diagramas desde PDFs de Siemens.
Utiliza pypdf nativo (sin dependencias externas pesadas) para extraer diagramas de cableado,
esquemas y capturas de pantalla de la página referenciada.
"""

from pathlib import Path
from typing import List
import pypdf

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
CACHE_DIR = PROJECT_ROOT / "data" / "extracted_images"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_images_for_page(pdf_name: str, page_number: int) -> List[Path]:
    """
    Extrae o recupera de caché las imágenes/diagramas presentes en la página indicada.
    
    Args:
        pdf_name: Nombre del archivo PDF (ej. 'SINAMICS_V90_OPI_en-US_en-US.pdf')
        page_number: Número de página humana (1-indexed)
        
    Returns:
        Lista de rutas locales a las imágenes extraídas (.png/.jpg)
    """
    pdf_path = DOCS_DIR / pdf_name
    if not pdf_path.exists():
        return []
        
    # Prefijo en caché
    prefix = f"{Path(pdf_name).stem}_p{page_number}"
    existing = list(CACHE_DIR.glob(f"{prefix}_*"))
    if existing:
        return existing
        
    extracted_paths = []
    try:
        reader = pypdf.PdfReader(str(pdf_path))
        if 0 <= (page_number - 1) < len(reader.pages):
            page = reader.pages[page_number - 1]
            for idx, img_file in enumerate(page.images):
                # Filtrar imágenes diminutas (iconos o viñetas menores a 3 KB)
                if len(img_file.data) < 3072:
                    continue
                    
                ext = Path(img_file.name).suffix or ".png"
                out_path = CACHE_DIR / f"{prefix}_img{idx}{ext}"
                with open(out_path, "wb") as f:
                    f.write(img_file.data)
                extracted_paths.append(out_path)
    except Exception as e:
        print(f"Aviso al extraer imagen de {pdf_name} p.{page_number}: {e}")
        
    return extracted_paths
