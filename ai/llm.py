import os

import google.generativeai.client as genai
from dotenv import load_dotenv
from google.genai import Client
from google.genai.types import Content, GenerateContentConfig, Part
from google.generativeai.generative_models import GenerativeModel

from ai.llm_response import LlmResponse
from ai.prompt import Prompt
from constants import *
from settings import DEBUG_MODE, GEMINI_MODEL, MAX_OUTPUT_TOKENS
from utils.logger import logger


class Llm:
    def __init__(self):
        """Initialize the Llm instance."""
        load_dotenv()
        self._api_key = os.getenv("API_KEY")
        if DEBUG_MODE:
            logger.info(os.getenv("API_KEY"))

        if self._api_key is None:
            raise Exception("API key not found in environment variables")

        self.client = Client(api_key=self._api_key)

        # Configuration for content generation
        self.generate_content_config = GenerateContentConfig(
            temperature=0,
            top_p=0.9,
            top_k=40,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            response_mime_type="text/plain",
        )

        self.model = GEMINI_MODEL

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
        model = GenerativeModel(
            f"models/{GEMINI_MODEL}",
        )
        logger.info("Total tokens: %d", model.count_tokens(prompt.text).total_tokens)

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
