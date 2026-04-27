from textual.app import ComposeResult
from textual.widgets import Static, Input


class CommandBar(Static):
    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Enter command here...",
            id="command-input"
        )

    def on_mount(self) -> None:
        self.command_input = self.query_one("#command-input", Input)

    def get_command(self) -> str:
        return self.command_input.value.strip()

    def clear(self) -> None:
        self.command_input.value = ""