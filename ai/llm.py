# Import necessary libraries
from dotenv import load_dotenv
import os
from google.genai import Client

from google.genai.types import GenerateContentConfig, Content, Part
from google.generativeai.generative_models import GenerativeModel
import google.generativeai.client as genai
from ai.prompt import Prompt
from constants import *
import logging
import re
from settings import DEBUG_MODE, GEMINI_MODEL, MAX_TOKENS


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
            if DEBUG_MODE:
                logging.info(os.getenv("API_KEY"))
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
        genai.configure(api_key=self._api_key)
        model = GenerativeModel(f"models/{GEMINI_MODEL}",)
        logging.info("Total tokens: ", model.count_tokens(prompt.text))

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
