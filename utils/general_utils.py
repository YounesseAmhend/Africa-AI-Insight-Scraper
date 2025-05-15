

import logging



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
