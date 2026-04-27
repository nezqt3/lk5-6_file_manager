from textual.app import ComposeResult
from textual.widgets import Static, ListView, ListItem, Label


class FilePanel(Static):
    def __init__(self, title: str, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.current_path = "/"
        self.files = []

    def compose(self) -> ComposeResult:
        yield Label(f"{self.title}: {self.current_path}", id="panel-title")
        yield ListView(id="file-list")

    def on_mount(self) -> None:
        self.file_list = self.query_one("#file-list", ListView)
        self.panel_title = self.query_one("#panel-title", Label)

    def set_active(self, is_active: bool) -> None:
        if is_active:
            self.add_class("active")
        else:
            self.remove_class("active")

    def set_path(self, path: str) -> None:
        self.current_path = path
        self.panel_title.update(f"{self.title}: {self.current_path}")

    def set_files(self, files: list[str]) -> None:
        self.files = files
        self.file_list.clear()

        for file_name in files:
            self.file_list.append(
                ListItem(Label(file_name))
            )

    def load_demo_files(self) -> None:
        demo_files = [
            "[DIR] documents",
            "[DIR] images",
            "[DIR] projects",
            "notes.txt",
            "main.py",
            "archive.zip",
        ]

        self.set_files(demo_files)

    def refresh_files(self) -> None:
        # TODO: здесь потом вызываешь свою функцию получения файлов
        self.set_files(self.files)

    def get_selected_item(self) -> str:
        if self.file_list.index is None:
            return "nothing selected"

        if not self.files:
            return "empty"

        return self.files[self.file_list.index]