from ai.llm import Llm
from ai.prompt import Prompt
from utils.custom_driver import CustomDriver
from utils.logger import logger


class SelectorGenerator:
    @staticmethod
    def get_scraping_selectors(
        url: str,
        selector_prompt_template_path: str,
    ) -> tuple[str, dict[str, object | dict]]:
        """Fetch HTML content and generate CSS selectors for web scraping using AI.

        Args:
            url: The URL to scrape
            selector_prompt_template_path: Path to the prompt template that instructs AI to generate selectors

        Returns:
            tuple containing:
                - HTML content of the page
                - Dictionary of CSS selectors for scraping different elements
        """
        driver = CustomDriver()
        llm = Llm()

        driver.get(url)
        html_content = driver.get_html()
        driver.quit()

        prompt = Prompt(
            template_path=selector_prompt_template_path,
            content=html_content,
        )

        result = llm.prompt(prompt)
        logger.info(f"Generated selectors: {result}")

        selectors: dict[str, object | dict] = result.code # type: ignore

        return html_content, selectors
