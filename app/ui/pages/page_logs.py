from PyQt6 import QtWidgets

from app.ui.widgets.card import Card


class PageLogs(QtWidgets.QWidget):
    """Simple console view for device logs."""

    def __init__(self) -> None:
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        card = Card("Console / Logs")
        self.txt = QtWidgets.QTextEdit()
        self.txt.setReadOnly(True)
        card.body.addWidget(self.txt)
        root.addWidget(card)

    def append_line(self, text: str) -> None:
        self.txt.append(text)

    def clear(self) -> None:
        self.txt.clear()
