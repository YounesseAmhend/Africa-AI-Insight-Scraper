import logging
import re


class LlmResponse:
    def __init__(self, text: str) -> None:
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
        # Check for both Python and JSON code blocks
        patterns = [
            r"```python\n(.*?)```",
            r"```json\n(.*?)```"
        ]
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, self.text, re.DOTALL))
        logging.info(f"Code: {matches}")
        
        if not matches or len(matches) == 0:
            return {}
            
        code_str = matches[0]
        try:
            code = eval(code_str)
        except Exception as _:  # JSON code
            import json
            code = json.loads(code_str)

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
