import os
import json
import numpy as np
from pdfExtractor import extract_text_from_pdf
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ========= CONFIG =========
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LECTURE_DIR = os.path.join(BASE_DIR, "lectures")
ASSIGNMENT_DIR = os.path.join(BASE_DIR, "assignments")
OUTPUT_JSON = os.path.join(BASE_DIR, "lecture_data.json")
OUTPUT_VECTOR = os.path.join(BASE_DIR, "vector_store.json")

CHUNK_SIZE = 300
CHUNK_OVERLAP = 50
MODEL_NAME = "all-MiniLM-L6-v2"
# ==========================

def process_pdfs():
    all_content = []

    # Process lecture PDFs
    if os.path.exists(LECTURE_DIR):
        print(f"📚 Processing lecture PDFs from folder: {LECTURE_DIR}")
        for file in os.listdir(LECTURE_DIR):
            if file.endswith(".pdf"):
                print(f"  ➤ Lecture: {file}")
                pages = extract_text_from_pdf(os.path.join(LECTURE_DIR, file))
                for page in pages:
                    page["source"] = "lecture"
                    page["file_name"] = file
                all_content.extend(pages)
    else:
        print("⚠ No 'lectures' folder found.")

    # Process assignment PDFs
    if os.path.exists(ASSIGNMENT_DIR):
        print(f"📝 Processing assignment PDFs from folder: {ASSIGNMENT_DIR}")
        for file in os.listdir(ASSIGNMENT_DIR):
            if file.endswith(".pdf"):
                print(f"  ➤ Assignment: {file}")
                pages = extract_text_from_pdf(os.path.join(ASSIGNMENT_DIR, file))
                for page in pages:
                    page["source"] = "assignment"
                    page["file_name"] = file
                all_content.extend(pages)
    else:
        print("⚠ No 'assignments' folder found.")

    return all_content

def build_embeddings(pages):
    print("🧠 Building vector embeddings...")
    model = SentenceTransformer(MODEL_NAME)
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    
    vector_data = []
    for page in pages:
        text = page.get("text", "")
        if not text.strip():
            continue
        # 🚨 Don't use image data in embeddings
        page.pop("base64_image_data", None)
        
        chunks = splitter.split_text(text)
        for chunk in chunks:
            emb = model.encode(chunk)
            vector_data.append({
                "chunk": chunk,
                "embedding": emb.tolist(),
                "source": page["source"],
                "file_name": page["file_name"],
                "slide_index": page.get("page_number", None) if page["source"] == "lecture" else None
            })
    
    print(f"✔ Created {len(vector_data)} vector records.")
    return vector_data

if __name__ == "__main__":
    print("\n🚀 STARTING FULL PDF PROCESSING\n")

    # Step 1: Extract text & images
    combined_slides = process_pdfs()
    with open(OUTPUT_JSON, "w") as f:
        json.dump(combined_slides, f, indent=2)
    print(f"\n📦 Saved {len(combined_slides)} pages to: {OUTPUT_JSON}")

    # Step 2: Build embeddings
    vectors = build_embeddings(combined_slides)
    with open(OUTPUT_VECTOR, "w") as f:
        json.dump(vectors, f, indent=2)
    print(f"💾 Saved vector store to: {OUTPUT_VECTOR}\n")

    print("🎉 DONE! Backend knowledge base is ready to use.\n")
