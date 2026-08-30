import re
import unicodedata


def normalize_text(text: str) -> str:

    if not text:
        return ""

    text = unicodedata.normalize(
        "NFC",
        text
    )

    text = text.lower()

    text = re.sub(
        r"""[.,!?;:'“”‘’(){}\[\]<>।॥]""",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    text = text.strip()

    return text