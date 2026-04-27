import json
from pathlib import Path


DEFAULT_CONFIG = {
    "root_dir": "workspace",
    "users_file": "src/file_manager/users/users.json",
    "default_user": "default",
    "disk_quota_mb": None,
    "max_file_size_mb": None,
    "allow_archives": True,
}


def load_config(config_path: str | Path) -> dict:
    path = Path(config_path)
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(DEFAULT_CONFIG, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return DEFAULT_CONFIG.copy()

    raw = path.read_text(encoding="utf-8").strip()
    if not raw:
        path.write_text(
            json.dumps(DEFAULT_CONFIG, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        return DEFAULT_CONFIG.copy()

    loaded = json.loads(raw)
    config = DEFAULT_CONFIG.copy()
    config.update(loaded)
    return config
