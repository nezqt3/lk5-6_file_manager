from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Header, Footer, Static

from file_manager.ui.css.main_styles import styles

from file_manager.ui.widgets.file_panel import FilePanel
from file_manager.ui.widgets.command_bar import CommandBar
from file_manager.ui.widgets.status_bar import StatusBar


class FileManagerApp(App):
    TITLE = "Python File Manager"
    SUB_TITLE = "Textual UI"

    CSS = styles

    BINDINGS = [
        ("q", "quit", "Exit"),
        ("tab", "switch_panel", "Switch panel"),
        ("f5", "copy_file", "Copy"),
        ("f6", "move_file", "Move"),
        ("f7", "create_directory", "Mkdir"),
        ("f8", "delete_item", "Delete"),
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
        self.left_panel = self.query_one("#left-panel", FilePanel)
        self.right_panel = self.query_one("#right-panel", FilePanel)
        self.command_bar = self.query_one("#command-bar", CommandBar)
        self.status_bar = self.query_one("#status-bar", StatusBar)

        self.active_panel = self.left_panel
        self.inactive_panel = self.right_panel

        self.left_panel.set_active(True)
        self.right_panel.set_active(False)

        self.left_panel.load_demo_files()
        self.right_panel.load_demo_files()

        self.status_bar.set_message("Ready")

    def action_switch_panel(self) -> None:
        self.active_panel.set_active(False)
        self.inactive_panel.set_active(True)

        self.active_panel, self.inactive_panel = (
            self.inactive_panel,
            self.active_panel,
        )

        self.status_bar.set_message(f"Active panel: {self.active_panel.title}")

    def action_refresh(self) -> None:
        self.active_panel.refresh_files()
        self.status_bar.set_message("Panel refreshed")

    def action_copy_file(self) -> None:
        selected = self.active_panel.get_selected_item()
        if selected in {"nothing selected", "empty"}:
            self.status_bar.set_message("Copy failed: nothing selected")
            return

        if selected in self.inactive_panel.files:
            self.status_bar.set_message(f"Copy skipped: {selected} already exists")
            return

        self.inactive_panel.set_files([*self.inactive_panel.files, selected])
        self.status_bar.set_message(f"Copied: {selected}")

    def action_move_file(self) -> None:
        selected = self.active_panel.get_selected_item()
        self.status_bar.set_message(f"Move: {selected}")

        # TODO: подключить свою функцию перемещения

    def action_create_directory(self) -> None:
        self.status_bar.set_message("Create directory")

        # TODO: открыть ввод имени папки и подключить mkdir

    def action_delete_item(self) -> None:
        selected = self.active_panel.get_selected_item()
        self.status_bar.set_message(f"Delete: {selected}")

        # TODO: подключить удаление файла/папки


if __name__ == "__main__":
    app = FileManagerApp()
    app.run()
