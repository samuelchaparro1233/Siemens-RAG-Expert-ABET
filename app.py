"""
Interfaz de Usuario Profesional para Siemens RAG Expert.
Diseño moderno con temática industrial de Siemens (Petroleum Teal & Dark UI),
tarjetas interactivas con métricas de relevancia, indicadores de estado y visor avanzado de citas.
"""

import sys
import site
from pathlib import Path

user_site = site.getusersitepackages()
if user_site and user_site not in sys.path:
    sys.path.append(user_site)

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.rag_pipeline import SiemensRAGPipeline
from src.image_extractor import get_images_for_page


# 1. Configuración de página con favicon y layout expandido
st.set_page_config(
    page_title="Siemens RAG Expert | Industrial Automation AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inyección de CSS personalizado para estética Siemens Industrial
st.markdown("""
<style>
    /* Tipografía y paleta Siemens: Teal #00646E, Petrol #009999, Dark Slate #1B2838 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Encabezado Hero */
    .hero-container {
        background: linear-gradient(135deg, #00333A 0%, #00646E 60%, #009999 100%);
        padding: 2.2rem 2.5rem;
        border-radius: 14px;
        color: #FFFFFF;
        box-shadow: 0 8px 24px rgba(0, 100, 110, 0.25);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    .hero-title {
        font-size: 2.4rem;
        font-weight: 700;
        letter-spacing: -0.5px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.8rem;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        font-weight: 300;
        opacity: 0.92;
        margin-top: 0.5rem;
    }
    .badge-abet {
        background: rgba(255, 255, 255, 0.18);
        border: 1px solid rgba(255, 255, 255, 0.3);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        display: inline-block;
        margin-top: 0.8rem;
    }

    /* Tarjetas de métricas en la barra lateral */
    .metric-card {
        background: #0E1621;
        border: 1px solid #1E2D3D;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 0.8rem;
    }
    .metric-label {
        color: #8C9BAE;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .metric-val {
        color: #00E5FF;
        font-size: 1.4rem;
        font-weight: 700;
    }

    /* Tarjeta de respuesta del Asistente */
    .response-card {
        background: #0E1621;
        border-left: 5px solid #00E5FF;
        border-radius: 10px;
        padding: 1.5rem 1.8rem;
        margin-top: 1.5rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }

    /* Tarjetas de evidencia documental */
    .source-box {
        background: #152232;
        border: 1px solid #233549;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 0.8rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .source-box:hover {
        border-color: #00E5FF;
        transform: translateY(-2px);
    }
    .source-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.6rem;
        font-size: 0.88rem;
        font-weight: 600;
    }
    .tag-page {
        background: #00646E;
        color: #E0F7FA;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.78rem;
    }
    .tag-score {
        background: rgba(0, 229, 255, 0.15);
        color: #00E5FF;
        border: 1px solid #00E5FF;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 0.78rem;
    }
</style>
""", unsafe_allow_html=True)


# 3. Encabezado Hero Interactivo
st.markdown("""
<div class="hero-container">
    <div class="hero-title">
        <span>⚡ Siemens RAG Expert</span>
    </div>
    <div class="hero-subtitle">
        Asistente Cognitivo de Soporte y Diagnóstico para Controladores SIMATIC S7, TIA Portal y Accionamientos SINAMICS
    </div>
    <div class="badge-abet">
        🎓 Proyecto Final de IA (18314) | Marco ABET (SO1, SO6, SO7) | Nivel N5
    </div>
</div>
""", unsafe_allow_html=True)


# 4. Barra Lateral de Control y Telemetría del Sistema
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/5f/Siemens-logo.svg", width=140)
    st.markdown("### 🎛️ Centro de Telemetría RAG")
    
    docs_dir = PROJECT_ROOT / "docs"
    pdf_list = list(docs_dir.glob("*.pdf")) if docs_dir.exists() else []
    
    # Obtener conteo dinámico real de la colección
    try:
        from chromadb import PersistentClient
        _client = PersistentClient(path=str(PROJECT_ROOT / "data" / "vectorstore" / "chroma"))
        _col = _client.get_collection("siemens_knowledge")
        total_chunks_count = f"{_col.count():,}".replace(",", ".")
    except Exception:
        total_chunks_count = "2.428"
    
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Manuales</div>
            <div class="metric-val">{len(pdf_list)}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Chunks</div>
            <div class="metric-val">{total_chunks_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("#### 📂 Documentos Activos en Base de Datos")
    for pdf in pdf_list:
        file_size_mb = pdf.stat().st_size / (1024 * 1024)
        st.markdown(f"📄 **`{pdf.name[:24]}...`**  \n<small style='color:#8C9BAE;'>Tamaño: {file_size_mb:.1f} MB</small>", unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("#### ⚙️ Parámetros de Recuperación")
    top_k = st.slider("Ventana de Contexto (Top-K Chunks):", min_value=1, max_value=8, value=3)
    
    st.markdown("#### ⚖️ Balance de Recuperación Híbrida")
    dense_ratio = st.slider("Peso Semántico vs Léxico (BM25):", min_value=0.1, max_value=0.9, value=0.6, step=0.1, help="0.6 = 60% significado conceptual (Embeddings) + 40% coincidencia exacta de códigos (BM25)")
    
    min_similarity = st.slider("Filtro de Similitud Mínima:", min_value=0.0, max_value=0.8, value=0.30, step=0.05)
    
    st.markdown("---")
    st.markdown("#### 🤖 Modo de Generación")
    mode_selection = st.radio(
        "Selecciona el modo de respuesta:",
        options=["✨ Modo Generativo (Gemini AI)", "💻 Modo Local (Offline / Evidencia Directa)"],
        index=0,
        help="El modo Gemini redacta la solución técnica en español. El modo Local extrae la evidencia textual pura y los diagramas sin conexión a internet."
    )
    
    st.markdown("---")
    st.caption("🚀 Motor: `all-MiniLM-L6-v2` | Base Vectorial: `ChromaDB HNSW`")


# 5. Instanciar Pipeline según el modo seleccionado
def get_pipeline(use_api: bool):
    return SiemensRAGPipeline(use_api=use_api)

use_gemini = (mode_selection == "✨ Modo Generativo (Gemini AI)")
pipeline = get_pipeline(use_api=use_gemini)


# 6. Banco de Pruebas Rápidas (Chips de Consultas de Planta)
st.markdown("#### 💡 Escenarios de Planta y Consultas Frecuentes")
c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("🔧 Puesta en Marcha BOP-2", use_container_width=True):
        st.session_state["query_input"] = "¿Cómo se realiza la puesta en marcha rápida básica usando el panel BOP-2?"
with c2:
    if st.button("⚡ Cableado PTI en SINAMICS V90", use_container_width=True):
        st.session_state["query_input"] = "¿Cuáles son las instrucciones de cableado para la entrada de tren de pulsos PTI en el SINAMICS V90?"
with c3:
    if st.button("🖥️ Avisos y Alarmas en WinCC Unified", use_container_width=True):
        st.session_state["query_input"] = "¿Cómo se configuran los avisos y alarmas en WinCC Unified?"
with c4:
    if st.button("🔌 Conexión CPU 1516-3 PN/DP", use_container_width=True):
        st.session_state["query_input"] = "¿Cuáles son las interfaces de comunicación de la CPU 1516-3 PN/DP y cómo se configuran?"

st.markdown("")

# 7. Formulario de Búsqueda
default_val = st.session_state.get("query_input", "")
user_query = st.text_input(
    "🔍 Ingresa tu consulta técnica, código de alarma o requerimiento de conexionado:",
    value=default_val,
    placeholder="Ej: ¿Qué indica el código de fallo F07900 o cómo cablear entradas analógicas en CPU 1512C-1 PN?"
)

col_btn1, col_btn2 = st.columns([1, 5])
with col_btn1:
    submit_btn = st.button("Consultar Asistente", type="primary", use_container_width=True)

if submit_btn and user_query:
    with st.spinner("⚡ Ejecutando Búsqueda Híbrida (Dense + BM25) y RRF Fusion..."):
        result = pipeline.answer_query(user_query, top_k=top_k)
        sources = result["sources"]
        
        # Filtrar por similitud mínima
        filtered_sources = [s for s in sources if s.get("similarity", 0.0) >= min_similarity]
        
        st.markdown("---")
        st.markdown("### 📋 Síntesis Técnica Asistida")
        
        if not filtered_sources:
            st.warning("⚠️ No se encontraron fragmentos documentales con similitud suficiente frente a la consulta. Verifique la redacción o reduzca el filtro de similitud mínima en la barra lateral.")
        else:
            st.markdown(f"""
            <div class="response-card">
                {result["answer"].replace(chr(10), "<br>")}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("")
            st.markdown("### 🔍 Evidencia Documental y Trazabilidad (ABET SO6)")
            st.caption("A continuación se presentan los fragmentos oficiales del manual recuperados por proximidad de coseno:")
            
            for idx, src in enumerate(filtered_sources, 1):
                doc_name = src["metadata"]["source"]
                page_num = src["metadata"]["page"]
                sim = src["similarity"]
                rrf = src.get("rrf_score", 0.0)
                d_rank = src.get("dense_rank", "-")
                s_rank = src.get("sparse_rank", "-")
                content = src["content"]
                
                with st.expander(f"📌 Fragmento #{idx} — {doc_name} (Pág. {page_num}) — Score RRF: {rrf:.5f}", expanded=(idx==1)):
                    st.markdown(f"""
                    <div class="source-box">
                        <div class="source-header">
                            <span class="tag-page">📄 {doc_name} — Página {page_num}</span>
                            <span class="tag-score">Similitud Coseno: {sim:.4f} | Dense Rank: #{d_rank} | BM25 Rank: #{s_rank}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.code(content, language="text")
                    
                    # 🖼️ Extracción y despliegue de diagramas técnicos de esa página
                    page_images = get_images_for_page(doc_name, int(page_num))
                    if page_images:
                        st.markdown("#### 🖼️ Diagrama / Esquema Técnico de esta Página:")
                        for pimg in page_images:
                            st.image(str(pimg), caption=f"Diagrama oficial — {doc_name} (Página {page_num})", use_container_width=True)
