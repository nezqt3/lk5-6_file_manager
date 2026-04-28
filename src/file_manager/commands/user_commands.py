from file_manager.users.user_manager import UserManager


def register_command(user_manager: UserManager, args: list[str]) -> str:
    if len(args) != 1:
        raise ValueError("Usage: register <username>")
    path = user_manager.register_user(args[0])
    return f"User created: {args[0]} ({path})"


def users_command(user_manager: UserManager, args: list[str]) -> str:
    if args:
        raise ValueError("Usage: users")
    users = user_manager.list_users()
    return "\n".join(users) if users else "(no users)"


def login_command(user_manager: UserManager, args: list[str]) -> tuple[str, str]:
    if len(args) != 1:
        raise ValueError("Usage: login <username>")
    home = user_manager.ensure_user(args[0])
    return args[0], f"Logged in as: {args[0]} ({home})"


def whoami_command(current_user: str, args: list[str]) -> str:
    if args:
        raise ValueError("Usage: whoami")
    return current_user
