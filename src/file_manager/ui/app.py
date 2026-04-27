from file_manager.core.file_manager import FileManager

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Button
from textual.widgets import Header, Footer

from file_manager.ui.css import main_styles, dialog_styles

from file_manager.ui.widgets.file_panel import FilePanel
from file_manager.ui.widgets.command_bar import CommandBar
from file_manager.ui.widgets.status_bar import StatusBar


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

class FileManagerApp(App):
    TITLE = "Python File Manager"
    SUB_TITLE = "Textual UI"

    CSS = main_styles

    BINDINGS = [
        ("q", "quit", "Exit"),
        ("tab", "switch_panel", "Switch panel"),

        ("f5", "copy_file", "Copy"),
        ("c", "copy_file", "Copy"),

        ("f6", "move_file", "Move"),
        ("m", "move_file", "Move"),

        ("f7", "create_directory", "Mkdir"),
        ("n", "create_directory", "Mkdir"),

        ("f8", "delete_item", "Delete"),
        ("d", "delete_item", "Delete"),

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
        self.fm = FileManager("workspace")

        self.left_panel.set_path(".")
        self.right_panel.set_path(".")

        self.left_panel.set_active(True)
        self.right_panel.set_active(False)

        self.load_panel_files(self.left_panel)
        self.load_panel_files(self.right_panel)

    def action_switch_panel(self) -> None:
        self.active_panel.set_active(False)
        self.inactive_panel.set_active(True)

        self.active_panel, self.inactive_panel = (
            self.inactive_panel,
            self.active_panel,
        )

        self.status_bar.set_message(f"Active panel: {self.active_panel.title}")

    def action_refresh(self) -> None:
        self.load_panel_files(self.active_panel)
        self.status_bar.set_message("Panel refreshed")
        
    def load_panel_files(self, panel: FilePanel) -> None:
        files = self.fm.list_files(panel.current_path)
        panel.set_files(files)

    def action_copy_file(self) -> None:
        selected = self.active_panel.get_selected_item()

        if not selected or selected == "nothing selected":
            self.status_bar.set_message("Nothing selected")
            return

        try:
            self.fm.copy(
                selected,
                self.active_panel.current_path,
                self.inactive_panel.current_path,
            )

            self.load_panel_files(self.inactive_panel)
            self.status_bar.set_message(f"Copied: {selected}")

        except Exception as error:
            self.status_bar.set_message(f"Error: {error}")

    def action_move_file(self) -> None:
        selected = self.active_panel.get_selected_item()

        if not selected or selected == "nothing selected":
            self.status_bar.set_message("Nothing selected")
            return

        try:
            self.fm.move(
                selected,
                self.active_panel.current_path,
                self.inactive_panel.current_path,
            )

            self.load_panel_files(self.active_panel)
            self.load_panel_files(self.inactive_panel)

            self.status_bar.set_message(f"Moved: {selected}")

        except Exception as error:
            self.status_bar.set_message(f"Error: {error}")

    def action_create_directory(self) -> None:
        self.push_screen(CreateDirectoryDialog(), self.create_directory_callback)
        
    def create_directory_callback(self, dirname: str | None) -> None:
        if not dirname:
            self.status_bar.set_message("Directory creation cancelled")
            return

        try:
            self.fm.mkdir(dirname, self.active_panel.current_path)
            self.load_panel_files(self.active_panel)
            self.status_bar.set_message(f"Directory created: {dirname}")

        except Exception as error:
            self.status_bar.set_message(f"Error: {error}")

    def action_delete_item(self) -> None:
        selected = self.active_panel.get_selected_item()

        if not selected or selected == "nothing selected":
            self.status_bar.set_message("Nothing selected")
            return

        try:
            self.fm.delete(selected, self.active_panel.current_path)
            self.load_panel_files(self.active_panel)

            self.status_bar.set_message(f"Deleted: {selected}")

        except Exception as error:
            self.status_bar.set_message(f"Error: {error}")


if __name__ == "__main__":
    app = FileManagerApp()
    app.run()
