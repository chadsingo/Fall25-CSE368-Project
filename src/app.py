from flask import Flask, request, jsonify
import json
import numpy as np
from sentence_transformers import SentenceTransformer, util

from utils.generate_suggestion import generate_suggestion
app = Flask(__name__)


# Load model + data
model = SentenceTransformer("all-MiniLM-L6-v2")

with open("slides.json") as f:
    slides = json.load(f)

embeddings = np.load("embeddings.npy")  # shape: (N, 384)




@app.route("/")
def hello_world():

    return "<p>Hello, World!</p>"


@app.route("/suggest", methods=['POST'])
def suggest():
    data = request.get_json()
    question = data.get('question', '')

    if not question:
        return jsonify({"error": "No question supplied"}), 400
    
    q_emb = model.encode(question)

    scores = util.cos_sim(q_emb, embeddings)[0]
    top_idx = np.argsort(-scores)[:3]

    top_slides = [slides[i] for i in top_idx]

    suggestion = generate_suggestion(question)


    # TODO: later add GPT to generate conceptual hint
    return jsonify({
        "question": question,
        "top_slides": top_slides,
        "scores": [float(scores[i]) for i in top_idx],
        "suggested_answer": "AI backend working! GPT integration coming soon."
    })



if __name__ == "__main__":
    app.run(port=5000)