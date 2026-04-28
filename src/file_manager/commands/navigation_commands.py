from pathlib import Path

from file_manager.core.file_manager import FileManager


def pwd_command(manager: FileManager, current_dir: str, args: list[str]) -> str:
    if args:
        raise ValueError("Usage: pwd")
    return manager.get_relative_path(current_dir)


def cd_command(manager: FileManager, current_dir: str, args: list[str]) -> tuple[str, str]:
    if len(args) != 1:
        raise ValueError("Usage: cd <path>")
    if args[0] == ".." and current_dir == ".":
        return ".", "Current directory: ."
    target = manager.change_directory(current_dir, args[0])
    relative = manager.get_relative_path(target)
    return relative, f"Current directory: {relative}"


def up_command(manager: FileManager, current_dir: str, args: list[str]) -> tuple[str, str]:
    if args:
        raise ValueError("Usage: up")
    parent = Path(current_dir).parent
    normalized = "." if str(parent) in ("", ".") else str(parent)
    target = manager.change_directory(".", normalized)
    relative = manager.get_relative_path(target)
    return relative, f"Current directory: {relative}"
