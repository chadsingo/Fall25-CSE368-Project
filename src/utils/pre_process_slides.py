import os
import json
from pdfExtractor import extract_text_from_pdf

SLIDE_PATH = "../../cs368-fa25-lec04-graph-search-and-local-search.pdf"  # Update if needed
OUTPUT_FILE = "../lecture_data.json"  # save to project root

if __name__ == "__main__":
    pages = extract_text_from_pdf(SLIDE_PATH)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(pages, f, indent=2)
    print(f"Saved {len(pages)} pages to {OUTPUT_FILE}")
