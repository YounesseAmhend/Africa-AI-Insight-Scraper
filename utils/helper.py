


from typing import Callable


class Helpers:
    
    
    @staticmethod
    def try_until(
        func: Callable[[], None | object],
        max_retries: int = 3,
        error_message: str = "Failed to get valid HTML content and selectors after maximum retries. Please check the prompt or the code.",
    ) -> object:
        """Retry a function until it returns a non-None value or max retries is reached.

        Args:
            func: The function to retry, which should return None or an object
            max_retries: Maximum number of retry attempts (default: 3)
            error_message: Error message to raise if all retries fail

        Returns:
            object: The first non-None result from func

        Raises:
            Exception: If max_retries is reached without func returning a non-None value
        """
        for _ in range(max_retries):
            result = func()
            if result:
                return result
        raise Exception(error_message)
