from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pdfExtractor import extract_text_from_pdf  # IMPORTED THE EXTRACTOR
import numpy as np
import json
import os

# --- 1. DEFINE YOUR DOCUMENT LIBRARY ---
# You would populate this list with the actual paths to your PDF files.
# NOTE: Please replace the placeholder paths with actual, accessible paths for testing.
LECTURE_LIBRARY = [
    {
        "id": "graph_search_v2",
        "title": "Graph and Local Search Algorithms",
        "path": "data/lecture_slides_graph_search.pdf"
    },
    {
        "id": "reinforcement_l",
        "title": "Introduction to Reinforcement Learning",
        "path": "data/lecture_slides_rl.pdf"
    },
    {
        "id": "probability_i",
        "title": "Foundations of Probability and Bayes Theorem",
        "path": "data/lecture_slides_probability.pdf"
    }
]

# --- 2. INITIALIZE COMPONENTS ---

# Recommended model for high-quality, fast embedding generation
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
try:
    model = SentenceTransformer(EMBEDDING_MODEL)
except Exception as e:
    print(f"ERROR: Failed to load Sentence Transformer model. Did you run 'pip install sentence-transformers'? {e}")
    sys.exit(1)

# Initialize the text splitter (parameters optimized for slides)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    separators=["\n\n", "\n", " ", ""]  # Try splitting by large gaps first
)

# This master list will hold ALL chunks from ALL documents
master_vector_store_entries = []

# --- 3. PROCESS THE ENTIRE LIBRARY ---

print(f"Starting indexing for {len(LECTURE_LIBRARY)} documents...")

for lecture in LECTURE_LIBRARY:
    lecture_id = lecture['id']
    lecture_title = lecture['title']
    pdf_path = lecture['path']

    print(f"\nProcessing Lecture: '{lecture_title}' (ID: {lecture_id})...")

    # CALL PHASE 1: Extraction
    page_data_list = extract_text_from_pdf(pdf_path)

    if not page_data_list:
        print(f"Skipping {lecture_title} due to extraction errors or file not found.")
        continue

    # Process all pages from the extracted data
    for page_data in page_data_list:
        full_text = page_data['text']
        base64_image = page_data['base64_image_data']
        page_number = page_data['page_number']

        # Skip pages with very little text (often just image titles or blank)
        if len(full_text) < 50:
            # If text is too short, we still generate an entry if the page is important,
            # but we'll prioritize chunking the long text.
            pass

            # PHASE 2: Chunking
        text_chunks = text_splitter.split_text(full_text)

        # PHASE 2: Embedding
        if text_chunks:
            embeddings = model.encode(text_chunks)
        else:
            # Handle empty chunks gracefully (e.g., if the page was almost blank)
            continue

        # Store vector, text chunk, and enriched metadata
        for i, chunk_text in enumerate(text_chunks):
            # Convert numpy array to list
            vector = embeddings[i].tolist()

            entry = {
                "lecture_id": lecture_id,
                "lecture_title": lecture_title,  # CATEGORY!
                "source_page": page_number,
                "chunk_id": f"{lecture_id}-p{page_number}-c{i}",
                "text_content": chunk_text,
                "base64_image_data": base64_image,
                "vector": vector,
            }
            master_vector_store_entries.append(entry)

# --- 4. OUTPUT RESULTS ---

print("\n=======================================================")
print(f"MASTER INDEXING COMPLETE! Total unique chunks created: {len(master_vector_store_entries)}")
print(f"Total Vector Dimension: {len(master_vector_store_entries[0]['vector']) if master_vector_store_entries else 0}")
print("=======================================================")

if master_vector_store_entries:
    # Save the final structured vector store to a JSON file for later use
    output_filename = "rag_master_vector_store.json"
    with open(output_filename, 'w') as f:
        # We need to save as JSON because this will later be loaded by the RAG query engine
        json.dump(master_vector_store_entries, f, indent=2)

    print(f"Master Vector Store saved to: {output_filename}")
    print("\nExample of enriched chunk metadata:")

    first_chunk = master_vector_store_entries[0]
    print(f"  > Lecture ID: {first_chunk['lecture_id']}")
    print(f"  > Lecture Title (Category): {first_chunk['lecture_title']}")
    print(f"  > Source Page: {first_chunk['source_page']}")
    print(f"  > Chunk Content: {first_chunk['text_content'][:100]}...")
    print(f"  > Base64 Data Size: {len(first_chunk['base64_image_data'])} bytes")