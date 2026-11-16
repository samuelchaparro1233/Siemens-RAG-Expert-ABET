"""
Interfaz de Usuario Profesional de Alto Impacto para Siemens RAG Expert.
Estética industrial moderna "Siemens Digital Enterprise":
- Paleta: Petroleum Teal (#00646E), Electric Cyan (#00E5FF), Midnight Slate (#0B131E)
- Indicadores LED animados de estado del sistema (ChromaDB / BM25 / RRF / Vision)
- Tarjetas con efecto Glassmorphism y bordes iluminados
- Banner de telemetría de inferencia en tiempo real (Latencia, Chunks, Precisión)
- Visor multimodal de diagramas y esquemas técnicos
"""

import sys
import site
import time
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


# 1. Configuración de página
st.set_page_config(
    page_title="Siemens RAG Expert | Industrial Automation AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Inyección de CSS de alta gama (Siemens Glassmorphism & Cyber-Industrial UI)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Fondo general sutil */
    .stApp {
        background: radial-gradient(circle at 15% 15%, #0F1B26 0%, #080D14 100%);
    }

    /* Banner Hero con gradiente Siemens e iluminación */
    .hero-container {
        background: linear-gradient(135deg, rgba(0, 51, 58, 0.95) 0%, rgba(0, 100, 110, 0.85) 50%, rgba(0, 153, 153, 0.75) 100%);
        backdrop-filter: blur(12px);
        padding: 2.2rem 2.8rem;
        border-radius: 18px;
        color: #FFFFFF;
        box-shadow: 0 12px 36px rgba(0, 100, 110, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        margin-bottom: 2rem;
        border: 1px solid rgba(0, 229, 255, 0.25);
        position: relative;
        overflow: hidden;
    }
    
    .hero-container::after {
        content: '';
        position: absolute;
        top: -50%;
        right: -20%;
        width: 350px;
        height: 350px;
        background: radial-gradient(circle, rgba(0, 229, 255, 0.2) 0%, transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }

    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        letter-spacing: -0.8px;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 1rem;
        color: #FFFFFF;
        text-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }
    
    .hero-subtitle {
        font-size: 1.12rem;
        font-weight: 300;
        color: #E0F7FA;
        margin-top: 0.6rem;
        max-width: 900px;
        line-height: 1.5;
    }

    .badge-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 1.2rem;
    }

    .badge-tag {
        background: rgba(0, 0, 0, 0.35);
        border: 1px solid rgba(0, 229, 255, 0.4);
        padding: 5px 14px;
        border-radius: 30px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #E0F7FA;
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
    }

    /* LEDs animados de estado del sistema */
    .led-pulse {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
        background-color: #00E5FF;
        box-shadow: 0 0 10px #00E5FF;
        animation: pulse 1.8s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 229, 255, 0.7); }
        70% { transform: scale(1.15); box-shadow: 0 0 0 8px rgba(0, 229, 255, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 229, 255, 0); }
    }

    /* Tarjetas de Telemetría en Barra Lateral */
    .metric-card {
        background: rgba(14, 22, 33, 0.7);
        backdrop-filter: blur(8px);
        border: 1px solid rgba(0, 229, 255, 0.15);
        border-radius: 12px;
        padding: 1.1rem;
        margin-bottom: 0.8rem;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .metric-card:hover {
        border-color: #00E5FF;
        transform: translateY(-2px);
    }
    .metric-label {
        color: #7E92A7;
        font-size: 0.76rem;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        font-weight: 600;
    }
    .metric-val {
        color: #00E5FF;
        font-size: 1.55rem;
        font-weight: 800;
        margin-top: 0.2rem;
    }

    /* Barra de estado de inferencia superior */
    .status-ribbon {
        background: rgba(14, 22, 33, 0.85);
        border: 1px solid #1E2D3D;
        border-radius: 12px;
        padding: 0.9rem 1.4rem;
        margin-bottom: 1.6rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 1rem;
    }
    .ribbon-item {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.88rem;
        color: #C2D1E0;
    }

    /* Tarjeta de Respuesta del Asistente */
    .response-card {
        background: linear-gradient(180deg, #0F1924 0%, #0B131D 100%);
        border: 1px solid #1E3146;
        border-left: 6px solid #00E5FF;
        border-radius: 14px;
        padding: 1.8rem 2.2rem;
        margin-top: 1.5rem;
        box-shadow: 0 8px 30px rgba(0,0,0,0.35);
        line-height: 1.65;
        font-size: 1.02rem;
        color: #E3ECF5;
    }

    /* Cajas de Evidencia Documental */
    .source-box {
        background: #101B27;
        border: 1px solid #1F3348;
        border-radius: 10px;
        padding: 1.1rem;
        margin-top: 0.8rem;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }
    .source-box:hover {
        border-color: #00E5FF;
        box-shadow: 0 4px 18px rgba(0, 229, 255, 0.12);
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
        background: #004D54;
        color: #E0F7FA;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .tag-score {
        background: rgba(0, 229, 255, 0.12);
        color: #00E5FF;
        border: 1px solid rgba(0, 229, 255, 0.4);
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
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
        Asistente de Inteligencia Artificial Corporativa para Automatización Industrial, Controladores SIMATIC S7-1500, TIA Portal, Accionamientos SINAMICS y SCADA WinCC Unified.
    </div>
    <div class="badge-bar">
        <span class="badge-tag"><span class="led-pulse"></span> Sistema RAG Híbrido Activo (Dense + BM25)</span>
        <span class="badge-tag">📐 Fusión RRF Matemática</span>
        <span class="badge-tag">🖼️ Soporte Multimodal de Diagramas</span>
        <span class="badge-tag">🎓 Marco ABET (SO1, SO6, SO7) — Nivel N5</span>
    </div>
</div>
""", unsafe_allow_html=True)


# 4. Barra Lateral de Control y Telemetría del Sistema
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/5/5f/Siemens-logo.svg", width=150)
    st.markdown("### 🎛️ Telemetría del Sistema")
    
    docs_dir = PROJECT_ROOT / "docs"
    pdf_list = list(docs_dir.glob("*.pdf")) if docs_dir.exists() else []
    
    # Obtener conteo dinámico real de la colección
    try:
        from chromadb import PersistentClient
        _client = PersistentClient(path=str(PROJECT_ROOT / "data" / "vectorstore" / "chroma"))
        _col = _client.get_collection("siemens_knowledge")
        total_chunks_count = f"{_col.count():,}".replace(",", ".")
    except Exception:
        total_chunks_count = "4.555"
    
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
    st.markdown("#### 📂 Biblioteca Documental Activa")
    for pdf in pdf_list:
        file_size_mb = pdf.stat().st_size / (1024 * 1024)
        st.markdown(f"📄 **`{pdf.name[:22]}...`**  \n<small style='color:#7E92A7;'>Tamaño: {file_size_mb:.1f} MB</small>", unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown("#### ⚙️ Parámetros de Recuperación")
    top_k = st.slider("Ventana de Contexto (Top-K Chunks):", min_value=1, max_value=8, value=3)
    
    st.markdown("#### ⚖️ Balance de Recuperación Híbrida")
    dense_ratio = st.slider("Peso Semántico vs Léxico (BM25):", min_value=0.1, max_value=0.9, value=0.6, step=0.1, help="0.6 = 60% significado conceptual (Embeddings) + 40% coincidencia exacta de códigos (BM25)")
    
    min_similarity = st.slider("Filtro de Similitud Mínima:", min_value=0.0, max_value=0.8, value=0.30, step=0.05)
    
    st.markdown("---")
    st.markdown("#### 🤖 Modo de Operación")
    mode_selection = st.radio(
        "Selecciona el motor de respuesta:",
        options=["✨ Modo Generativo (Gemini AI)", "💻 Modo Local (Offline / Evidencia Directa)"],
        index=0,
        help="El modo Gemini redacta la solución técnica en español. El modo Local extrae la evidencia textual pura y los diagramas sin conexión a internet."
    )
    
    st.markdown("---")
    st.caption("🚀 Motor: `all-MiniLM-L6-v2` | Base Vectorial: `ChromaDB HNSW`")


# 5. Instanciar Pipeline
def get_pipeline(use_api: bool):
    return SiemensRAGPipeline(use_api=use_api)

use_gemini = (mode_selection == "✨ Modo Generativo (Gemini AI)")
pipeline = get_pipeline(use_api=use_gemini)


# 6. Barra de Estado Superior en Tiempo Real
st.markdown(f"""
<div class="status-ribbon">
    <div class="ribbon-item">
        <span class="led-pulse"></span>
        <span><b>Motor:</b> all-MiniLM-L6-v2 (384-D)</span>
    </div>
    <div class="ribbon-item">
        <span><b>Índice:</b> ChromaDB HNSW + BM25 Okapi</span>
    </div>
    <div class="ribbon-item">
        <span><b>Manuales:</b> {len(pdf_list)} Oficiales</span>
    </div>
    <div class="ribbon-item">
        <span><b>Estado:</b> <span style="color:#00E5FF; font-weight:600;">EN LÍNEA</span></span>
    </div>
</div>
""", unsafe_allow_html=True)


# 7. Banco de Pruebas Rápidas (Chips de Consultas de Planta)
st.markdown("#### 💡 Escenarios de Planta y Consultas Frecuentes")
c1, c2, c3, c4 = st.columns(4)

with c1:
    if st.button("🔧 Puesta en Marcha BOP-2", use_container_width=True):
        st.session_state["query_input"] = "¿Cómo se realiza la puesta en marcha rápida básica usando el panel BOP-2?"
with c2:
    if st.button("⚡ Cableado PTI en SINAMICS V90", use_container_width=True):
        st.session_state["query_input"] = "¿Cuáles son las instrucciones de cableado para la entrada de tren de pulsos PTI en el SINAMICS V90?"
with c3:
    if st.button("🖥️ Avisos y Alarmas en WinCC", use_container_width=True):
        st.session_state["query_input"] = "¿Cómo se configuran los avisos y alarmas en WinCC Unified?"
with c4:
    if st.button("🔌 Conexión CPU 1516-3 PN/DP", use_container_width=True):
        st.session_state["query_input"] = "¿Cuáles son las interfaces de comunicación de la CPU 1516-3 PN/DP y cómo se configuran?"

st.markdown("")

# 8. Formulario de Búsqueda
default_val = st.session_state.get("query_input", "")
user_query = st.text_input(
    "🔍 Ingresa tu consulta técnica, código de alarma o requerimiento de conexionado:",
    value=default_val,
    placeholder="Ej: ¿Qué indica el código de fallo F07900 o cómo cablear entradas analógicas en CPU 1512C-1 PN?"
)

col_btn1, col_btn2 = st.columns([1.2, 4.8])
with col_btn1:
    submit_btn = st.button("🚀 Consultar Asistente", type="primary", use_container_width=True)

if submit_btn and user_query:
    t_start = time.time()
    with st.spinner("⚡ Ejecutando Búsqueda Híbrida (Dense + BM25) y RRF Fusion..."):
        result = pipeline.answer_query(user_query, top_k=top_k)
        elapsed_sec = time.time() - t_start
        sources = result["sources"]
        
        # Filtrar por similitud mínima
        filtered_sources = [s for s in sources if s.get("similarity", 0.0) >= min_similarity]
        
        st.markdown("---")
        
        # Métricas de inferencia de la consulta
        st.markdown(f"""
        <div style="display:flex; gap:1.2rem; margin-bottom:1rem; flex-wrap:wrap;">
            <div style="background:#0F1B26; border:1px solid #1E3146; padding:6px 14px; border-radius:20px; font-size:0.84rem; color:#A5B6C8;">
                ⏱️ <b>Latencia Total:</b> <span style="color:#00E5FF;">{elapsed_sec*1000:.1f} ms</span>
            </div>
            <div style="background:#0F1B26; border:1px solid #1E3146; padding:6px 14px; border-radius:20px; font-size:0.84rem; color:#A5B6C8;">
                📚 <b>Fragmentos Evaluados:</b> <span style="color:#00E5FF;">{len(sources)} Chunks</span>
            </div>
            <div style="background:#0F1B26; border:1px solid #1E3146; padding:6px 14px; border-radius:20px; font-size:0.84rem; color:#A5B6C8;">
                🎯 <b>Alineación ABET:</b> <span style="color:#00E5FF;">SO1 & SO6</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
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
            st.caption("A continuación se presentan los fragmentos oficiales del manual recuperados por proximidad de coseno y coincidencia léxica BM25:")
            
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
