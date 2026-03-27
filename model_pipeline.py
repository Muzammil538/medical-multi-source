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

# Load embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# =========================
# LOAD DATA
# =========================

def load_data():
    clinical = pd.read_csv("synthetic_clinical_dataset.csv")
    research = pd.read_csv("medical_text_classification_fake_dataset.csv")
    qa = pd.read_csv("train.csv")
    return clinical, research, qa

clinical_df, research_df, qa_df = load_data()

# =========================
# TEXT CONVERSION
# =========================

def clinical_text(row):
    return f"Clinical: Age {row['Age']}, Condition {row['Medical_Condition']}, Test {row['Test_Results']}"

def research_text(row):
    return f"Research: {row['text']}"

def qa_text(row):
    options = [row['opa'], row['opb'], row['opc'], row['opd']]
    return f"Q: {row['question']} A: {options[int(row['cop'])]}"

clinical_docs = clinical_df.apply(clinical_text, axis=1).tolist()
research_docs = research_df.apply(research_text, axis=1).tolist()
qa_docs = qa_df.apply(qa_text, axis=1).tolist()

# =========================
# BUILD FAISS
# =========================

def build_index(docs):
    emb = embedding_model.encode(docs)
    index = faiss.IndexFlatL2(emb.shape[1])
    index.add(np.array(emb))
    return index

clinical_index = build_index(clinical_docs)
research_index = build_index(research_docs)
qa_index = build_index(qa_docs)

# =========================
# RETRIEVE
# =========================

def retrieve(query, top_k=2):
    q_emb = embedding_model.encode([query])

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
        "clinical": search(clinical_index, clinical_docs),
        "research": search(research_index, research_docs),
        "qa": search(qa_index, qa_docs)
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