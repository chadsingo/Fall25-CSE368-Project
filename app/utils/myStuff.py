import fitz  # PyMuPDF is imported as 'fitz'
import base64  # Needed to encode the image data for the Gemini API
import io  # Needed for handling image streams
import os  # For checking file existence


def extract_text_from_pdf(pdf_path):
    """
    Extracts all text content and generates a Base64 image representation
    of each page for use in a Multimodal RAG system (e.g., with Gemini).

    Args:
        pdf_path (str): The file path to the PDF document.

    Returns:
        list[dict]: A list of dictionaries, where each dict represents a page
                    and contains its text, page number, and Base64 image data.
    """
    if not os.path.exists(pdf_path):
        print(f"ERROR: File not found at path: {pdf_path}")
        return []

    extracted_pages = []

    try:
        # Open the PDF document
        doc = fitz.open(pdf_path)
        print(f"--- Loaded Document: {pdf_path} (Pages: {doc.page_count}) ---\n")

        # Iterate through all pages
        for i, page in enumerate(doc):
            page_number = i + 1

            # --- 1. Text Extraction (for the main body) ---
            # Using 'text' method for general flow text
            text = page.get_text("text").strip()

            # --- 2. Multimodal Image Extraction (for equations/graphs) ---
            # Matrix(300/72) scales the default 72 DPI to 300 DPI for high resolution
            pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))
            img_bytes = pix.tobytes("png")

            # Encode the byte array to a Base64 string
            base64_encoded_image = base64.b64encode(img_bytes).decode('utf-8')

            # --- 3. Structure and Collect Data ---
            page_data = {
                "page_number": page_number,
                # Note: We need a title per page, but PDFs don't always have one.
                # For now, we'll use a placeholder or the first line of text.
                "title": text.split('\n', 1)[0][:50] if text else f"Page {page_number}",
                "text": text,
                "base64_image_data": base64_encoded_image  # Changed stub to data for clarity
            }
            extracted_pages.append(page_data)

            print(
                f"Page {page_number}: Text length={len(text)}, Image size={len(base64_encoded_image)} chars. Collected.")

        doc.close()

        print(f"\n--- Extraction Complete. Total {len(extracted_pages)} pages structured. ---")
        return extracted_pages

    except Exception as e:
        print(f"An error occurred while processing the file: {e}")
        return []


# --- CONFIGURATION ---

# !!! REPLACE THE PATH BELOW with the actual path to your .pdf file !!!
pdf_file_path = "path/to/your/lecture_slides.pdf"

# Run the extraction function and capture the output
structured_lecture_data = extract_text_from_pdf(pdf_file_path)

# You can now pass 'structured_lecture_data' to your indexer!
# Example: print(structured_lecture_data[0])