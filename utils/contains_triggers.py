def contains_triggers(
    text: str,
    trigger_words: list[str],
    trigger_phrases: list[str],
) -> bool:
    words = text.split()
    for word in trigger_words:
        if word.lower() in [w.lower() for w in words]:
            return True
    # Check for trigger phrases
    for phrase in trigger_phrases:
        if phrase.lower() in text.lower():
            return True
    return False
