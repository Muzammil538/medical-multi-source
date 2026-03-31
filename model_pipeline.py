import os
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import requests

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = "arcee-ai/trinity-large-preview:free"

# Load embedding model lazily to avoid import-time issues.
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedding_model

# =========================
# CACHE AND DATA
# =========================

_clinical_df = None
_research_df = None
_qa_df = None
_clinical_docs = None
_research_docs = None
_qa_docs = None
_clinical_index = None
_research_index = None
_qa_index = None

def load_data():
    clinical = pd.read_csv("healthcare_dataset.csv")
    research = pd.read_csv("medical_text_classification_fake_dataset.csv")
    qa = pd.read_csv("train.csv")
    return clinical, research, qa

# =========================
# TEXT CONVERSION
# =========================

def clinical_text(row):
    return (
        f"Clinical: Name {row.get('Name', 'N/A')}, Age {row.get('Age', 'N/A')}, "
        f"Gender {row.get('Gender', 'N/A')}, Blood Type {row.get('Blood Type', 'N/A')}, "
        f"Medical Condition {row.get('Medical Condition', 'N/A')}, "
        f"Test Results {row.get('Test Results', 'N/A')}"
    )

def research_text(row):
    return f"Research: {row['text']}"

def qa_text(row):
    options = [row['opa'], row['opb'], row['opc'], row['opd']]
    return f"Q: {row['question']} A: {options[int(row['cop'])]}"

# =========================
# INITIALIZATION
# =========================

def initialize():
    global _clinical_df, _research_df, _qa_df
    global _clinical_docs, _research_docs, _qa_docs
    global _clinical_index, _research_index, _qa_index

    if _clinical_index is not None:
        return

    _clinical_df, _research_df, _qa_df = load_data()
    _clinical_docs = _clinical_df.apply(clinical_text, axis=1).tolist()
    _research_docs = _research_df.apply(research_text, axis=1).tolist()
    _qa_docs = _qa_df.apply(qa_text, axis=1).tolist()

    _clinical_index = build_index(_clinical_docs)
    _research_index = build_index(_research_docs)
    _qa_index = build_index(_qa_docs)

# =========================
# BUILD FAISS
# =========================

def build_index(docs):
    emb = get_embedding_model().encode(docs, show_progress_bar=False)
    index = faiss.IndexFlatL2(emb.shape[1])
    index.add(np.array(emb))
    return index

# Initialize lazily only when the first query runs.

# =========================
# RETRIEVE
# =========================

def retrieve(query, top_k=2):
    initialize()
    q_emb = get_embedding_model().encode([query])

    def search(index, docs):
        D, I = index.search(q_emb, top_k)
        results = []
        for dist, idx in zip(D[0], I[0]):
            score = float(1 / (1 + dist))
            results.append({
                "text": docs[idx],
                "score": round(score, 3)
            })
        return results

    return {
        "clinical": search(_clinical_index, _clinical_docs),
        "research": search(_research_index, _research_docs),
        "qa": search(_qa_index, _qa_docs)
    }


# =========================
# LLM
# =========================

def call_llm(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Provide structured medical guidance."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    res = requests.post("https://openrouter.ai/api/v1/chat/completions",
                        headers=headers, json=data)

    result = res.json()
    if "choices" in result:
        return result["choices"][0]["message"]["content"]
    return "LLM error"

# =========================
# MAIN
# =========================

def process_query(user_profile, question):

    retrieved = retrieve(question)

    context = ""
    sources = []

    for source_type, items in retrieved.items():
        for item in items:
            context += item["text"] + "\n"
            sources.append({
                "type": source_type,
                "score": item["score"],
                "text": item["text"]
            })

    prompt = f"""
Patient:
Age: {user_profile.get('age')}
Gender: {user_profile.get('gender')}
Condition: {user_profile.get('medical_condition')}

Context:
{context}

Question:
{question}

Respond strictly in this format:

Symptoms:
- ...

Precautions:
- ...

Steps:
1. ...
2. ...

Reasoning:
Explain briefly how the answer is derived from context.
"""

    answer = call_llm(prompt)

    # 🔥 SIMPLE EVALUATION METRICS
    avg_score = round(sum([s["score"] for s in sources]) / len(sources), 2)

    evaluation = {
        "confidence": avg_score,
        "num_sources": len(sources)
    }

    return answer, sources, evaluation
