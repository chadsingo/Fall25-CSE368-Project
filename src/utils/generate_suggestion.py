from utils.gemini import gen_content

def generate_suggestion(context):
    question = context["question"]
    slide = context["related_slide"]
    chunk = context["related_chunk"]
    similarity = context["similarity"]

    image_data = slide.get("base64_image_data", None)

    prompt = f"""
    You are an AI assistant helping an instructor respond to a student question on Piazza.

    🔒 STRICT RESPONSE RULES (DO NOT BREAK):
    - DO NOT give away full solutions or direct homework answers.
    - DO briefly clarify concepts or guide students toward understanding.
    - DO reference relevant lecture slides.
    - If an image is relevant, mention it (e.g., “as shown in the graph diagram on Slide 5”).
    - Limit response to **maximum 3 sentences**.
    - Maintain a supportive, educational tone.

    🧑 Student question:
    "{question}"

    📚 Closely related lecture excerpt:
    "{chunk}"

    🔍 Slide metadata:
    - Slide #: {slide.get('page_number', '?')}
    - Title: {slide.get('title', 'Untitled')}

    {"🖼️ Lecture image is available and may show a diagram or example." if image_data else ""}

    ✏️ Now draft a helpful hint for the instructor to post (do NOT fully answer):
    """

    # 📌 If image exists, append for multimodal LLMs (Gemini supports this)
    if image_data:
        prompt += "\n\n<image>" + image_data + "</image>"

    return gen_content(prompt)
