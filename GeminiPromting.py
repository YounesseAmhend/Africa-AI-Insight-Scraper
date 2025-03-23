# Import necessary libraries
from google import genai             # Google's Generative AI library for Gemini API access
from dotenv import load_dotenv       # For loading environment variables from .env file
import os                            # For accessing environment variables and file operations
import base64                        # For handling Base64 encoding (though not used in current code)
from google.genai import types       # For type definitions used with Gemini API
from constants import *              # Import constants from a separate module (includes file paths)

# Load environment variables and API key
load_dotenv()  # Load variables from .env file
api_key = os.getenv("API_KEY")  # Get the Gemini API key from environment variables

# Function to read markdown files
def read_markdown_file(filepath):
    """Read a markdown file and return its contents as a string.
    
    Args:
        filepath (str): Path to the markdown file to be read
        
    Returns:
        str: The content of the file as a string
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        content = file.read()
    return content

# Read two important files
md_htmltest = read_markdown_file("./testhtml.txt")  # Contains the HTML content to be processed
md_BluePrint_md = read_markdown_file(NEWS_PROMPTS_MD_PATH)  # Template markdown file (path from constants)

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
    import re  # Import regex library for pattern matching
    
    # Extract content between <body> tags using regex
    body_pattern = re.compile(r'<body[^>]*>(.*?)</body>', re.DOTALL)
    body_match = body_pattern.search(html_content)
    
    # Validate that body tags were found
    if not body_match:
        raise ValueError("No <body> tags found in the HTML content")
    
    body_content = body_match.group(1)  # Extract the content within body tags
    
    # Remove all <script> tags and their contents
    script_pattern = re.compile(r'<script[\s\S]*?</script>', re.DOTALL | re.IGNORECASE)
    cleaned_body = script_pattern.sub('', body_content)
    
    # Remove HTML comments <!-- ... -->
    comment_pattern = re.compile(r'<!--[\s\S]*?-->', re.DOTALL)
    cleaned_body = comment_pattern.sub('', cleaned_body)
    
    # Note: The following section for removing inline JavaScript is commented out
    # but kept for potential future use
    # inline_js_pattern = re.compile(r'\s+on\w+="[^"]*"', re.IGNORECASE)
    # cleaned_body = inline_js_pattern.sub('', cleaned_body)
    
    # Remove empty lines (lines with only whitespace)
    cleaned_lines = []
    for line in cleaned_body.split('\n'):
        if line.strip():  # If line contains non-whitespace characters
            cleaned_lines.append(line)
    
    cleaned_body = '\n'.join(cleaned_lines)  # Rejoin the non-empty lines
   
    # Read the markdown template
    with open(markdown_template_path, 'r', encoding='utf-8') as file:
        markdown_template = file.read()
    
    # Replace the placeholder with the cleaned body content
    result = markdown_template.replace('[HTML CODE HERE]', cleaned_body)
    
    return result

# Commented-out test code for file writing - useful for debugging
# with open("new_file.md", "w", encoding="utf-8") as md_file:
#     md_file.write("# This is a new Markdown file\n\n")
#     md_file.write(extract_body_and_insert_to_md(md_htmltest,NEWS_PROMPTS_MD_PATH))
# print("new_file.md created successfully!")

def generate(prompt_text):
    """
    Send a prompt to the Gemini AI API and stream the response to the console.
    
    Args:
        prompt_text (str): The prompt text to send to Gemini
    """
    # Initialize the Gemini API client with the API key
    client = genai.Client(
        api_key=api_key
    )
    
    # Specify the model to use
    model = "gemini-2.0-flash"  # Using Gemini 2.0 Flash model for text generation
    
    # Format the prompt for the API
    contents = [
        types.Content(
            role="user",  # Set role to user for the prompt
            parts=[
                types.Part.from_text(text=prompt_text),  # Convert text to the required format
            ],
        ),
    ]
    
    # Configure generation parameters
    generate_content_config = types.GenerateContentConfig(
        temperature=1,         # Higher temperature (1.0) for more creative/diverse outputs
        top_p=0.95,            # Nucleus sampling parameter to control diversity
        top_k=40,              # Top-k sampling parameter to filter token selection
        max_output_tokens=8192,  # Maximum length of generated text (8K tokens)
        response_mime_type="text/plain",  # Request plain text response
    )
    
    # Stream the generated content and print it chunk by chunk in real-time
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")  # Print each chunk without newlines between chunks

# Main execution block
if __name__ == "__main__":
    # Generate content by sending the processed HTML embedded in the markdown template
    generate(extract_body_and_insert_to_md(md_htmltest, NEWS_PROMPTS_MD_PATH))