from PyQt6 import QtCore, QtWidgets

from app.ui.widgets.card import Card


class PageLogs(QtWidgets.QWidget):
    """Simple console view for device logs."""

    sig_send_command = QtCore.pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        card = Card("Console / Logs")
        self.txt = QtWidgets.QTextEdit()
        self.txt.setReadOnly(True)
        card.body.addWidget(self.txt)

        controls = QtWidgets.QHBoxLayout()
        controls.setSpacing(8)
        self.entry = QtWidgets.QLineEdit()
        self.entry.setPlaceholderText("Escribe un comando serial...")
        self.entry.returnPressed.connect(self._emit_send_command)
        controls.addWidget(self.entry, 1)

        self.btn_send = QtWidgets.QPushButton("Enviar")
        self.btn_send.setProperty("primary", True)
        self.btn_send.clicked.connect(self._emit_send_command)
        controls.addWidget(self.btn_send)

        self.btn_clear = QtWidgets.QPushButton("Limpiar")
        self.btn_clear.setProperty("ghost", True)
        self.btn_clear.clicked.connect(self.clear)
        controls.addWidget(self.btn_clear)

        card.body.addLayout(controls)
        root.addWidget(card)

    def append_line(self, text: str) -> None:
        self.txt.append(text)

    def clear(self) -> None:
        self.txt.clear()

    def _emit_send_command(self) -> None:
        command = self.entry.text().strip()
        if not command:
            return
        self.sig_send_command.emit(command)
        self.entry.clear()
