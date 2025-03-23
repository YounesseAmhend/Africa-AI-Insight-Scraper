from google import genai
from dotenv import load_dotenv
import os
import base64
from google.genai import types
from constants import *

##just loading the api key
load_dotenv()  # Load variables from .env file
api_key = os.getenv("API_KEY")


# Read the content of a .md file
def read_markdown_file(filepath):
    """Read a markdown file and return its contents as a string."""
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

prompt_text = read_markdown_file(NEWS_PROMPTS_MD_PATH)


def generate():
    client = genai.Client(
        api_key=api_key
    )

    model = "gemini-2.0-flash"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompt_text),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=1,
        top_p=0.95,
        top_k=40,
        max_output_tokens=8192,
        response_mime_type="text/plain",
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")

if __name__ == "__main__":
    generate()
