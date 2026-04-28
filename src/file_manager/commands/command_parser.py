from __future__ import annotations

import shlex
from dataclasses import dataclass

from file_manager.commands.archive_commands import unzip_command, zip_command
from file_manager.commands.directory_commands import ls_command, mkdir_command, rmdir_command
from file_manager.commands.file_commands import (
    copy_command,
    delete_command,
    move_command,
    read_command,
    rename_command,
    touch_command,
    write_command,
)
from file_manager.commands.navigation_commands import cd_command, pwd_command, up_command
from file_manager.commands.user_commands import (
    login_command,
    register_command,
    users_command,
    whoami_command,
)
from file_manager.core.file_manager import FileManager
from file_manager.users.user_manager import UserManager
from file_manager.utils.helpers import format_size


@dataclass
class CommandResult:
    message: str
    current_dir: str | None = None
    should_exit: bool = False


class CommandParser:
    def __init__(
        self,
        manager: FileManager,
        user_manager: UserManager,
        allow_archives: bool = True,
        *,
        disk_quota_bytes: int | None = None,
        max_file_size_bytes: int | None = None,
    ):
        self.manager = manager
        self.user_manager = user_manager
        self.allow_archives = allow_archives
        self.disk_quota_bytes = disk_quota_bytes
        self.max_file_size_bytes = max_file_size_bytes
        self.current_user = "default"

    def execute(self, raw_command: str, current_dir: str) -> CommandResult:
        parts = shlex.split(raw_command)
        if not parts:
            return CommandResult(message="")

        command, args = parts[0].lower(), parts[1:]

        if command in {"exit", "quit"}:
            return CommandResult(message="Bye!", should_exit=True)

        if command == "help":
            return CommandResult(message=self.help_text())

        if command == "pwd":
            return CommandResult(message=pwd_command(self.manager, current_dir, args))
        if command == "cd":
            next_dir, message = cd_command(self.manager, current_dir, args)
            return CommandResult(message=message, current_dir=next_dir)
        if command == "up":
            next_dir, message = up_command(self.manager, current_dir, args)
            return CommandResult(message=message, current_dir=next_dir)

        if command == "ls":
            return CommandResult(message=ls_command(self.manager, current_dir, args))
        if command == "mkdir":
            return CommandResult(message=mkdir_command(self.manager, current_dir, args))
        if command == "rmdir":
            return CommandResult(message=rmdir_command(self.manager, current_dir, args))

        if command == "touch":
            return CommandResult(message=touch_command(self.manager, current_dir, args))
        if command == "read":
            return CommandResult(message=read_command(self.manager, current_dir, args))
        if command == "write":
            return CommandResult(message=write_command(self.manager, current_dir, args))
        if command in {"delete", "rm"}:
            return CommandResult(message=delete_command(self.manager, current_dir, args))
        if command == "copy":
            return CommandResult(message=copy_command(self.manager, current_dir, args))
        if command == "move":
            return CommandResult(message=move_command(self.manager, current_dir, args))
        if command == "rename":
            return CommandResult(message=rename_command(self.manager, current_dir, args))

        if command == "register":
            return CommandResult(message=register_command(self.user_manager, args))
        if command == "users":
            return CommandResult(message=users_command(self.user_manager, args))
        if command == "login":
            username, message = login_command(self.user_manager, args)
            self.manager = FileManager(
                self.user_manager.get_user_home(username),
                disk_quota_bytes=self.disk_quota_bytes,
                max_file_size_bytes=self.max_file_size_bytes,
            )
            self.current_user = username
            return CommandResult(message=message, current_dir=".")
        if command == "whoami":
            return CommandResult(message=whoami_command(self.current_user, args))
        if command == "quota":
            if args:
                raise ValueError("Usage: quota")
            usage = format_size(self.manager.get_quota_usage())
            limit = self.manager.get_quota_limit()
            if limit is None:
                return CommandResult(message=f"Quota usage: {usage} / unlimited")
            return CommandResult(message=f"Quota usage: {usage} / {format_size(limit)}")

        if command == "zip":
            if not self.allow_archives:
                raise ValueError("Archive operations are disabled by config")
            return CommandResult(message=zip_command(self.manager, current_dir, args))
        if command == "unzip":
            if not self.allow_archives:
                raise ValueError("Archive operations are disabled by config")
            return CommandResult(message=unzip_command(self.manager, current_dir, args))

        raise ValueError(f"Unknown command: {command}")

    @staticmethod
    def help_text() -> str:
        return "\n".join(
            [
                "help",
                "pwd",
                "ls [path]",
                "cd <path>",
                "up",
                "mkdir <dirname>",
                "rmdir <dirname>",
                "touch <filename>",
                "read <filename>",
                'write <filename> <text>',
                "delete|rm <name>",
                "copy <source> <target>",
                "move <source> <target>",
                "rename <source> <new_name>",
                "zip <source> <archive_name>",
                "unzip <archive_name> <target_dir>",
                "register <username>",
                "login <username>",
                "users",
                "whoami",
                "quota",
                "exit",
            ]
        )
