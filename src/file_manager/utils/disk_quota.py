from pathlib import Path

from file_manager.core.exceptions import QuotaExceededError


class DiskQuotaManager:
    def __init__(self, limit_bytes: int | None = None):
        self.limit_bytes = limit_bytes

    def get_usage(self, root: str | Path) -> int:
        base = Path(root)
        total = 0
        for path in base.rglob("*"):
            if path.is_file():
                total += path.stat().st_size
        return total

    def ensure_within_limit(self, root: str | Path, additional_bytes: int = 0) -> None:
        if self.limit_bytes is None:
            return

        usage = self.get_usage(root)
        if usage + max(additional_bytes, 0) > self.limit_bytes:
            raise QuotaExceededError(
                f"Disk quota exceeded: {usage + additional_bytes} > {self.limit_bytes} bytes"
            )
