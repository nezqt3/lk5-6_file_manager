from pathlib import PurePath

from file_manager.core.exceptions import InvalidNameError


FORBIDDEN_NAMES = {".", "..", ""}


def validate_entry_name(name: str) -> str:
    cleaned = name.strip()
    if cleaned in FORBIDDEN_NAMES:
        raise InvalidNameError("Name cannot be empty, '.' or '..'")

    parts = PurePath(cleaned).parts
    if any(part in FORBIDDEN_NAMES for part in parts):
        raise InvalidNameError("Relative traversal is not allowed in names")

    return cleaned
