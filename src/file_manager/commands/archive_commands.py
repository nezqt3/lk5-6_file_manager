import zipfile
from pathlib import Path

from file_manager.core.file_manager import FileManager


def zip_command(manager: FileManager, current_dir: str, args: list[str]) -> str:
    if len(args) != 2:
        raise ValueError("Usage: zip <source> <archive_name>")

    source = manager.resolve_path(Path(current_dir) / args[0])
    archive = manager.resolve_path(Path(current_dir) / args[1])
    archive.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as zip_file:
        if source.is_dir():
            for item in source.rglob("*"):
                zip_file.write(item, arcname=item.relative_to(source.parent))
        else:
            zip_file.write(source, arcname=source.name)

    return f"Archive created: {manager.get_relative_path(archive)}"


def unzip_command(manager: FileManager, current_dir: str, args: list[str]) -> str:
    if len(args) != 2:
        raise ValueError("Usage: unzip <archive_name> <target_dir>")

    archive = manager.resolve_path(Path(current_dir) / args[0])
    target = manager.resolve_path(Path(current_dir) / args[1])
    target.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(archive, "r") as zip_file:
        for member in zip_file.infolist():
            destination = manager.resolve_path(target / member.filename)
            if member.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            destination.parent.mkdir(parents=True, exist_ok=True)
            with zip_file.open(member) as source, destination.open("wb") as output:
                output.write(source.read())

    return f"Archive extracted to: {manager.get_relative_path(target)}"
