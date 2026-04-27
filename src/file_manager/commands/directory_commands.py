from file_manager.core.file_manager import FileManager


def ls_command(manager: FileManager, current_dir: str, args: list[str]) -> str:
    path = current_dir if not args else str(manager.resolve_path(current_dir) / args[0])
    items = manager.list_files(path)
    return "\n".join(items) if items else "(empty)"


def mkdir_command(manager: FileManager, current_dir: str, args: list[str]) -> str:
    if len(args) != 1:
        raise ValueError("Usage: mkdir <dirname>")
    path = manager.make_dir(args[0], current_dir)
    return f"Directory created: {path.name}"


def rmdir_command(manager: FileManager, current_dir: str, args: list[str]) -> str:
    if len(args) != 1:
        raise ValueError("Usage: rmdir <dirname>")
    manager.remove_dir(args[0], current_dir)
    return f"Directory removed: {args[0]}"
