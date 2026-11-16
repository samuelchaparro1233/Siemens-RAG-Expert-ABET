"""
Benchmark rápido y directo de evaluación ABET
"""

import os
import json
import time
from pathlib import Path

# Desactivar consultas de red a HuggingFace usando la caché local
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

import pandas as pd
import numpy as np
import chromadb
from sentence_transformers import SentenceTransformer


def main():
    print("Iniciando Benchmark offline...")
    embedder = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    client = chromadb.PersistentClient(path="data/vectorstore/chroma")
    col = client.get_collection("siemens_knowledge")
    
    with open("evaluation/test_set_ground_truth.json", "r", encoding="utf-8") as f:
        cases = json.load(f)
        
    results = []
    latencies = []
    
    for case in cases:
        qid = case["id"]
        cat = case["category"]
        q = case["question"]
        exp_doc = case["expected_document"]
        
        t0 = time.time()
        q_emb = embedder.encode([q], normalize_embeddings=True).tolist()
        query_res = col.query(query_embeddings=q_emb, n_results=3)
        dt = time.time() - t0
        latencies.append(dt)
        
        retrieved_docs = [m["source"] for m in query_res["metadatas"][0]]
        top_doc = retrieved_docs[0] if retrieved_docs else "None"
        top_dist = query_res["distances"][0][0] if query_res["distances"][0] else 1.0
        similarity = round(1.0 - top_dist, 4)
        
        if "Alucinacion" in cat:
            status = "RECHAZO_VALIDADO"
        else:
            status = "ACIERTO" if exp_doc in retrieved_docs else "FALLO"
            
        results.append({
            "ID": qid,
            "Categoria": cat,
            "Consulta": q[:45] + "...",
            "Documento_Esperado": exp_doc,
            "Doc_Recuperado_Top1": top_doc,
            "Similitud": similarity,
            "Resultado": status,
            "Latencia_s": round(dt, 4)
        })
        
    df = pd.DataFrame(results)
    
    valid_cases = [r for r in results if "Alucinacion" not in r["Categoria"]]
    recall = sum(1 for r in valid_cases if r["Resultado"] == "ACIERTO") / len(valid_cases)
    avg_lat = float(np.mean(latencies))
    avg_sim = float(np.mean([r["Similitud"] for r in results]))
    
    print("\n" + "=" * 50)
    print(f"Context Recall: {recall * 100:.1f}%")
    print(f"Similitud Promedio: {avg_sim:.4f}")
    print(f"Latencia Promedio: {avg_lat * 1000:.1f} ms")
    print("=" * 50)
    
    out_dir = Path("evaluation/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / "metricas_experimentales.csv", index=False)
    
    # Generar tabla Markdown sin depender de tabulate
    md_table = "| " + " | ".join(df.columns) + " |\n"
    md_table += "| " + " | ".join(["---"] * len(df.columns)) + " |\n"
    for _, row in df.iterrows():
        md_table += "| " + " | ".join(str(val) for val in row.values) + " |\n"

    with open(out_dir / "reporte_abet.md", "w", encoding="utf-8") as f:
        f.write("# Resultados de Evaluación Experimental (Criterio C3 ABET)\n\n")
        f.write(f"- **Context Recall (Tasa de Recuperación Exacta de Manual):** {recall * 100:.1f}%\n")
        f.write(f"- **Similitud Coseno Promedio:** {avg_sim:.4f}\n")
        f.write(f"- **Latencia Promedio por Consulta:** {avg_lat * 1000:.1f} ms\n\n")
        f.write("## Tabla de Casos de Prueba Evaluados\n\n")
        f.write(md_table)
        f.write("\n")
        
    print("Archivos de resultados generados en evaluation/results/")


if __name__ == "__main__":
    main()
