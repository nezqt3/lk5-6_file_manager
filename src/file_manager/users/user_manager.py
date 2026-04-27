import json
from pathlib import Path

from file_manager.core.exceptions import UserAlreadyExistsError, UserNotFoundError


class UserManager:
    def __init__(self, users_file: str | Path, workspace_root: str | Path):
        self.users_file = Path(users_file)
        self.workspace_root = Path(workspace_root)
        self.users_file.parent.mkdir(parents=True, exist_ok=True)
        self.workspace_root.mkdir(parents=True, exist_ok=True)
        if not self.users_file.exists() or not self.users_file.read_text(encoding="utf-8").strip():
            self._save({"users": {}})

    def register_user(self, username: str) -> Path:
        data = self._load()
        if username in data["users"]:
            raise UserAlreadyExistsError(f"User '{username}' already exists")

        user_dir = self.workspace_root / username
        user_dir.mkdir(parents=True, exist_ok=False)
        data["users"][username] = {"home": str(user_dir)}
        self._save(data)
        return user_dir

    def get_user_home(self, username: str) -> Path:
        data = self._load()
        user = data["users"].get(username)
        if user is None:
            raise UserNotFoundError(f"User '{username}' does not exist")
        return Path(user["home"])

    def list_users(self) -> list[str]:
        return sorted(self._load()["users"].keys())

    def ensure_user(self, username: str) -> Path:
        try:
            return self.get_user_home(username)
        except UserNotFoundError:
            return self.register_user(username)

    def _load(self) -> dict:
        return json.loads(self.users_file.read_text(encoding="utf-8"))

    def _save(self, data: dict) -> None:
        self.users_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
