"""
Pipeline RAG completo para Siemens RAG Expert.
Integra recuperación semántica, inyección de contexto con System Prompt anti-alucinaciones
y síntesis de respuestas técnicas con citas de páginas y manuales.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Cargar automáticamente credenciales del archivo .env
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

from src.retriever import SiemensRetriever

try:
    from google import genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False


SYSTEM_PROMPT = """Eres Siemens RAG Expert, un asistente de ingenieria especializado en automatizacion industrial, control con PLCs Siemens (SIMATIC S7-1200 / S7-1500), entorno TIA Portal y accionamientos SINAMICS.

Directivas estrictas de respuesta:
1. IDIOMA: Responde SIEMPRE en ESPANOL claro, tecnico y profesional, sin importar que los manuales originales esten en ingles. Traduce y explica los conceptos y procedimientos en espanol, conservando los nombres tecnicos de parametros (ej. p1082), bloques (ej. OB1, FB, FC) y pines (ej. X8, PTI).
2. FUNDAMENTACION ESTRICTA (GROUNDING): Basa tu respuesta EXCLUSIVAMENTE en el contexto documental proporcionado.
3. PREVENCION DE ALUCINACIONES: Si la informacion requerida no esta explicitamente en el contexto provisto, responde con total honestidad: "La documentacion provista no contiene informacion sobre este aspecto." NO inventes parametros ni procedimientos.
4. CITACION TECNICA: Indica siempre el nombre del manual y el numero de pagina exacta de donde se extrajo la solucion.
5. SEGURIDAD Y FORMATO: Si la respuesta involucra maniobras de hardware o cableado, destaca las precauciones de seguridad industrial (ej. desconexion de energia, bloqueo de seguridad LOTO).
"""


class SiemensRAGPipeline:
    def __init__(self, use_api: bool = True, api_key: str | None = None):
        self.retriever = SiemensRetriever()
        self.use_api = use_api
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        self.client = None
        
        if self.use_api and self.api_key and HAS_GENAI:
            try:
                self.client = genai.Client(api_key=self.api_key)
                print("Generador Gemini conectado exitosamente.")
            except Exception as e:
                print(f"Aviso al iniciar cliente Gemini: {e}")
                self.client = None
        else:
            print("Modo de operacion: Extraccion semantica y evidencia local (Modo Local).")

    def format_context(self, retrieved_chunks: List[Dict[str, Any]]) -> str:
        """Formatea los fragmentos recuperados para su inyección en el prompt."""
        formatted = []
        for i, c in enumerate(retrieved_chunks, 1):
            source = c["metadata"].get("source", "Desconocido")
            page = c["metadata"].get("page", "?")
            sim = c.get("similarity", 0.0)
            formatted.append(
                f"[Fragmento {i} | Fuente: {source} (Pág. {page}) | Relevancia: {sim:.2f}]\n{c['content']}"
            )
        return "\n\n".join(formatted)

    def answer_query(self, query: str, top_k: int = 4) -> Dict[str, Any]:
        """
        Ejecuta el flujo RAG completo:
        1. Búsqueda vectorial Top-K
        2. Inyección de contexto
        3. Generación fundamentada
        """
        # 1. Recuperar contexto semántico
        retrieved_docs = self.retriever.retrieve(query, top_k=top_k)
        context_str = self.format_context(retrieved_docs)
        
        # 2. Generar respuesta
        if self.client:
            user_prompt = f"CONTEXTO TECNICO OFICIAL:\n{context_str}\n\nCONSULTA DEL INGENIERO:\n{query}\n\nRESPUESTA ESTRUCTURADA EN ESPANOL:"
            
            # Usar directamente gemini-3.8-flash con reintento ante 503
            import time
            answer_text = None
            last_err = None
            
            for attempt in range(3):
                try:
                    response = self.client.models.generate_content(
                        model="gemini-3.8-flash",
                        contents=user_prompt,
                        config={"system_instruction": SYSTEM_PROMPT, "temperature": 0.2}
                    )
                    answer_text = response.text
                    break
                except Exception as e:
                    last_err = e
                    # Si es error 503 (servidor ocupado), esperar 1.5s y reintentar
                    if "503" in str(e):
                        time.sleep(1.5)
                        continue
                    else:
                        break
                    
            if not answer_text:
                answer_text = f"Aviso de generacion ({last_err}). Mostrando evidencia documental directa:\n\n{context_str}"
        else:
            # Síntesis estructurada local a partir de la evidencia documental (con encabezados en español)
            sources_summary = "\n".join(
                [f"- 📄 **{d['metadata']['source']}** (Página {d['metadata']['page']}) [Similitud: {d['similarity']:.2%}]" for d in retrieved_docs]
            )
            answer_text = (
                f"### 📋 Síntesis de Evidencia Recuperada (Modo Extracción Local):\n\n"
                f"> **Nota:** Los manuales técnicos originales se encuentran en inglés. A continuación se presentan los fragmentos oficiales más relevantes recuperados de los documentos oficiales de Siemens.\n\n"
                f"{context_str}\n\n"
                f"### 📚 Fuentes Oficiales Citadas:\n{sources_summary}\n\n"
                f"💡 *Para obtener una síntesis explicativa redactada 100% en español con diagnóstico paso a paso, ingresa tu API Key de Gemini en la barra lateral.*"
            )
            
        return {
            "query": query,
            "answer": answer_text,
            "sources": retrieved_docs
        }
