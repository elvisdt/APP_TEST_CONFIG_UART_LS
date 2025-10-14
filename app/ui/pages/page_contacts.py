from __future__ import annotations

from PyQt6 import QtCore, QtWidgets

from app.ui.widgets.card import Card


class PageContacts(QtWidgets.QWidget):
    """Contacts configuration page with CSV shortcuts."""

    sig_import_auth = QtCore.pyqtSignal(str)
    sig_export_auth = QtCore.pyqtSignal(str)
    sig_import_gsm = QtCore.pyqtSignal(str)
    sig_export_gsm = QtCore.pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        top_bar = QtWidgets.QHBoxLayout()
        self.btn_load = QtWidgets.QPushButton("Cargar desde archivo")
        self.btn_load.setProperty("ghost", True)
        self.btn_save = QtWidgets.QPushButton("Guardar a archivo")
        self.btn_save.setProperty("ghost", True)
        top_bar.addWidget(self.btn_load)
        top_bar.addWidget(self.btn_save)
        top_bar.addStretch(1)
        root.addLayout(top_bar)

        main_row = QtWidgets.QHBoxLayout()
        main_row.setSpacing(12)
        root.addLayout(main_row, 1)

        left = QtWidgets.QVBoxLayout()
        left.setSpacing(12)
        main_row.addLayout(left, 1)

        send_card = Card("Opciones de envio")
        send_grid = QtWidgets.QGridLayout()
        send_grid.setVerticalSpacing(8)
        lbl_allow = QtWidgets.QLabel("Permitir envio de reportes")
        lbl_allow.setProperty("muted", True)
        self.sw_allow = QtWidgets.QComboBox()
        self.sw_allow.addItems(["Deshabilitar", "Habilitar"])
        send_grid.addWidget(lbl_allow, 0, 0)
        send_grid.addWidget(self.sw_allow, 0, 1)
        lbl_order = QtWidgets.QLabel("Orden de reporte")
        lbl_order.setProperty("muted", True)
        self.cb_order = QtWidgets.QComboBox()
        self.cb_order.addItems([
            "WP => Ubicacion => Llamada",
            "WP => Llamada => Ubicacion",
        ])
        send_grid.addWidget(lbl_order, 1, 0)
        send_grid.addWidget(self.cb_order, 1, 1)
        send_card.body.addLayout(send_grid)
        left.addWidget(send_card)

        call_card = Card("Llamada entrante")
        call_row = QtWidgets.QHBoxLayout()
        call_row.setSpacing(8)
        for text in ("No hacer nada", "Colgar", "Reportar posicion", "Auto respuesta"):
            btn = QtWidgets.QPushButton(text)
            btn.setProperty("ghost", True)
            call_row.addWidget(btn)
        call_card.body.addLayout(call_row)
        left.addWidget(call_card)

        group_card = Card("Grupo / Alias")
        group_row = QtWidgets.QHBoxLayout()
        group_row.setSpacing(8)
        self.grp_name = QtWidgets.QLineEdit()
        self.grp_name.setPlaceholderText("Nombre del grupo (ej. ALARM_SMP)")
        self.grp_save = QtWidgets.QPushButton("Guardar")
        self.grp_save.setProperty("primary", True)
        group_row.addWidget(self.grp_name, 1)
        group_row.addWidget(self.grp_save)
        group_card.body.addLayout(group_row)
        left.addWidget(group_card)

        right = QtWidgets.QVBoxLayout()
        right.setSpacing(12)
        main_row.addLayout(right, 1)

        auth_card = Card("Numeros autorizados")
        self.tbl_auth = QtWidgets.QTableWidget(20, 1)
        self.tbl_auth.setHorizontalHeaderLabels(["Numero (E.164)"])
        self.tbl_auth.horizontalHeader().setStretchLastSection(True)
        self.tbl_auth.verticalHeader().setVisible(True)
        self.tbl_auth.verticalHeader().setDefaultAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter
        )
        self.tbl_auth.setShowGrid(False)
        for row in range(20):
            self.tbl_auth.setItem(row, 0, QtWidgets.QTableWidgetItem(""))
        auth_card.body.addWidget(self.tbl_auth)
        auth_btns = QtWidgets.QHBoxLayout()
        auth_btns.addStretch(1)
        self.btn_import_auth = QtWidgets.QPushButton("Importar CSV")
        self.btn_import_auth.setProperty("ghost", True)
        self.btn_export_auth = QtWidgets.QPushButton("Exportar CSV")
        self.btn_export_auth.setProperty("ghost", True)
        auth_btns.addWidget(self.btn_import_auth)
        auth_btns.addWidget(self.btn_export_auth)
        auth_card.body.addLayout(auth_btns)
        right.addWidget(auth_card)

        gsm_card = Card("Numeros predeterminados")
        self.tbl_gsm = QtWidgets.QTableWidget(10, 2)
        self.tbl_gsm.setHorizontalHeaderLabels(["Etiqueta", "Numero"])
        self.tbl_gsm.horizontalHeader().setStretchLastSection(True)
        self.tbl_gsm.verticalHeader().setVisible(True)
        self.tbl_gsm.setShowGrid(False)
        for row in range(10):
            for col in range(2):
                self.tbl_gsm.setItem(row, col, QtWidgets.QTableWidgetItem(""))
        gsm_card.body.addWidget(self.tbl_gsm)
        gsm_btns = QtWidgets.QHBoxLayout()
        gsm_btns.addStretch(1)
        self.btn_import_gsm = QtWidgets.QPushButton("Importar CSV")
        self.btn_import_gsm.setProperty("ghost", True)
        self.btn_export_gsm = QtWidgets.QPushButton("Exportar CSV")
        self.btn_export_gsm.setProperty("ghost", True)
        gsm_btns.addWidget(self.btn_import_gsm)
        gsm_btns.addWidget(self.btn_export_gsm)
        gsm_card.body.addLayout(gsm_btns)
        right.addWidget(gsm_card)

        self.btn_import_auth.clicked.connect(self._choose_import_auth)
        self.btn_export_auth.clicked.connect(self._choose_export_auth)
        self.btn_import_gsm.clicked.connect(self._choose_import_gsm)
        self.btn_export_gsm.clicked.connect(self._choose_export_gsm)

    def _choose_import_auth(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Importar numeros autorizados",
            "",
            "CSV (*.csv)",
        )
        if path:
            self.sig_import_auth.emit(path)

    def _choose_export_auth(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Exportar numeros autorizados",
            "autorizados.csv",
            "CSV (*.csv)",
        )
        if path:
            self.sig_export_auth.emit(path)

    def _choose_import_gsm(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Importar numeros predeterminados",
            "",
            "CSV (*.csv)",
        )
        if path:
            self.sig_import_gsm.emit(path)

    def _choose_export_gsm(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Exportar numeros predeterminados",
            "predefinidos.csv",
            "CSV (*.csv)",
        )
        if path:
            self.sig_export_gsm.emit(path)

    def fill_auth(self, numbers: list[str]) -> None:
        for idx in range(20):
            item = self.tbl_auth.item(idx, 0)
            value = numbers[idx] if idx < len(numbers) else ""
            if item is None:
                item = QtWidgets.QTableWidgetItem(value)
                self.tbl_auth.setItem(idx, 0, item)
            else:
                item.setText(value)

    def read_auth(self) -> list[str]:
        result: list[str] = []
        for idx in range(20):
            item = self.tbl_auth.item(idx, 0)
            text = item.text().strip() if item else ""
            if text:
                result.append(text)
        return result

    def fill_gsm(self, pairs: list[tuple[str, str]]) -> None:
        for idx in range(10):
            label = ""
            number = ""
            if idx < len(pairs):
                label, number = pairs[idx]
            for col, value in enumerate((label, number)):
                item = self.tbl_gsm.item(idx, col)
                if item is None:
                    self.tbl_gsm.setItem(idx, col, QtWidgets.QTableWidgetItem(value))
                else:
                    item.setText(value)

    def read_gsm(self) -> list[tuple[str, str]]:
        data: list[tuple[str, str]] = []
        for idx in range(10):
            label_item = self.tbl_gsm.item(idx, 0)
            number_item = self.tbl_gsm.item(idx, 1)
            label = label_item.text().strip() if label_item else ""
            number = number_item.text().strip() if number_item else ""
            if label or number:
                data.append((label, number))
        return data
