import os
from dotenv import load_dotenv
import google.generativeai as genai  # Correct import!

load_dotenv()

test_env = os.getenv("TEST_API")
test_mode = (test_env == '1' or test_env is None)

client = None
if not test_mode:
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    print("===================\nRUNNING WITH REAL GEMINI\n===================")


def gen_content(content):
    ret = None
    if test_mode:
        ret = "PRETEND THIS IS A SMART AI RESPONSE"
    else:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=content,
        )
        ret = response.text
    print("Sending response to client: "+ret)
    return ret
