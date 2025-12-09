import os
from dotenv import load_dotenv
from google import genai  # Correct import!

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
        ret = content
    else:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=content,
        )
        ret = response.text
    print("Sending response to client: "+ret)
    return ret
