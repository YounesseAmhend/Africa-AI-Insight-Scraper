from ai.llm import Llm
from ai.prompt import Prompt, PromptType
from constants import SUMMARY_PROMPT_PATH
from utils.logger import logger


class MultilingualSummarizer:
    """
    A class for detecting language and summarizing text in multiple languages
    (French, English, Arabic)  using LLMs.
    """

    def summarize(self, text: str) -> str:
        """
        Summarize the given text using an LLM.

        Args:
            text: The text to summarize

        Returns:
            The summarized text
        """

        try:
            logger.info("Initializing LLM for summarization")
            llm = Llm()

            logger.info(f"Creating prompt with template: {SUMMARY_PROMPT_PATH}")
            prompt = Prompt(
                content=text, template_path=SUMMARY_PROMPT_PATH, type=PromptType.TEXT
            )

            logger.info("Sending prompt to LLM for summarization")
            response = llm.prompt(prompt)

            logger.info(
                f"Summarization completed. Response length: {len(response.text)} characters"
            )
            return str(response.code)
        except Exception as e:
            logger.error(f"Failed to summarize text: {str(e)}")
            raise e
