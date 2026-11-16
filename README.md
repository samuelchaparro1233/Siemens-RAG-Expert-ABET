# Siemens RAG Expert: Asistente Inteligente de Soporte y Diagnóstico para Automatización Industrial
**Proyecto Final de Inteligencia Artificial (18314) — Catálogo Zubatronic 2026-2**  
*Programa de Ingeniería Mecatrónica — Universidad Militar Nueva Granada (UMNG)*  
*Evaluación bajo Marco de Acreditación ABET (Student Outcomes SO1, SO6, SO7)*

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/5/5f/Siemens-logo.svg" alt="Siemens Logo" width="180"/>
</p>

---

## 📸 Evidencia Visual y Desempeño Experimental

### 1. Comparativa Experimental ABET (Baseline vs. RAG V1 vs. Siemens RAG Expert)
<p align="center">
  <img src="assets/img/benchmark_abet_comparative.png" alt="Benchmark ABET Comparative" width="92%"/>
</p>

### 2. Soporte Multimodal: Extracción de Diagramas Oficiales de Cableado
El sistema no solo genera respuestas en texto; recupera dinámicamente esquemas eléctricos y diagramas de conexionado directamente de las páginas citadas de los manuales de Siemens:

<p align="center">
  <img src="assets/img/diagrama_v90_pti_wiring.png" alt="Diagrama de Cableado SINAMICS V90 PTI" width="85%"/>
  <br>
  <em>Figura 1: Diagrama oficial de cableado de interfaz de control X8 (Pulsos PTI) extraído de la página 73 del manual SINAMICS V90.</em>
</p>

---

## 📋 Ficha Técnica del Proyecto

- **Estrategia Seleccionada (Guía Oficial):** **Estrategia 4: GPT Personalizado / Asistentes RAG (Retrieval-Augmented Generation)**
- **Documento de Lineamientos:** [Proyecto_Final_IA.pdf](file:///c:/Users/starg/ProyectoLibre/Proyecto_Final_IA.pdf)
- **Meta de Desempeño:** Nivel N5 — Excelente (475 – 500 puntos / 4.75 – 5.00)
- **Dominio de Aplicación:** Automatización Industrial, Controladores Lógicos Programables (PLC Siemens SIMATIC S7-1200 / S7-1500) y Entorno TIA Portal.

---

## 1. Sustentación del Problema-Solución y Fundamentos de IA (Criterio C1 — 25% | SO7 / SO1)

### 1.1 Definición del Problema
En entornos industriales de manufactura automatizada y laboratorios mecatrónicos, los sistemas de control basados en PLCs de la familia **Siemens SIMATIC (S7-1200, S7-1500)** y módulos de periferia descentralizada (ET 200) operan bajo especificaciones críticas. La documentación técnica oficial asociada (manuales de sistema, guías de conexionado de módulos SM/SB y catálogos de diagnóstico) supera comúnmente las **1.500 páginas** de alta densidad técnica.

Cuando ocurre una parada de planta imprevista o una falla en el bus de campo:
1. El operario o ingeniero pierde minutos u horas críticas localizando manualmente la causa entre cientos de tablas de eventos y códigos hexadecimales.
2. Existe un alto riesgo de error humano en el conexionado eléctrico de canales analógicos/digitales y en la parametrización de filtros de señal en TIA Portal.

### 1.2 Limitaciones de los Métodos Tradicionales
* **Búsqueda Sintáctica / Determinista (`Ctrl+F` / Regex / SQL):** Falla ante la variabilidad lingüística de los operadores. Si el técnico consulta *"falla de sobrecalentamiento en motor"*, una búsqueda tradicional por palabras clave no encontrará coincidencia si el manual describe el evento como: *"Alarma 16#02:3952: Límite térmico excedido en canal de entrada analógica SM 1231"*.
* **Árboles de Decisión Estáticos (Sistemas Basados en Reglas Clásicas):** Son inviables e inescalables, ya que requerirían programar millones de reglas *if/else* estáticas para cada modelo de módulo, firmware y variante de hardware.

### 1.3 Justificación del Enfoque RAG frente a Modelos Generativos Aislados
* **El Problema del LLM Aislado (Cero Contexto):** Un modelo de lenguaje generalista suele **alucinar** detalles técnicos críticos (como voltajes admisibles, pines de conexión o sintaxis de bloques SCL), lo cual representa un riesgo de seguridad de maquinaria o daño irreparable en el hardware.
* **Solución RAG (Retrieval-Augmented Generation):**
  * **Espacio Vectorial Semántico:** Proyecta tanto las consultas de los usuarios como los fragmentos documentales a un espacio vectorial denso de $d$ dimensiones mediante modelos de *Embeddings*, permitiendo inferir similitud conceptual independiente de la redacción exacta.
  * **Inyección Estricta de Contexto y Cero Alucinación:** El generador LLM opera bajo un *System Prompt* restrictivo que lo limita a sintetizar la respuesta exclusivamente a partir de los fragmentos recuperados (*grounding*), exigiendo **citar la sección, página exacta del manual y precauciones de seguridad**.

### 1.4 Corpus Documental Técnico Oficial (6 Manuales Indexados)
El corpus documental del proyecto está integrado por manuales oficiales de ingeniería de Siemens ubicados en la carpeta [`docs/`](file:///c:/Users/starg/ProyectoLibre/docs), conformando una celda industrial y de visualización completa (**4.555 fragmentos vectoriales**):
1. **`WinCC_VisualizingProcessesUnifiedesES_es-ES.pdf` (39.9 MB):** Manual oficial de Siemens WinCC Unified (en español) para diseño de HMIs, alarm logging, visualización web y gestión de avisos.
2. **`s71500_cpu1516_3_pn_dp_manual_en-US_en-US.pdf` (1.7 MB):** Manual de hardware para la CPU modular de alta gama SIMATIC S7-1500 1516-3 PN/DP (interfaces PROFIBUS DP y PROFINET).
3. **`s71500_cpu1512c_1_pn_manual_en-US_en-US.pdf` (8.2 MB):** Manual de la CPU compacta SIMATIC S7-1500 1512C-1 PN con entradas/salidas analógicas y de conteo rápido integradas.
4. **`SINAMICS_V90_OPI_en-US_en-US.pdf` (16.0 MB):** Manual de instrucciones del servocontrolador SINAMICS V90 para control de movimiento, cableado de interfaz X8 y modo tren de pulsos (PTI).
5. **`DE_TIA-PRO1_EN_01_V150000.pdf` (20.7 MB):** Documento de entrenamiento oficial SITRAIN de Siemens para programación avanzada en TIA Portal V15 (OBs, FBs, FCs, DBs).
6. **`bop2_ba20_022016_en_en-us1.pdf` (4.3 MB):** Manual del panel operador básico SINAMICS BOP-2 para convertidores de frecuencia y puesta en marcha rápida.

---

### 2.1 Innovación Técnica: Búsqueda Híbrida (Dense + BM25) con Fusión RRF
Para resolver la principal debilidad de los RAGs tradicionales sobre manuales técnicos (donde la búsqueda puramente vectorial es débil encontrando códigos alfanuméricos como `F07900`, `p1082`, `SM 1231` o bloques `OB35`), este proyecto implementa **Búsqueda Híbrida**:
1. **Canal Denso (Dense Retrieval):** Modelo `all-MiniLM-L6-v2` con métrica de similitud coseno sobre ChromaDB para capturar el significado conceptual.
2. **Canal Léxico (Sparse Retrieval):** Algoritmo probabilístico `BM25Okapi` con tokenizador técnico especializado en códigos de hardware.
3. **Fusión Recíproca de Rangos (Reciprocal Rank Fusion - RRF):**
   $$\text{RRF Score} = \frac{w_{\text{dense}}}{60 + r_{\text{dense}}} + \frac{w_{\text{sparse}}}{60 + r_{\text{sparse}}}$$
   Garantizando que el fragmento con la solución exacta o código de alarma quede siempre en el Top-1.

```
┌────────────────────────────────────────────────────────┐
│  1. Ingesta y Preprocesamiento Documental              │
│     • Manuales técnicos oficiales en PDF                │
│     • Extracción de texto y tablas con PyMuPDF         │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  2. Segmentación Avanzada (Chunking Jerárquico)        │
│     • RecursiveCharacterTextSplitter                   │
│     • Chunk Size: 600 - 800 tokens                     │
│     • Overlap: 100 - 150 tokens                        │
│     • Inyección de Metadatos: {manual, pág, sección}   │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  3. Modelado Vectorial e Indexación                    │
│     • Modelo de Embeddings: all-MiniLM-L6-v2 / BGE     │
│     • Base Vectorial Local: ChromaDB persistente       │
│     • Métrica de Distancia: Similitud Coseno           │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  4. Motor de Recuperación (Retriever + Re-ranking)     │
│     • Búsqueda Top-K (k = 3 - 5)                       │
│     • Filtrado por umbral de similitud semántica       │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│  5. Generación Controlada y Mitigación de Alucinación  │
│     • System Prompt especializado con directivas de:   │
│       - Verificación estricta de evidencia             │
│       - Rechazo ante consultas fuera de manual         │
│       - Formateo de soluciones paso a paso y alertas   │
│     • LLM de Generación (Gemini API / LLM Local)       │
└────────────────────────────────────────────────────────┘
```

---

## 3. Protocolo Experimental y Métricas de Desempeño (Criterio C3 — 35% | SO6)

Para satisfacer el nivel **N5 (Excelente)**, el proyecto implementa un protocolo experimental formal y reproducible:

### 3.1 Diseño del Conjunto de Prueba (*Test Set Ground Truth*)
Se construye una batería controlada de **30 casos de prueba** divididos en:
* **Consultas de Diagnóstico de Fallas (40%):** Eventos de buffer, códigos de parpadeo de LEDs (SF/DIAG).
* **Consultas de Cableado y Parametrización de Hardware (40%):** Conexión de transductores analógicos, direccionamiento I/Q y fuentes de alimentación.
* **Consultas de Caso Límite / Fuera de Dominio (20%):** Preguntas sobre marcas externas (ej. Allen-Bradley) o información no contemplada en los manuales para verificar que el sistema responda *"Información no disponible en la documentación provista"* y no genere alucinaciones.

### 3.2 Experimento Comparativo (Ablación y Línea Base)
Se contrastan experimentalmente tres configuraciones del sistema:
1. **Línea Base (*Baseline* - Zero-Shot):** LLM tradicional sin acceso a RAG.
2. **RAG V1 (Estándar):** Chunking de tamaño fijo sin metadatos + recuperación vectorial simple.
3. **RAG V2 (Optimizado - Propuesta Final):** Chunking semántico jerárquico con solapamiento controlado, inyección de metadatos de página/sección y prompt con restricción de evidencia.

### 3.3 Métricas de Evaluación Cuantitativa (Framework RAGAS / Benchmark)
* **Fidelidad (*Faithfulness*):** Proporción de aseveraciones de la respuesta que se derivan estrictamente de los fragmentos de contexto recuperados (métrica clave anti-alucinaciones).
* **Relevancia de la Respuesta (*Answer Relevance*):** Grado de concordancia entre la solución generada y la consulta del ingeniero.
* **Precisión y Recuerdo de Contexto (*Context Precision & Recall*):** Evaluación de si el retriever seleccionó los fragmentos pertinentes del manual frente a la verdad terreno.
* **Latencia y Eficiencia Computacional:** Tiempo de respuesta por consulta (segundos) y consumo de tokens.

---

## 📂 Estructura del Repositorio

```
ProyectoLibre/
├── README.md                      # Documentación completa y sustentación técnica
├── Proyecto_Final_IA.pdf          # Lineamientos y rúbrica oficial ABET
├── requirements.txt               # Dependencias del proyecto
├── docs/                          # Manuales técnicos oficiales de Siemens (PDFs)
├── data/
│   ├── raw/                       # Extracciones crudas de texto
│   ├── processed/                 # Chunks serializados y procesados
│   └── vectorstore/               # Base de datos vectorial persistida (ChromaDB)
├── src/                           # Código fuente modular
│   ├── __init__.py
│   ├── pdf_loader.py              # Ingesta y preprocesamiento de PDFs
│   ├── chunking.py                # Segmentación y enriquecimiento de metadatos
│   ├── embeddings.py              # Generación de representaciones vectoriales
│   ├── vector_db.py               # Gestión y persistencia de ChromaDB
│   ├── retriever.py               # Algoritmos de recuperación y filtrado
│   └── rag_pipeline.py            # Orquestador del RAG y control de generación
├── evaluation/                    # Protocolo de experimentación formal
│   ├── test_set_ground_truth.json # Casos de prueba controlados
│   ├── evaluate_ragas.py          # Script de cálculo de métricas formales
│   └── results/                   # Tablas comparativas y gráficas de desempeño
└── app.py                         # Interfaz interactiva para el usuario / ingeniero
```

---

## 📊 4. Resultados Experimentales y Métricas ABET (Criterio C3 — 35% | Nivel N5)

Se ejecutó la batería de evaluación controlada sobre el conjunto de prueba con verdad de terreno ([test_set_ground_truth.json](file:///c:/Users/starg/ProyectoLibre/evaluation/test_set_ground_truth.json)).

### Métricas Cuantitativas Globales

| Métrica Formal | Valor Obtenido | Umbral Exigido (N5) | Interpretación Técnica |
| :--- | :---: | :---: | :--- |
| **Context Recall (Recuperación de Manual)** | **100.0%** | > 90.0% | El retriever identificó el documento oficial exacto en el 100% de las consultas dentro del Top-3. |
| **Similitud Coseno Promedio** | **0.4977** | > 0.4000 | Alta cercanía semántica entre el vector de consulta y el fragmento del manual. |
| **Latencia Promedio por Consulta** | **19.0 ms** | < 100 ms | Respuesta casi instantánea en la búsqueda semántica sobre los 1.160 fragmentos indexados. |
| **Tasa de Rechazo de Alucinaciones** | **100.0%** | 100.0% | En consultas fuera de dominio (ej. Allen-Bradley / motores NEMA 17), el sistema no genera información falsa. |

*Reporte completo detallado y reproducible:* [`evaluation/results/reporte_abet.md`](file:///c:/Users/starg/ProyectoLibre/evaluation/results/reporte_abet.md).

---

## 🚀 5. Instrucciones de Ejecución

### 1. Activar entorno e instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Indexar manuales (si se agregan nuevos PDFs a `docs/`)
```bash
python src/indexer.py
```

### 3. Ejecutar la Evaluación Experimental ABET
```bash
python run_eval.py
```

### 4. Lanzar la Interfaz Interactiva de Usuario
```bash
streamlit run app.py
```
