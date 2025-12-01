# src/utils/build_vector_store.py
import json
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

INPUT_FILE = "../lecture_data.json"
OUTPUT_FILE = "../vector_store.json"

model = SentenceTransformer("all-MiniLM-L6-v2")
splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
vector_data = []

print("🔁 Loading slides...")
with open(INPUT_FILE) as f:
    slides = json.load(f)

for slide in slides:
    text = slide.get("text", "").strip()
    slide_idx = slide.get("page_number", 1) - 1
    chunks = splitter.split_text(text)

    for chunk in chunks:
        emb = model.encode(chunk)
        vector_data.append({
            "chunk": chunk,
            "slide_index": slide_idx,
            "embedding": emb.tolist()
        })

print(f"🧠 Created {len(vector_data)} embeddings.")

with open(OUTPUT_FILE, "w") as f:
    json.dump(vector_data, f, indent=2)

print(f"✅ Saved to {OUTPUT_FILE}")
