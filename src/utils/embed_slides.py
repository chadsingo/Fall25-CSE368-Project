import json
import numpy as np
from sentence_transformers import SentenceTransformer

# Load processed slides
with open("slides.json") as f:
    slides = json.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

# Only embed textual content (can add image features later)
embeddings = model.encode([slide["text"] for slide in slides])

np.save("embeddings.npy", embeddings)

print(f"Saved embeddings for {len(slides)} slides to 'embeddings.npy'")
