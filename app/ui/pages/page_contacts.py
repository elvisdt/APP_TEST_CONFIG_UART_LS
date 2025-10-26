from __future__ import annotations

from PyQt6 import QtCore, QtWidgets

from app.ui.widgets.card import Card


class PageContacts(QtWidgets.QWidget):
    """Contacts configuration page with CSV shortcuts."""

    sig_import_auth = QtCore.pyqtSignal(str)
    sig_export_auth = QtCore.pyqtSignal(str)
    sig_import_gsm = QtCore.pyqtSignal(str)
    sig_export_gsm = QtCore.pyqtSignal(str)
    sig_rf_scan = QtCore.pyqtSignal()
    sig_rf_link = QtCore.pyqtSignal(str, str)

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

        manual_card = Card("Agregar manualmente")
        manual_card.body.setSpacing(8)
        auth_label = QtWidgets.QLabel("Autorizados")
        auth_label.setProperty("muted", True)
        auth_row = QtWidgets.QHBoxLayout()
        auth_row.setSpacing(8)
        self.input_auth_number = QtWidgets.QLineEdit()
        self.input_auth_number.setPlaceholderText("Número E.164")
        self.btn_add_auth = QtWidgets.QPushButton("Añadir")
        self.btn_add_auth.setProperty("primary", True)
        auth_row.addWidget(self.input_auth_number)
        auth_row.addWidget(self.btn_add_auth)
        manual_card.body.addWidget(auth_label)
        manual_card.body.addLayout(auth_row)
        gsm_label = QtWidgets.QLabel("Predeterminados")
        gsm_label.setProperty("muted", True)
        gsm_row = QtWidgets.QHBoxLayout()
        gsm_row.setSpacing(8)
        self.input_gsm_label = QtWidgets.QLineEdit()
        self.input_gsm_label.setPlaceholderText("Etiqueta")
        self.input_gsm_number = QtWidgets.QLineEdit()
        self.input_gsm_number.setPlaceholderText("Número")
        self.btn_add_gsm = QtWidgets.QPushButton("Añadir")
        self.btn_add_gsm.setProperty("primary", True)
        gsm_row.addWidget(self.input_gsm_label, 1)
        gsm_row.addWidget(self.input_gsm_number, 1)
        gsm_row.addWidget(self.btn_add_gsm)
        manual_card.body.addWidget(gsm_label)
        manual_card.body.addLayout(gsm_row)
        right.addWidget(manual_card)

        rf_card = Card("Remotos RF")
        rf_card.body.setSpacing(8)
        rf_header = QtWidgets.QHBoxLayout()
        rf_header.setSpacing(8)
        self.btn_rf_scan = QtWidgets.QPushButton("Escanear RF")
        self.btn_rf_scan.setProperty("primary", True)
        self.lbl_rf_status = QtWidgets.QLabel("Listo para escanear")
        self.lbl_rf_status.setProperty("muted", True)
        rf_header.addWidget(self.btn_rf_scan)
        rf_header.addWidget(self.lbl_rf_status, 1)
        rf_card.body.addLayout(rf_header)

        self.tbl_rf = QtWidgets.QTableWidget(10, 2)
        self.tbl_rf.setHorizontalHeaderLabels(["RF ID", "Contacto"])
        self.tbl_rf.horizontalHeader().setStretchLastSection(True)
        self.tbl_rf.verticalHeader().setVisible(True)
        self.tbl_rf.setShowGrid(False)
        for row in range(10):
            for col in range(2):
                self.tbl_rf.setItem(row, col, QtWidgets.QTableWidgetItem(""))
        rf_card.body.addWidget(self.tbl_rf)

        rf_link = QtWidgets.QHBoxLayout()
        rf_link.setSpacing(8)
        self.input_rf_id = QtWidgets.QLineEdit()
        self.input_rf_id.setPlaceholderText("ID RF (capturado)")
        self.input_rf_contact = QtWidgets.QLineEdit()
        self.input_rf_contact.setPlaceholderText("Número o alias de contacto")
        self.btn_rf_link = QtWidgets.QPushButton("Vincular contacto")
        self.btn_rf_link.setProperty("primary", True)
        rf_link.addWidget(self.input_rf_id, 1)
        rf_link.addWidget(self.input_rf_contact, 1)
        rf_link.addWidget(self.btn_rf_link)
        rf_card.body.addLayout(rf_link)
        right.addWidget(rf_card)

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

        self.btn_add_auth.clicked.connect(self._add_auth_manual)
        self.btn_add_gsm.clicked.connect(self._add_gsm_manual)
        self.btn_rf_scan.clicked.connect(self._emit_rf_scan)
        self.btn_rf_link.clicked.connect(self._emit_rf_link)
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

    def set_rf_entries(self, entries: list[tuple[str, str]]) -> None:
        for row in range(self.tbl_rf.rowCount()):
            rf_item = self.tbl_rf.item(row, 0)
            contact_item = self.tbl_rf.item(row, 1)
            value_rf = ""
            value_contact = ""
            if row < len(entries):
                value_rf, value_contact = entries[row]
            if rf_item is None:
                self.tbl_rf.setItem(row, 0, QtWidgets.QTableWidgetItem(value_rf))
            else:
                rf_item.setText(value_rf)
            if contact_item is None:
                self.tbl_rf.setItem(row, 1, QtWidgets.QTableWidgetItem(value_contact))
            else:
                contact_item.setText(value_contact)

    def append_rf_entry(self, rf_id: str, contact: str) -> None:
        for row in range(self.tbl_rf.rowCount()):
            rf_item = self.tbl_rf.item(row, 0)
            contact_item = self.tbl_rf.item(row, 1)
            current_rf = rf_item.text().strip() if rf_item else ""
            current_contact = contact_item.text().strip() if contact_item else ""
            if not current_rf and not current_contact:
                if rf_item is None:
                    self.tbl_rf.setItem(row, 0, QtWidgets.QTableWidgetItem(rf_id))
                else:
                    rf_item.setText(rf_id)
                if contact_item is None:
                    self.tbl_rf.setItem(row, 1, QtWidgets.QTableWidgetItem(contact))
                else:
                    contact_item.setText(contact)
                self.tbl_rf.setCurrentCell(row, 0)
                return
        QtWidgets.QMessageBox.information(self, "Sin espacio", "No hay filas libres en remotos RF.")

    def _emit_rf_scan(self) -> None:
        self.lbl_rf_status.setText("Escaneando…")
        self.sig_rf_scan.emit()

    def rf_scan_finished(self, success: bool, message: str | None = None) -> None:
        if success:
            text = message or "RF detectado."
        else:
            text = message or "Sin respuesta."
        self.lbl_rf_status.setText(text)

    def _emit_rf_link(self) -> None:
        rf_id = self.input_rf_id.text().strip()
        contact = self.input_rf_contact.text().strip()
        if not rf_id or not contact:
            QtWidgets.QMessageBox.warning(self, "Datos incompletos", "Completa el ID RF y el contacto.")
            return
        self.sig_rf_link.emit(rf_id, contact)
        self.input_rf_id.clear()
        self.input_rf_contact.clear()

    def _add_auth_manual(self) -> None:
        number = self.input_auth_number.text().strip()
        if not number:
            return
        for idx in range(self.tbl_auth.rowCount()):
            item = self.tbl_auth.item(idx, 0)
            current = item.text().strip() if item else ""
            if not current:
                if item is None:
                    item = QtWidgets.QTableWidgetItem(number)
                    self.tbl_auth.setItem(idx, 0, item)
                else:
                    item.setText(number)
                self.tbl_auth.setCurrentCell(idx, 0)
                self.input_auth_number.clear()
                return
        QtWidgets.QMessageBox.information(self, "Sin espacio", "No hay filas libres en autorizados.")

    def _add_gsm_manual(self) -> None:
        label = self.input_gsm_label.text().strip()
        number = self.input_gsm_number.text().strip()
        if not number:
            return
        for idx in range(self.tbl_gsm.rowCount()):
            label_item = self.tbl_gsm.item(idx, 0)
            number_item = self.tbl_gsm.item(idx, 1)
            current_label = label_item.text().strip() if label_item else ""
            current_number = number_item.text().strip() if number_item else ""
            if not current_label and not current_number:
                if label_item is None:
                    self.tbl_gsm.setItem(idx, 0, QtWidgets.QTableWidgetItem(label))
                else:
                    label_item.setText(label)
                if number_item is None:
                    self.tbl_gsm.setItem(idx, 1, QtWidgets.QTableWidgetItem(number))
                else:
                    number_item.setText(number)
                self.tbl_gsm.setCurrentCell(idx, 0)
                self.input_gsm_label.clear()
                self.input_gsm_number.clear()
                return
        QtWidgets.QMessageBox.information(self, "Sin espacio", "No hay filas libres en predeterminados.")
