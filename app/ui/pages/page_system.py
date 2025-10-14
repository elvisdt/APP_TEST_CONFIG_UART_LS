from PyQt6 import QtWidgets

from app.ui.widgets.card import Card


class PageSystem(QtWidgets.QWidget):
    """System level settings placeholders."""

    def __init__(self) -> None:
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        card = Card("Sistema")
        grid = QtWidgets.QGridLayout()
        grid.setVerticalSpacing(8)

        defaults = [
            ("Baudios", "115200"),
            ("Firma", "QC1"),
            ("Modelo", "ALR-LTE"),
            ("Dev ID", "A1B2C3"),
        ]
        self.inputs: dict[str, QtWidgets.QLineEdit] = {}
        for row, (label, value) in enumerate(defaults):
            lbl = QtWidgets.QLabel(label)
            lbl.setProperty("muted", True)
            edit = QtWidgets.QLineEdit(value)
            self.inputs[label] = edit
            grid.addWidget(lbl, row, 0)
            grid.addWidget(edit, row, 1)

        button_row = QtWidgets.QHBoxLayout()
        button_row.addStretch(1)
        btn_defaults = QtWidgets.QPushButton("Restaurar fabrica")
        btn_defaults.setProperty("ghost", True)
        btn_save = QtWidgets.QPushButton("Guardar NVS")
        btn_save.setProperty("primary", True)
        button_row.addWidget(btn_defaults)
        button_row.addWidget(btn_save)

        card.body.addLayout(grid)
        card.body.addLayout(button_row)
        root.addWidget(card)
