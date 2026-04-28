from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Button, ListView
from textual.widgets import Header, Footer

from file_manager.commands.command_parser import CommandResult
from file_manager.main import build_app
from file_manager.ui.css.dialog_styles import dialog_styles
from file_manager.ui.css.main_styles import styles as main_styles
from file_manager.ui.widgets.file_panel import FilePanel
from file_manager.ui.widgets.command_bar import CommandBar
from file_manager.ui.widgets.status_bar import StatusBar
from file_manager.utils.helpers import format_size


class CreateDirectoryDialog(ModalScreen[str | None]):
    CSS = dialog_styles

    def compose(self):
        with Vertical(id="dialog"):
            yield Input(placeholder="Directory name", id="dirname-input")
            yield Button("Create", id="create", variant="success")
            yield Button("Cancel", id="cancel")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create":
            dirname = self.query_one("#dirname-input", Input).value.strip()
            self.dismiss(dirname if dirname else None)

        if event.button.id == "cancel":
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "dirname-input":
            dirname = event.value.strip()
            self.dismiss(dirname if dirname else None)

class FileManagerApp(App):
    TITLE = "Python File Manager"
    SUB_TITLE = "Textual UI"

    CSS = main_styles

    BINDINGS = [
        ("q", "quit", "Exit"),
        Binding("tab", "switch_panel", "Switch panel", priority=True),
        ("enter", "open_selected", "Open"),
        ("backspace", "go_up", "Up"),
        ("slash", "focus_command", "Command"),
        ("ctrl+l", "focus_command", "Command"),
        Binding("escape", "focus_panel", "Panel", priority=True),

        Binding("f5", "copy_file", "Copy", priority=True),

        Binding("f6", "move_file", "Move", priority=True),

        Binding("f7", "create_directory", "Mkdir", priority=True),

        Binding("f8", "delete_item", "Delete", priority=True),

        ("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="main-area"):
            yield FilePanel("Left panel", id="left-panel")
            yield FilePanel("Right panel", id="right-panel")

        with Vertical(id="bottom-area"):
            yield CommandBar(id="command-bar")
            yield StatusBar(id="status-bar")

        yield Footer()

    def on_mount(self) -> None:
        self.parser, _ = build_app()
        self.fm = self.parser.manager
        self.left_panel = self.query_one("#left-panel", FilePanel)
        self.right_panel = self.query_one("#right-panel", FilePanel)
        self.command_bar = self.query_one("#command-bar", CommandBar)
        self.status_bar = self.query_one("#status-bar", StatusBar)
        self.active_panel = self.left_panel
        self.inactive_panel = self.right_panel

        self.left_panel.set_path(".")
        self.right_panel.set_path(".")

        self.left_panel.set_active(True)
        self.right_panel.set_active(False)

        self.load_panel_files(self.left_panel)
        self.load_panel_files(self.right_panel)
        self.command_bar.focus_input()
        self.update_context_status("Ready")

    def action_switch_panel(self) -> None:
        self.active_panel.set_active(False)
        self.inactive_panel.set_active(True)

        self.active_panel, self.inactive_panel = (
            self.inactive_panel,
            self.active_panel,
        )

        self.active_panel.focus_list()
        self.update_context_status(f"Active panel: {self.active_panel.title}")

    def action_refresh(self) -> None:
        self.load_panel_files(self.active_panel)
        self.active_panel.focus_list()
        self.update_context_status("Panel refreshed")

    def action_focus_command(self) -> None:
        self.command_bar.focus_input()
        self.update_context_status("Command input focused")

    def action_focus_panel(self) -> None:
        self.active_panel.focus_list()
        self.update_context_status("Panel focused")

    def load_panel_files(self, panel: FilePanel) -> None:
        files = self.fm.list_files(panel.current_path)
        panel.set_files(files)

    def action_copy_file(self) -> None:
        selected = self.active_panel.get_selected_item()

        if not selected:
            self.status_bar.set_message("Nothing selected")
            return

        try:
            self.fm.copy(
                selected,
                self.active_panel.current_path,
                self.fm.resolve_path(self.inactive_panel.current_path),
            )

            self.load_panel_files(self.inactive_panel)
            self.active_panel.focus_list()
            self.update_context_status(f"Copied: {selected}")

        except Exception as error:
            self.update_context_status(f"Error: {error}")

    def action_move_file(self) -> None:
        selected = self.active_panel.get_selected_item()

        if not selected:
            self.status_bar.set_message("Nothing selected")
            return

        try:
            self.fm.move(
                selected,
                self.active_panel.current_path,
                self.fm.resolve_path(self.inactive_panel.current_path),
            )

            self.load_panel_files(self.active_panel)
            self.load_panel_files(self.inactive_panel)
            self.active_panel.focus_list()

            self.update_context_status(f"Moved: {selected}")

        except Exception as error:
            self.update_context_status(f"Error: {error}")

    def action_create_directory(self) -> None:
        self.push_screen(CreateDirectoryDialog(), self.create_directory_callback)

    def create_directory_callback(self, dirname: str | None) -> None:
        if not dirname:
            self.update_context_status("Directory creation cancelled")
            return

        try:
            self.fm.mkdir(dirname, self.active_panel.current_path)
            self.load_panel_files(self.active_panel)
            self.active_panel.focus_list()
            self.update_context_status(f"Directory created: {dirname}")

        except Exception as error:
            self.update_context_status(f"Error: {error}")

    def action_delete_item(self) -> None:
        selected = self.active_panel.get_selected_item()

        if not selected:
            self.update_context_status("Nothing selected")
            return

        try:
            self.fm.delete(selected, self.active_panel.current_path)
            self.load_panel_files(self.active_panel)
            self.active_panel.focus_list()

            self.update_context_status(f"Deleted: {selected}")

        except Exception as error:
            self.update_context_status(f"Error: {error}")

    def action_open_selected(self) -> None:
        selected = self.active_panel.get_selected_item()
        if not selected or not selected.startswith("[DIR] "):
            return

        try:
            next_path = self.fm.change_directory(
                self.active_panel.current_path,
                selected.replace("[DIR] ", "", 1),
            )
            relative = self.fm.get_relative_path(next_path)
            self.active_panel.set_path(relative)
            self.load_panel_files(self.active_panel)
            self.active_panel.focus_list()
            self.update_context_status(f"Current directory: {relative}")
        except Exception as error:
            self.update_context_status(f"Error: {error}")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view is self.active_panel.file_list:
            self.action_open_selected()

    def action_go_up(self) -> None:
        try:
            if self.active_panel.current_path == ".":
                relative = "."
            else:
                next_path = self.fm.change_directory(self.active_panel.current_path, "..")
                relative = self.fm.get_relative_path(next_path)
            self.active_panel.set_path(relative)
            self.load_panel_files(self.active_panel)
            self.active_panel.focus_list()
            self.update_context_status(f"Current directory: {relative}")
        except Exception as error:
            self.update_context_status(f"Error: {error}")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id != "command-input":
            return

        raw_command = event.value.strip()
        if not raw_command:
            self.active_panel.focus_list()
            return

        try:
            result = self.parser.execute(raw_command, self.active_panel.current_path)
            self._apply_command_result(result)
        except Exception as error:
            self.update_context_status(f"Error: {error}")
        finally:
            self.command_bar.clear()
            self.command_bar.focus_input()

    def _apply_command_result(self, result: CommandResult) -> None:
        self.fm = self.parser.manager

        if result.current_dir is not None:
            self.active_panel.set_path(result.current_dir)

        self.load_panel_files(self.left_panel)
        self.load_panel_files(self.right_panel)

        if result.message:
            self.update_context_status(result.message.splitlines()[0])

        if result.should_exit:
            self.exit()

    def update_context_status(self, message: str) -> None:
        usage = self.fm.get_quota_usage()
        limit = self.fm.get_quota_limit()
        quota_text = f"quota {format_size(usage)} / unlimited"
        if limit is not None:
            quota_text = f"quota {format_size(usage)} / {format_size(limit)}"
        current_path = self.active_panel.current_path
        self.status_bar.set_context(self.parser.current_user, current_path, quota_text)
        if message:
            self.status_bar.set_message(
                f"{message} | User: {self.parser.current_user} | Path: {current_path} | {quota_text}"
            )


if __name__ == "__main__":
    app = FileManagerApp()
    app.run()
