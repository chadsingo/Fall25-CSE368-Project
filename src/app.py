import os
import json
import numpy as np
from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer, util
from utils.generate_suggestion import generate_suggestion

# === Load Models and Data ===
model = SentenceTransformer("all-MiniLM-L6-v2")

# Load processed slides
with open("lecture_data.json") as f:
    slides = json.load(f)

# Load vector store
with open("vector_store.json") as f:
    vector_store = json.load(f)

app = Flask(__name__)

@app.route("/suggest", methods=['POST'])
def suggest():
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "No question provided."}), 400

    # Compute embedding for question
    q_emb = model.encode(question)
    scores = np.array([util.cos_sim(q_emb, v["embedding"])[0][0] for v in vector_store])

    # Rank scores (descending) — take top 10 candidates
    top_indices = np.argsort(scores)[::-1][:10]

    best_chunk = None
    linked_slide = None
    best_idx = None

    # Prefer meaningful chunks (not just titles)
    for idx in top_indices:
        candidate_chunk = vector_store[int(idx)]
        chunk_text = candidate_chunk["chunk"]

        if len(chunk_text) < 50:
            continue

        if any(keyword in chunk_text.lower() for keyword in [" is ", " refers to ", " allows ", " helps ", " used to "]):
            linked_slide = next(
                (s for s in slides if s["file_name"] == candidate_chunk["file_name"] and s.get("text", "").strip()),
                None
            )
            if linked_slide:
                best_chunk = candidate_chunk
                best_idx = int(idx)
                break

    # Fallback if no good explanations found
    if linked_slide is None:
        best_idx = int(np.argmax(scores))
        best_chunk = vector_store[best_idx]
        linked_slide = next((s for s in slides if s["file_name"] == best_chunk["file_name"]), None)

    # Final answer generation (LLM)
    suggestion = generate_suggestion({
        "question": question,
        "related_slide": linked_slide,
        "related_chunk": best_chunk["chunk"],
        "similarity": float(scores[best_idx]),
    })

    # 🔥 Return improved response — include *actual matched content*
    return jsonify({
        "question": question,
        "suggested_answer": suggestion,
        "most_relevant_slide": {
            "file_name": linked_slide["file_name"],
            "page_number": linked_slide.get("page_number", None),
            "slide_title": linked_slide.get("text", "")[:100],  # shorter preview
            "matched_content": best_chunk["chunk"],  # 🎯 This is the relevant chunk!
        },
        "similarity_score": float(scores[best_idx]),
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "running"}), 200

if __name__ == "__main__":
    print("🚀 Backend running at http://127.0.0.1:5000")
    app.run(debug=True)
