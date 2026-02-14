import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import requests
import json

# ==========================
# LOAD DATASETS
# ==========================

train_df = pd.read_csv("train.csv")
val_df = pd.read_csv("validation.csv")

qa_df = pd.concat([train_df, val_df], ignore_index=True)
qa_df = qa_df.sample(min(500, len(qa_df)), random_state=42)

def convert_mcq(row):
    options = [row['opa'], row['opb'], row['opc'], row['opd']]
    correct = options[int(row['cop'])]
    return f"Question: {row['question']} Answer: {correct}"

qa_texts = qa_df.apply(convert_mcq, axis=1).tolist()

research_df = pd.read_csv("medical_text_classification_fake_dataset.csv")
research_df = research_df.sample(min(300, len(research_df)), random_state=42)

research_texts = research_df["text"].dropna().tolist()

all_documents = qa_texts + research_texts

print("Total knowledge entries loaded:", len(all_documents))

# ==========================
# SIMPLE TF-IDF RETRIEVAL
# ==========================

vectorizer = TfidfVectorizer(stop_words='english')
doc_vectors = vectorizer.fit_transform(all_documents)

def retrieve_context(query, top_k=3):
    query_vec = vectorizer.transform([query])
    similarities = cosine_similarity(query_vec, doc_vectors)
    top_indices = similarities[0].argsort()[-top_k:][::-1]
    return [all_documents[i] for i in top_indices]

# ==========================
# OPENROUTER LLM
# ==========================

OPENROUTER_API_KEY = "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"
MODEL_NAME = "arcee-ai/trinity-large-preview:free"

def call_llm(prompt):

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a medical assistant."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=data
    )

    # print("Status Code:", response.status_code)
    # print("Response:", response.text)

    result = response.json()

    if response.status_code == 200 and "choices" in result:
        return result["choices"][0]["message"]["content"]
    else:
        return f"API Error: {result}"


# ==========================
# MAIN FUNCTION
# ==========================

def process_query(user_profile, question):

    context = retrieve_context(question)

    prompt = f"""
Patient:
Age: {user_profile.get('age')}
Gender: {user_profile.get('gender')}
Condition: {user_profile.get('medical_condition')}

Medical Context:
{' '.join(context)}

Question:
{question}

Provide medical guidance without diagnosis.
"""

    answer = call_llm(prompt)

    return answer, context
