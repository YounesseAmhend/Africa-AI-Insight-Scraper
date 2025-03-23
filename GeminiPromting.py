from google import genai             # Google's Generative AI library for Gemini API access
from dotenv import load_dotenv       # For loading environment variables from .env file
import os                            # For accessing environment variables and file operations
import base64                        # For handling Base64 encoding (though not used in current code)
from google.genai import types       # For type definitions used with Gemini API
from constants import *              # Import constants from a separate module (includes file paths)
import time                          # For implementing retry delays
import logging                       # For proper logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables and API key
load_dotenv()  # Load variables from .env file
api_key = os.getenv("API_KEY")  # Get the Gemini API key from environment variables

class RetryLimitExceeded(Exception):
    """Custom exception for when retry limit is exceeded."""
    pass

# Function to read markdown files
def read_markdown_file(filepath, max_retries=3):
    """Read a markdown file and return its contents as a string.
    
    Args:
        filepath (str): Path to the markdown file to be read
        max_retries (int): Maximum number of retry attempts
        
    Returns:
        str: The content of the file as a string
        
    Raises:
        RetryLimitExceeded: If the maximum number of retries is exceeded
        FileNotFoundError: If the file does not exist
    """
    retries = 0
    while retries < max_retries:
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except FileNotFoundError as e:
            logger.error(f"File not found: {filepath}")
            raise e  # Don't retry for missing files
        except Exception as e:
            retries += 1
            if retries >= max_retries:
                logger.error(f"Maximum retries ({max_retries}) exceeded while reading file: {filepath}")
                raise RetryLimitExceeded(f"Failed to read file after {max_retries} attempts: {str(e)}")
            logger.warning(f"Error reading file (attempt {retries}/{max_retries}): {str(e)}")
            time.sleep(1)  # Wait before retrying
    
    # This should never execute due to the raise in the loop, but added for safety
    raise RetryLimitExceeded(f"Failed to read file after {max_retries} attempts")


def extract_body_and_insert_to_md(html_content, markdown_template_path, max_retries=3):
    """
    Extract content between <body> tags from HTML, remove JavaScript and comments,
    and insert it into the markdown template.
    
    Args:
        html_content (str): The HTML content to extract the body from
        markdown_template_path (str): Path to the markdown template file
        max_retries (int): Maximum number of retry attempts
    
    Returns:
        str: The markdown content with the cleaned HTML body inserted
    
    Raises:
        RetryLimitExceeded: If the maximum number of retries is exceeded
        ValueError: If no body tags are found in the HTML content
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
    
    # Remove empty lines (lines with only whitespace)
    cleaned_lines = []
    for line in cleaned_body.split('\n'):
        if line.strip():  # If line contains non-whitespace characters
            cleaned_lines.append(line)
    
    cleaned_body = '\n'.join(cleaned_lines)  # Rejoin the non-empty lines
   
    # Read the markdown template with retry mechanism
    retries = 0
    while retries < max_retries:
        try:
            with open(markdown_template_path, 'r', encoding='utf-8') as file:
                markdown_template = file.read()
            
            # Replace the placeholder with the cleaned body content
            result = markdown_template.replace('[HTML CODE HERE]', cleaned_body)
            return result
        except Exception as e:
            retries += 1
            if retries >= max_retries:
                logger.error(f"Maximum retries ({max_retries}) exceeded while processing template")
                raise RetryLimitExceeded(f"Failed to process template after {max_retries} attempts: {str(e)}")
            logger.warning(f"Error processing template (attempt {retries}/{max_retries}): {str(e)}")
            time.sleep(1)  # Wait before retrying
    
    # This should never execute due to the raise in the loop, but added for safety
    raise RetryLimitExceeded(f"Failed to process template after {max_retries} attempts")

def generate(prompt_text, max_retries=3):
    """
    Send a prompt to the Gemini AI API and stream the response to the console.
    
    Args:
        prompt_text (str): The prompt text to send to Gemini
        max_retries (int): Maximum number of retry attempts
        
    Raises:
        RetryLimitExceeded: If the maximum number of retries is exceeded
    """
    retries = 0
    
    while retries < max_retries:
        try:
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
                
            # If we get here without exceptions, return successfully
            return
            
        except Exception as e:
            retries += 1
            if retries >= max_retries:
                logger.error(f"Maximum retries ({max_retries}) exceeded during API call")
                raise RetryLimitExceeded(f"Failed to generate content after {max_retries} attempts: {str(e)}")
            
            logger.warning(f"Error generating content (attempt {retries}/{max_retries}): {str(e)}")
            
            # Wait longer between retries (exponential backoff)
            time.sleep(2 ** retries)  # 2, 4, 8 seconds...

# Main execution block
if __name__ == "__main__":
    try:
        # Read the required files with retry mechanism
        logger.info("Reading HTML test file...")
        md_htmltest = read_markdown_file("./testhtml.txt")
        
        logger.info("Reading markdown template...")
        md_BluePrint_md = read_markdown_file(NEWS_PROMPTS_MD_PATH)
        
        # Process the HTML and generate content
        logger.info("Extracting body content and inserting into template...")
        final_prompt = extract_body_and_insert_to_md(md_htmltest, NEWS_PROMPTS_MD_PATH)
        
        logger.info("Sending prompt to Gemini API...")
        generate(final_prompt)
        
        logger.info("Process completed successfully")
        
    except RetryLimitExceeded as e:
        logger.error(f"Error: {str(e)}")
        print(f"\nError: The operation failed after multiple attempts. Please check your code or fix the prompt.")
        # You could exit with a non-zero code here if desired
        # import sys
        # sys.exit(1)
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\nUnexpected error: {str(e)}")