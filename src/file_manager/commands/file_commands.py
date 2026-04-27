from file_manager.core.file_manager import FileManager


def touch_command(manager: FileManager, current_dir: str, args: list[str]) -> str:
    if len(args) != 1:
        raise ValueError("Usage: touch <filename>")
    path = manager.create_file(args[0], current_dir)
    return f"Created file: {path.name}"


def read_command(manager: FileManager, current_dir: str, args: list[str]) -> str:
    if len(args) != 1:
        raise ValueError("Usage: read <filename>")
    return manager.read_file(args[0], current_dir)


def write_command(manager: FileManager, current_dir: str, args: list[str]) -> str:
    if len(args) < 2:
        raise ValueError('Usage: write <filename> <text>')
    filename, content = args[0], " ".join(args[1:])
    manager.write_file(filename, content, current_dir)
    return f"Written to: {filename}"


def delete_command(manager: FileManager, current_dir: str, args: list[str]) -> str:
    if len(args) != 1:
        raise ValueError("Usage: delete <name>")
    manager.delete(args[0], current_dir)
    return f"Deleted: {args[0]}"


def copy_command(manager: FileManager, current_dir: str, args: list[str]) -> str:
    if len(args) != 2:
        raise ValueError("Usage: copy <source> <target>")
    target = manager.copy(args[0], current_dir, manager.resolve_path(current_dir) / args[1])
    return f"Copied to: {manager.get_relative_path(target)}"


def move_command(manager: FileManager, current_dir: str, args: list[str]) -> str:
    if len(args) != 2:
        raise ValueError("Usage: move <source> <target>")
    target = manager.move(args[0], current_dir, manager.resolve_path(current_dir) / args[1])
    return f"Moved to: {manager.get_relative_path(target)}"


def rename_command(manager: FileManager, current_dir: str, args: list[str]) -> str:
    if len(args) != 2:
        raise ValueError("Usage: rename <source> <new_name>")
    target = manager.rename(args[0], args[1], current_dir)
    return f"Renamed to: {target.name}"
