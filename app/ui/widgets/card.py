from PyQt6 import QtWidgets

from .basics import HLine


class Card(QtWidgets.QFrame):
    """Reusable rounded container with optional title header."""

    def __init__(self, title: str | None = None):
        super().__init__()
        self.setProperty("card", True)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)
        if title:
            header = QtWidgets.QLabel(title)
            header.setProperty("cardTitle", True)
            layout.addWidget(header)
            layout.addWidget(HLine())
        self.body: QtWidgets.QVBoxLayout = layout
