import random
import re


def make_word_chunk(text: str, words_target: int = 60, start: int | None = None) -> tuple[str, int]:
    words = [w for w in re.split(r"\s+", text.replace("\n", " ").strip()) if w]
    if not words:
        return ("", 0)
    if len(words) <= words_target:
        return (" ".join(words), 0)

    if start is None:
        start = random.randint(0, max(0, len(words) - words_target))
    else:
        start = max(0, min(int(start), max(0, len(words) - words_target)))

    chunk = " ".join(words[start:start + words_target])
    return (chunk, start)
