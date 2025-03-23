

import logging


def contains_triggers(
    text: str,
    trigger_words: list[str],
    trigger_phrases: list[str],
) -> bool:
    # Check for trigger words
    words = text.split()
    for word in trigger_words:
        if word.lower() in [w.lower() for w in words]:
            return True
    # Check for trigger phrases
    for phrase in trigger_phrases:
        if phrase.lower() in text.lower():
            return True
    return False


def write_to_file(filepath: str, content: str) -> None:
    try:
        with open(filepath, "w", encoding="utf-8") as file:
            file.write(content)
    except IOError as e:
        logging.error(f"Failed to write to file {filepath}: {str(e)[1500:]}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error writing to file {filepath}: {str(e)[1500:]}")
        raise


def read_file(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()
    return content
