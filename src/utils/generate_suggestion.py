from src.gemini import client

def generate_suggestion(post_text):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=post_text,
    )

    return response.text