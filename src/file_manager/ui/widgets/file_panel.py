from textual.app import ComposeResult
from textual.widgets import Static, ListView, ListItem, Label


class FilePanel(Static):
    def __init__(self, title: str, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.current_path = "."
        self.files: list[str] = []

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

        if files:
            self.file_list.index = 0

    def focus_list(self) -> None:
        self.file_list.focus()

    def get_selected_item(self) -> str | None:
        if self.file_list.index is None:
            return None

        if not self.files:
            return None

        return self.files[self.file_list.index]
