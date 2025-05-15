import logging
from utils.general_utils import read_file


import re


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
        logging.info(
            f"Creating prompt from HTML content using template: {self.template_path}"
        )
        cleaned_html = self.clean_html_content(self.html_content)

        self.html_content = cleaned_html

        logging.info(f"Inserting cleaned HTML into template: {self.template_path}")

        result = self.insert_html_into_template()

        logging.info(f"Final prompt length: {len(result)} characters")

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
            logging.error("No <body> tags found in the HTML content")
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
            logging.debug(
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

        logging.info(
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
                logging.error(
                    f"Placeholder '{PLACEHOLDER}' not found in template file: {self.template_path}"
                )
                raise ValueError(
                    f"Placeholder '{PLACEHOLDER}' not found in template file: {self.template_path}"
                )

            return template_content.replace(PLACEHOLDER, self.html_content)
        except FileNotFoundError as e:
            logging.error(f"Template file not found: {self.template_path}")
            raise FileNotFoundError(
                f"Template file not found: {self.template_path}"
            ) from e
