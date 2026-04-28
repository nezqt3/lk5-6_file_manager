from textual.app import ComposeResult
from textual.widgets import Static, Input


class CommandBar(Static):
    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Type a command here, for example: ls, pwd, mkdir docs...",
            id="command-input"
        )

    def on_mount(self) -> None:
        self.command_input = self.query_one("#command-input", Input)

    def get_command(self) -> str:
        return self.command_input.value.strip()

    def clear(self) -> None:
        self.command_input.value = ""

    def focus_input(self) -> None:
        self.command_input.focus()

    def input_has_focus(self) -> bool:
        return getattr(self, "command_input", None) is not None and self.command_input.has_focus
