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

md_htmltest = read_markdown_file("./testhtml.txt")
md_BluePrint_md = read_markdown_file(NEWS_PROMPTS_MD_PATH)


def extract_body_and_insert_to_md(html_content, markdown_template_path):
    """
    Extract content between <body> tags from HTML, remove JavaScript and comments,
    and insert it into the markdown template.
    
    Args:
        html_content (str): The HTML content to extract the body from
        markdown_template_path (str): Path to the markdown template file
    
    Returns:
        str: The markdown content with the cleaned HTML body inserted
    """
    import re
    
    # Extract content between <body> tags
    body_pattern = re.compile(r'<body[^>]*>(.*?)</body>', re.DOTALL)
    body_match = body_pattern.search(html_content)
    
    if not body_match:
        raise ValueError("No <body> tags found in the HTML content")
    
    body_content = body_match.group(1)
    
    # Remove all <script> tags and their contents
    script_pattern = re.compile(r'<script[\s\S]*?</script>', re.DOTALL | re.IGNORECASE)
    cleaned_body = script_pattern.sub('', body_content)
    
    # Remove HTML comments <!-- ... -->
    comment_pattern = re.compile(r'<!--[\s\S]*?-->', re.DOTALL)
    cleaned_body = comment_pattern.sub('', cleaned_body)
    
    # i don't know if they will be used or help in the generating of selectors 
    # Also remove inline JavaScript (onclick, onload, etc.)
    # inline_js_pattern = re.compile(r'\s+on\w+="[^"]*"', re.IGNORECASE)
    # cleaned_body = inline_js_pattern.sub('', cleaned_body)
    
     # Remove empty lines (lines with only whitespace)
    cleaned_lines = []
    for line in cleaned_body.split('\n'):
        if line.strip():  # If line contains non-whitespace characters
            cleaned_lines.append(line)
    
    cleaned_body = '\n'.join(cleaned_lines)


    # Read the markdown template
    with open(markdown_template_path, 'r', encoding='utf-8') as file:
        markdown_template = file.read()
    
    # Replace the placeholder with the cleaned body content
    result = markdown_template.replace('[HTML CODE HERE]', cleaned_body)
    
    return result

# Create a new .md file and write content just to test that every think is there cause i doesn't show in the terminal
# with open("new_file.md", "w", encoding="utf-8") as md_file:
#     md_file.write("# This is a new Markdown file\n\n")
#     md_file.write(extract_body_and_insert_to_md(md_htmltest,NEWS_PROMPTS_MD_PATH))

# print("new_file.md created successfully!")
    

def generate(prompt_text):


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
    generate(extract_body_and_insert_to_md(md_htmltest,NEWS_PROMPTS_MD_PATH))
