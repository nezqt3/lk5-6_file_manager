from pathlib import Path

from file_manager.commands.command_parser import CommandParser
from file_manager.core.config_loader import load_config
from file_manager.core.file_manager import FileManager
from file_manager.users.user_manager import UserManager


def build_app() -> tuple[CommandParser, str]:
    project_root = Path(__file__).resolve().parents[2]
    config = load_config(project_root / "config" / "config.json")

    workspace_root = project_root / config["root_dir"]
    users_file = project_root / config["users_file"]
    default_user = config["default_user"]

    user_manager = UserManager(users_file, workspace_root)
    user_home = user_manager.ensure_user(default_user)

    quota_mb = config.get("disk_quota_mb")
    max_file_size_mb = config.get("max_file_size_mb")

    manager = FileManager(
        user_home,
        disk_quota_bytes=None if quota_mb is None else int(quota_mb * 1024 * 1024),
        max_file_size_bytes=None
        if max_file_size_mb is None
        else int(max_file_size_mb * 1024 * 1024),
    )
    parser = CommandParser(manager, user_manager, allow_archives=config.get("allow_archives", True))
    return parser, "."


def main() -> None:
    parser, current_dir = build_app()
    print("File manager started. Type 'help' to see commands.")

    while True:
        try:
            raw_command = input(f"{current_dir}> ").strip()
            if not raw_command:
                continue

            result = parser.execute(raw_command, current_dir)
            if result.message:
                print(result.message)

            if result.current_dir is not None:
                current_dir = result.current_dir

            if result.should_exit:
                break

        except Exception as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
