from textual.app import ComposeResult
from textual.widgets import Static, Label


class StatusBar(Static):
    def compose(self) -> ComposeResult:
        yield Label("Ready", id="status-message")

    def on_mount(self) -> None:
        self.status_message = self.query_one("#status-message", Label)

    def set_message(self, message: str) -> None:
        self.status_message.update(message)

    def set_context(self, user: str, current_path: str, quota_message: str) -> None:
        self.set_message(f"User: {user} | Path: {current_path} | {quota_message}")
