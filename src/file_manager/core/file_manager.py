from __future__ import annotations

import shutil
from pathlib import Path

from file_manager.core.path_guard import PathGuard
from file_manager.utils.disk_quota import DiskQuotaManager
from file_manager.utils.helpers import format_listing_entry, strip_listing_prefix
from file_manager.utils.validators import validate_entry_name


class FileManager:
    def __init__(
        self,
        root: str | Path,
        *,
        disk_quota_bytes: int | None = None,
        max_file_size_bytes: int | None = None,
    ):
        self.guard = PathGuard(root)
        self.root = self.guard.root
        self.quota = DiskQuotaManager(disk_quota_bytes)
        self.max_file_size_bytes = max_file_size_bytes

    def resolve_path(self, path: str | Path = ".") -> Path:
        return self.guard.resolve(path)

    def resolve_child_path(self, current_dir: str | Path, child: str | Path) -> Path:
        return self.resolve_path(self.resolve_path(current_dir) / child)

    def list_files(self, path: str | Path = ".") -> list[str]:
        current_path = self.resolve_path(path)
        return [
            format_listing_entry(item)
            for item in sorted(current_path.iterdir(), key=lambda entry: (not entry.is_dir(), entry.name.lower()))
        ]

    def exists(self, path: str | Path) -> bool:
        return self.resolve_path(path).exists()

    def make_dir(self, dirname: str, current_dir: str | Path = ".") -> Path:
        name = validate_entry_name(strip_listing_prefix(dirname))
        path = self.resolve_child_path(current_dir, name)
        path.mkdir(parents=False, exist_ok=False)
        return path

    def mkdir(self, dirname: str, current_dir: str | Path = ".") -> Path:
        return self.make_dir(dirname, current_dir)

    def remove_dir(self, dirname: str, current_dir: str | Path = ".") -> None:
        name = validate_entry_name(strip_listing_prefix(dirname))
        path = self.resolve_child_path(current_dir, name)
        shutil.rmtree(path)

    def create_file(self, filename: str, current_dir: str | Path = ".", content: str = "") -> Path:
        name = validate_entry_name(strip_listing_prefix(filename))
        payload_bytes = len(content.encode("utf-8"))
        self.quota.ensure_within_limit(self.root, payload_bytes)

        path = self.resolve_child_path(current_dir, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def read_file(self, filename: str, current_dir: str | Path = ".") -> str:
        path = self.resolve_child_path(current_dir, strip_listing_prefix(filename))
        if self.max_file_size_bytes is not None and path.stat().st_size > self.max_file_size_bytes:
            raise ValueError("File exceeds configured read size limit")
        return path.read_text(encoding="utf-8")

    def write_file(self, filename: str, content: str, current_dir: str | Path = ".") -> Path:
        name = validate_entry_name(strip_listing_prefix(filename))
        path = self.resolve_child_path(current_dir, name)
        old_size = path.stat().st_size if path.exists() else 0
        new_size = len(content.encode("utf-8"))
        self.quota.ensure_within_limit(self.root, new_size - old_size)
        path.write_text(content, encoding="utf-8")
        return path

    def delete(self, name: str, current_dir: str | Path = ".") -> None:
        path = self.resolve_child_path(current_dir, strip_listing_prefix(name))
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    def delete_file(self, filename: str, current_dir: str | Path = ".") -> None:
        self.delete(filename, current_dir)

    def copy(self, source: str, source_dir: str | Path = ".", target: str | Path | None = None) -> Path:
        src = self.resolve_child_path(source_dir, strip_listing_prefix(source))
        if target is None:
            raise ValueError("Target path is required")

        target_path = self.resolve_path(target)
        if target_path.exists() and target_path.is_dir():
            target_path = target_path / src.name
        elif not target_path.exists() and Path(target).suffix == "" and src.is_file():
            target_path.mkdir(parents=True, exist_ok=True)
            target_path = target_path / src.name

        additional_bytes = self._calculate_copy_size(src, target_path)
        self.quota.ensure_within_limit(self.root, additional_bytes)

        if src.is_dir():
            shutil.copytree(src, target_path, dirs_exist_ok=True)
        else:
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target_path)
        return target_path

    def move(self, source: str, source_dir: str | Path = ".", target: str | Path | None = None) -> Path:
        src = self.resolve_child_path(source_dir, strip_listing_prefix(source))
        if target is None:
            raise ValueError("Target path is required")

        target_path = self.resolve_path(target)
        if target_path.exists() and target_path.is_dir():
            target_path = target_path / src.name
        elif not target_path.exists() and Path(target).suffix == "" and src.is_file():
            target_path.mkdir(parents=True, exist_ok=True)
            target_path = target_path / src.name

        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(target_path))
        return target_path

    def rename(self, source: str, new_name: str, current_dir: str | Path = ".") -> Path:
        src = self.resolve_child_path(current_dir, strip_listing_prefix(source))
        validated = validate_entry_name(strip_listing_prefix(new_name))
        dst = src.with_name(validated)
        src.rename(dst)
        return dst

    def change_directory(self, current_dir: str | Path, target: str) -> Path:
        target_path = self.resolve_path(self.resolve_path(current_dir) / target)
        if not target_path.is_dir():
            raise NotADirectoryError(f"{target} is not a directory")
        return target_path

    def get_relative_path(self, path: str | Path) -> str:
        resolved = self.resolve_path(path)
        if resolved == self.root:
            return "."
        return str(resolved.relative_to(self.root))

    def get_quota_usage(self) -> int:
        return self.quota.get_usage(self.root)

    def get_quota_limit(self) -> int | None:
        return self.quota.limit_bytes

    def _calculate_copy_size(self, source: Path, target: Path) -> int:
        source_size = self._path_size(source)
        if target.exists():
            target_size = self._path_size(target)
            return max(source_size - target_size, 0)
        return source_size

    def _path_size(self, path: Path) -> int:
        if path.is_file():
            return path.stat().st_size
        return sum(item.stat().st_size for item in path.rglob("*") if item.is_file())
