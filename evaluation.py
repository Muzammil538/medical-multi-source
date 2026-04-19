import matplotlib.pyplot as plt
import numpy as np
from model_pipeline import retrieve

# -----------------------------
# SAMPLE TEST QUERIES
# -----------------------------
test_queries = [
    "What are symptoms of diabetes?",
    "How to treat hypertension?",
    "Causes of heart disease",
    "Symptoms of asthma",
    "Treatment for fever"
]

# Dummy ground truth (for demo)
ground_truth = [
    ["diabetes", "insulin"],
    ["hypertension", "blood pressure"],
    ["heart", "cardiac"],
    ["asthma", "breathing"],
    ["fever", "temperature"]
]

precision_list = []
recall_list = []
confidence_list = []
source_counts = []

# -----------------------------
# EVALUATION LOOP
# -----------------------------
for i, query in enumerate(test_queries):

    retrieved = retrieve(query)

    retrieved_texts = [
        item["text"] for v in retrieved.values() for item in v
    ]

    scores = [
        item["score"] for v in retrieved.values() for item in v
    ]

    # Precision & Recall
    hits = sum([1 for gt in ground_truth[i] if any(gt in r for r in retrieved_texts)])

    precision = hits / len(retrieved_texts)
    recall = hits / len(ground_truth[i])

    precision_list.append(precision)
    recall_list.append(recall)

    # Confidence
    confidence_list.append(np.mean(scores))

    # Source count
    source_counts.append(len(retrieved_texts))

# -----------------------------
# 1️⃣ PRECISION vs RECALL
# -----------------------------
plt.figure()
plt.plot(precision_list, label="Precision", marker='o')
plt.plot(recall_list, label="Recall", marker='o')
plt.title("Precision vs Recall")
plt.xlabel("Query Index")
plt.ylabel("Score")
plt.legend()
plt.grid()
plt.show()

# -----------------------------
# 2️⃣ CONFIDENCE DISTRIBUTION
# -----------------------------
plt.figure()
plt.hist(confidence_list)
plt.title("Confidence Score Distribution")
plt.xlabel("Confidence")
plt.ylabel("Frequency")
plt.grid()
plt.show()

# -----------------------------
# 3️⃣ SOURCE COUNT PER QUERY
# -----------------------------
plt.figure()
plt.bar(range(len(source_counts)), source_counts)
plt.title("Number of Sources Retrieved")
plt.xlabel("Query Index")
plt.ylabel("Sources")
plt.grid()
plt.show()

# -----------------------------
# 4️⃣ PERFORMANCE SUMMARY
# -----------------------------
print("\n--- MODEL PERFORMANCE ---")
print("Avg Precision:", round(np.mean(precision_list), 2))
print("Avg Recall:", round(np.mean(recall_list), 2))
print("Avg Confidence:", round(np.mean(confidence_list), 2))