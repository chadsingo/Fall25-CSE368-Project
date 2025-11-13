import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

test_env = os.getenv("TEST_API")
test_mode = (test_env == '1' or test_env is None)
client = None
if (not test_mode):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    print("===================\nRUNNING WITH REAL GEMINI\n===================")


def gen_content(content):
    if (test_mode):
        return "PRETEND THIS IS A SMART AI RESPONSE"
    else:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=content,
        )
        return response.text