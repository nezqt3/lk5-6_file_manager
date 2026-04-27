class FileManagerError(Exception):
    """Base exception for the file manager."""


class PathOutsideRootError(FileManagerError):
    """Raised when an operation targets a path outside the workspace."""


class InvalidNameError(FileManagerError):
    """Raised when a file or directory name is invalid."""


class QuotaExceededError(FileManagerError):
    """Raised when disk quota would be exceeded."""


class UserAlreadyExistsError(FileManagerError):
    """Raised when attempting to create an existing user."""


class UserNotFoundError(FileManagerError):
    """Raised when a requested user does not exist."""
