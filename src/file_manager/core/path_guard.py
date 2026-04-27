from pathlib import Path

from file_manager.core.exceptions import PathOutsideRootError


class PathGuard:
    """Ensures that all operations stay inside the configured workspace."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, path: str | Path) -> Path:
        candidate = Path(path)
        if not candidate.is_absolute():
            candidate = self.root / candidate

        resolved = candidate.resolve()
        if resolved != self.root and self.root not in resolved.parents:
            raise PathOutsideRootError("Access outside workspace is forbidden")

        return resolved
