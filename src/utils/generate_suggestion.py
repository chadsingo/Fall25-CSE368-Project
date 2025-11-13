import src.gemini as gemini

def generate_suggestion(post_text):
    return gemini.gen_content(post_text)