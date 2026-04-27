from pathlib import Path


def format_listing_entry(path: Path) -> str:
    prefix = "[DIR]" if path.is_dir() else "[FILE]"
    return f"{prefix} {path.name}"


def strip_listing_prefix(value: str) -> str:
    for prefix in ("[DIR] ", "[FILE] "):
        if value.startswith(prefix):
            return value[len(prefix):]
    return value.strip()


def format_size(num_bytes: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    size = float(num_bytes)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} {unit}"
        size /= 1024
    return f"{num_bytes} B"
