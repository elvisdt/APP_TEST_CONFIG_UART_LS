from __future__ import annotations
from PyQt6 import QtCore, QtWidgets

class SideBar(QtWidgets.QFrame):
    """
    Barra lateral con botones de páginas.
    Señales:
      pageRequested(str) -> nombre de la página
    """
    pageRequested = QtCore.pyqtSignal(str)

    def __init__(self, pages: list[str], app_name: str = "Linseg QC1", version: str = "v1.0.0"):
        super().__init__()
        self.setObjectName("SideBar")

        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(8)

        logo = QtWidgets.QLabel(app_name)
        logo.setStyleSheet("font-weight:700; font-size:16px;")
        lay.addWidget(logo)

        lay.addSpacing(8)

        self._group = QtWidgets.QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[str, QtWidgets.QPushButton] = {}

        for i, name in enumerate(pages):
            btn = QtWidgets.QPushButton(name)
            btn.setCheckable(True)
            btn.setProperty("sideBtn", True)
            self._group.addButton(btn, i)
            self._buttons[name] = btn
            lay.addWidget(btn)
            btn.clicked.connect(lambda _, n=name: self.pageRequested.emit(n))

        lay.addStretch(1)

        lbl_ver = QtWidgets.QLabel(version)
        lbl_ver.setProperty("muted", True)
        lay.addWidget(lbl_ver)

    def setActive(self, name: str) -> None:
        btn = self._buttons.get(name)
        if not btn:
            return
        btn.setChecked(True)
        # Forzamos refresco de pseudo-estados QSS
        btn.style().unpolish(btn)
        btn.style().polish(btn)
