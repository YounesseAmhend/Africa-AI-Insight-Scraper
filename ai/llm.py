# Import necessary libraries
from dotenv import load_dotenv
import os
from google.genai import Client
from google.genai.types import GenerateContentConfig, Content, Part
from constants import *
import logging
import re
from settings import GEMINI_MODEL, MAX_TOKENS
from utils.utils import read_file

logger = logging.getLogger(__name__)


class LlmResponse:
    def __init__(self, text: str):
        """Initialize an LlmResponse instance with text and optional code.

        Args:
            text: The text response from the LLM
            code: Optional dictionary containing any code blocks from the response
        """
        self.text = text
        self.code = self.get_code()

    def get_code(self) -> dict[str, object]:
        """Extract Python code blocks from the LLM response text.

        Returns:
            dict: A dictionary containing extracted code blocks with their language as keys
        """
        # Pattern to match Python code blocks
        pattern = r"```python\n(.*?)```"
        matches = re.findall(pattern, self.text, re.DOTALL)
        print(matches[0])
        code = eval(matches[0]) if matches else {}

        if code:
            return code
        else:
            raise Exception(f"No code blocks found in the LLM response: {self.text}")

    def __str__(self) -> str:
        """Return a string representation of the LlmResponse containing both the text content and any extracted code.

        Returns:
            str: A formatted string showing the text response and any code blocks from the LLM
        """
        if self.code:
            return f"Text Response:\n{self.text}\n\nExtracted Code:\n{self.code}"
        return f"Text Response:\n{self.text}"


class Prompt:

    def __init__(
        self,
        template_path: str,
        html_content: str,
    ) -> None:
        """Initialize a Prompt instance with template path and HTML content.

        Args:
            prompt_template_path: Path to the template file
            html_content: HTML content to be used in the prompt
        """
        self.template_path = template_path
        self.html_content = html_content

        self.text = self.create_prompt_from_html()

    def create_prompt_from_html(
        self,
    ) -> str:
        """Create a prompt by combining cleaned HTML content with a template.

        This function takes raw HTML content, cleans it by removing unnecessary elements,
        and inserts it into a specified template file to create a final prompt.

        Args:
            html_content: Raw HTML content to be processed
            template_path: Path to the template file that will wrap the HTML content

        Returns:
            str: The final prompt string combining the template and cleaned HTML content
        """
        logger.info(
            f"Creating prompt from HTML content using template: {self.template_path}"
        )
        cleaned_html = self.clean_html_content(self.html_content)

        self.html_content = cleaned_html

        logger.info(f"Inserting cleaned HTML into template: {self.template_path}")

        result = self.insert_html_into_template()

        logger.info(f"Final prompt length: {len(result)} characters")

        return result

    def clean_html_content(self, html_content: str) -> str:
        """Clean HTML content by removing unnecessary elements and whitespace.

        Args:
            html_content: Raw HTML content to be cleaned

        Returns:
            Cleaned HTML content with only relevant elements

        Raises:
            ValueError: If no <body> tag is found in the HTML content
        """
        # Extract content between <body> tags using regex
        body_pattern = re.compile(r"<body[^>]*>(.*?)</body>", re.DOTALL)
        body_match = body_pattern.search(html_content)

        if not body_match:
            logger.error("No <body> tags found in the HTML content")
            raise ValueError("No <body> tags found in the HTML content")

        body_content = body_match.group(1)

        # Define patterns for elements to remove
        patterns_to_remove = [
            (r"<script[\s\S]*?</script>", "script tags"),  # Remove <script> tags
            (r"<!--[\s\S]*?-->", "HTML comments"),  # Remove HTML comments
            (
                r"<noscript[\s\S]*?</noscript>",
                "noscript tags",
            ),  # Remove <noscript> tags
            (r"<style[\s\S]*?</style>", "style tags"),  # Remove <style> tags
        ]

        # Apply all removal patterns
        cleaned_html = body_content
        for pattern, description in patterns_to_remove:
            compiled_pattern = re.compile(pattern, re.DOTALL | re.IGNORECASE)
            before_length = len(cleaned_html)
            cleaned_html = compiled_pattern.sub("", cleaned_html)
            after_length = len(cleaned_html)
            logger.debug(
                f"Removed {description}, reduced content by {before_length - after_length} characters"
            )

        # Remove excessive whitespace and empty lines
        cleaned_html = "\n".join(
            line.strip() for line in cleaned_html.split("\n") if line.strip()
        )

        # Calculate and log cleaning statistics
        original_length = len(body_content)
        cleaned_length = len(cleaned_html)
        percentage_removed = (
            (original_length - cleaned_length) / original_length
        ) * 100

        logger.info(
            f"HTML cleaning completed. Removed {percentage_removed:.2f}% of original content. "
            f"Final content length: {cleaned_length} characters"
        )

        return cleaned_html

    def insert_html_into_template(
        self,
    ) -> str:
        """Insert HTML content into a template file at a specified placeholder.

        Args:
            template_path: Path to the template file
            html_content: HTML content to insert into the template

        Returns:
            The template content with HTML inserted at the placeholder

        Raises:
            ValueError: If the placeholder '[HTML CODE HERE]' is not found in the template
            FileNotFoundError: If the template file cannot be found
        """
        try:
            template_content = read_file(self.template_path)
            PLACEHOLDER = "[HTML CODE HERE]"

            if PLACEHOLDER not in template_content:
                logger.error(
                    f"Placeholder '{PLACEHOLDER}' not found in template file: {self.template_path}"
                )
                raise ValueError(
                    f"Placeholder '{PLACEHOLDER}' not found in template file: {self.template_path}"
                )

            return template_content.replace(PLACEHOLDER, self.html_content)
        except FileNotFoundError as e:
            logger.error(f"Template file not found: {self.template_path}")
            raise FileNotFoundError(
                f"Template file not found: {self.template_path}"
            ) from e


class Llm:
    _instance = None
    _api_key: str | None
    client: Client
    generate_content_config: GenerateContentConfig
    model: str

    def __new__(cls):
        """Create a single instance of the Llm class (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(Llm, cls).__new__(cls)
            # Initialize the instance only once
            load_dotenv()
            cls._instance._api_key = os.getenv("API_KEY")  # Private API key for Gemini
            cls._instance.client = Client(api_key=cls._instance._api_key)

            # Configuration for content generation
            cls._instance.generate_content_config = GenerateContentConfig(
                temperature=0,
                top_p=0.9,
                top_k=40,
                max_output_tokens=MAX_TOKENS,
                response_mime_type="text/plain",
            )

            cls._instance.model = GEMINI_MODEL

        return cls._instance

    def prompt(
        self,
        prompt: Prompt,
    ) -> LlmResponse:
        """Generate a response from the LLM model using the provided prompt text.

        Args:
            prompt_text: The text prompt to send to the model

        Returns:
            The generated response text from the model

        Raises:
            Exception: If an empty response is received from the model
        """

        contents = [
            Content(
                role="user",
                parts=[
                    Part.from_text(text=prompt.text),
                ],
            ),
        ]

        response = self.client.models.generate_content_stream(
            model=str(self.model),  # Specifies which Gemini model to use
            contents=contents[0],  # Provides the prompt content to generate from
            config=self.generate_content_config,
        )

        response_text: str = ""
        for chunk in response:
            response_text += chunk.text if chunk.text else ""

        if len(response_text) == 0:
            raise Exception("Empty response received from the model")

        return LlmResponse(response_text)


class RetryLimitExceeded(Exception):
    """Custom exception for when retry limit is exceeded."""


# def generate(
#     prompt_text: str,
#     max_retries: int = 3,
#     retries: int = 0,
#     model: str = GEMINI_MODEL,
# ) -> None:

#     while retries < max_retries:
#         try:
#             # Initialize the Gemini API client with the API key
#             client = genai.Client(api_key=api_key)

#             # Format the prompt for the API
#             contents = [
#                 Content(
#                     role="user",
#                     parts=[
#                         Part.from_text(text=prompt_text),
#                     ],
#                 ),
#             ]

#             # Configure generation parameters
#             generate_content_config = types.GenerateContentConfig(
#                 temperature=0,
#                 top_p=0.9,
#                 top_k=40,
#                 max_output_tokens=MAX_TOKENS,
#                 response_mime_type="text/plain",
#             )

#             # Stream the generated content
#             response = client.models.generate_content_stream(
#                 model=str(model),  # Specifies which Gemini model to use
#                 contents=contents[0],  # Provides the prompt content to generate from
#                 config=generate_content_config,
#             )

#             for chunk in response:
#                 print(chunk.text, end="")

#             return

#         except Exception as e:
#             retries += 1
#             if retries >= max_retries:
#                 logger.error(
#                     f"Maximum retries ({max_retries}) exceeded during API call"
#                 )
#                 raise RetryLimitExceeded(
#                     f"Failed to generate content after {max_retries} attempts: {str(e)}"
#                 )

#             logger.warning(
#                 f"Error generating content (attempt {retries}/{max_retries}): {str(e)}"
#             )
#             logger.debug(f"Full error details: {str(e)}")

#             # Wait between retries (increasing delay)
#             time.sleep(2**retries)  # 2, 4, 8 seconds...
