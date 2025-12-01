import os
import json
import numpy as np
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer, util
from utils.generate_suggestion import generate_suggestion

# === Load Models and Data ===
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load processed pages (with text + image)
with open("lecture_data.json") as f:
    slides = json.load(f)

# Load vector store (chunked embeddings)
with open("vector_store.json") as f:
    vector_store = json.load(f)

# ======================
# 🔍 DEBUG: Print top 5 vector chunks for "What is an IDS?"
# ======================
test_question = "What is an IDS?"
test_emb = model.encode(test_question)
scores = np.array([util.cos_sim(test_emb, v["embedding"])[0][0] for v in vector_store])
top_idxs = np.argsort(scores)[::-1][:5]

print("\n🔍 DEBUG — Top 5 Chunk Matches for test question:")
for i in top_idxs:
    chunk_text = vector_store[int(i)]["chunk"]
    clean_preview = chunk_text.replace("\n", " ").replace("\r", " ")[:200]
    print(f"➡ Score: {scores[i]:.4f} | Text: \"{clean_preview}…\"")
print("====================================================\n")

app = Flask(__name__)


@app.route("/suggest", methods=['POST'])
def suggest():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "No question provided."}), 400

    # 1. Create embedding for the instructor's question
    q_emb = model.encode(question)

    # 2. Compute cosine similarity to each chunk embedding
    scores = np.array([util.cos_sim(q_emb, v["embedding"])[0][0] for v in vector_store])

    # 3. Sort chunks by similarity (descending)
    top_indices = np.argsort(scores)[::-1][:10]

    best_chunk = None
    linked_slide = None
    best_idx = None

    # Try to find a meaningful chunk (avoid title/short text)
    for idx in top_indices:
        candidate_chunk = vector_store[int(idx)]
        chunk_text = candidate_chunk["chunk"]

        # Minimum chunk length to avoid pure titles
        if len(chunk_text) < 50:
            continue

        # Prefer explanatory language
        if any(keyword in chunk_text.lower() for keyword in [" is ", " refers to ", " allows ", " helps ", " used to "]):
            linked_slide = next(
                (s for s in slides
                 if s["file_name"] == candidate_chunk["file_name"] and s.get("text", "").strip()),
                None
            )
            if linked_slide:
                best_chunk = candidate_chunk
                best_idx = int(idx)
                break

    # If no meaningful match found, fallback to the highest score
    if linked_slide is None:
        best_idx = int(np.argmax(scores))
        best_chunk = vector_store[best_idx]
        linked_slide = next(
            (s for s in slides if s["file_name"] == best_chunk["file_name"]),
            None
        )

    print("\n🔍 Top 5 Chunks by Similarity:")
    for i in top_indices[:5]:
        print(f"\n[Rank {i}] Score: {scores[i]}")
        print(f"Chunk: {vector_store[int(i)]['chunk'][:250]}…")

    # 4. Now safely generate response
    suggestion = generate_suggestion({
        "question": question,
        "related_slide": linked_slide,
        "related_chunk": best_chunk["chunk"],
        "similarity": float(scores[best_idx]),
    })

    return jsonify({
        "question": question,
        "suggested_answer": suggestion,
        "most_relevant_slide": linked_slide,
        "similarity_score": float(scores[best_idx]),
        "chunk_used": best_chunk["chunk"]
    })


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200


if __name__ == "__main__":
    print("🚀 Backend running at http://127.0.0.1:5000")
    app.run(debug=True)
