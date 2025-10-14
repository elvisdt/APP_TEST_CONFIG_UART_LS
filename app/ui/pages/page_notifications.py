from __future__ import annotations

from PyQt6 import QtCore, QtWidgets

from app.ui.widgets.card import Card


class PageNotifications(QtWidgets.QWidget):
    """Gestiona canales de alerta, grupos de WhatsApp y plantillas de mensaje."""

    sig_channels_changed = QtCore.pyqtSignal(dict)
    sig_groups_changed = QtCore.pyqtSignal(list)
    sig_group_test = QtCore.pyqtSignal(dict)
    sig_templates_saved = QtCore.pyqtSignal(dict)

    _DEFAULT_GROUPS = [
        {"name": "Seguridad municipal", "number": "+51999900001", "notes": "Despacho central"},
        {"name": "Voluntarios", "number": "+51999900002", "notes": "Brigadistas"},
    ]

    _DEFAULT_TEMPLATES = {
        "alarma": "ALERTA {zona}: Evento {evento} detectado a las {hora}.",
        "restauracion": "RESTABLECIDO {zona}: Estado normal desde {hora}.",
        "prueba": "Prueba de sirena ejecutada en {hora}. Confirmar recepcion.",
        "general": "Mensaje :: {contenido}",
    }

    def __init__(self) -> None:
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        self._build_channels_card(root)
        self._build_groups_card(root)
        self._build_templates_card(root)

        self.reset_channels()
        self.reset_groups()
        self.reset_templates()

    # ------------------------------------------------------------------
    def _build_channels_card(self, root: QtWidgets.QVBoxLayout) -> None:
        card = Card("Canales de alerta habilitados")

        grid = QtWidgets.QGridLayout()
        grid.setHorizontalSpacing(18)
        grid.setVerticalSpacing(10)

        self.chk_whatsapp = QtWidgets.QCheckBox("WhatsApp (via servidor MQTT)")
        self.chk_mobile = QtWidgets.QCheckBox("App movil Linseg")
        self.chk_sms = QtWidgets.QCheckBox("SMS de respaldo")
        self.chk_email = QtWidgets.QCheckBox("Correo electronico")
        self.chk_voice = QtWidgets.QCheckBox("Llamada de voz automatizada")

        for idx, widget in enumerate([
            self.chk_whatsapp,
            self.chk_mobile,
            self.chk_sms,
            self.chk_email,
            self.chk_voice,
        ]):
            row = idx // 2
            col = idx % 2
            grid.addWidget(widget, row, col)

        card.body.addLayout(grid)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        self.btn_channels_reset = QtWidgets.QPushButton("Restaurar")
        self.btn_channels_reset.setProperty("ghost", True)
        self.btn_channels_apply = QtWidgets.QPushButton("Aplicar canales")
        self.btn_channels_apply.setProperty("primary", True)
        buttons.addWidget(self.btn_channels_reset)
        buttons.addWidget(self.btn_channels_apply)
        card.body.addLayout(buttons)

        root.addWidget(card)

        self.btn_channels_reset.clicked.connect(self.reset_channels)
        self.btn_channels_apply.clicked.connect(lambda: self.sig_channels_changed.emit(self.channels()))

    def _build_groups_card(self, root: QtWidgets.QVBoxLayout) -> None:
        card = Card("Grupos y destinatarios")

        layout = QtWidgets.QHBoxLayout()
        layout.setSpacing(12)

        self.lst_groups = QtWidgets.QListWidget()
        self.lst_groups.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.lst_groups.currentRowChanged.connect(self._sync_group_details)
        layout.addWidget(self.lst_groups, 1)

        form_box = QtWidgets.QVBoxLayout()
        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        form.setFormAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        self.edit_group_name = QtWidgets.QLineEdit()
        self.edit_group_number = QtWidgets.QLineEdit()
        self.edit_group_number.setPlaceholderText("+51999900000")
        self.edit_group_notes = QtWidgets.QPlainTextEdit()
        self.edit_group_notes.setPlaceholderText("Notas u objetivos del grupo")
        self.edit_group_notes.setFixedHeight(72)

        form.addRow("Nombre", self.edit_group_name)
        form.addRow("Numero", self.edit_group_number)
        form.addRow("Notas", self.edit_group_notes)
        form_box.addLayout(form)

        actions = QtWidgets.QHBoxLayout()
        actions.addStretch(1)
        self.btn_group_new = QtWidgets.QPushButton("Nuevo grupo")
        self.btn_group_new.setProperty("ghost", True)
        self.btn_group_delete = QtWidgets.QPushButton("Eliminar")
        self.btn_group_delete.setProperty("ghost", True)
        self.btn_group_sync = QtWidgets.QPushButton("Sincronizar catalogo")
        self.btn_group_sync.setProperty("ghost", True)
        actions.addWidget(self.btn_group_new)
        actions.addWidget(self.btn_group_delete)
        actions.addWidget(self.btn_group_sync)
        form_box.addLayout(actions)

        test_row = QtWidgets.QHBoxLayout()
        test_row.addStretch(1)
        self.btn_group_test = QtWidgets.QPushButton("Enviar prueba")
        self.btn_group_test.setProperty("ghost", True)
        self.btn_group_save = QtWidgets.QPushButton("Guardar cambios")
        self.btn_group_save.setProperty("primary", True)
        test_row.addWidget(self.btn_group_test)
        test_row.addWidget(self.btn_group_save)
        form_box.addLayout(test_row)

        layout.addLayout(form_box, 1)
        card.body.addLayout(layout)

        footer = QtWidgets.QHBoxLayout()
        footer.addStretch(1)
        self.btn_groups_apply = QtWidgets.QPushButton("Aplicar destinatarios")
        self.btn_groups_apply.setProperty("primary", True)
        footer.addWidget(self.btn_groups_apply)
        card.body.addLayout(footer)

        root.addWidget(card)

        self.btn_group_new.clicked.connect(self._add_group)
        self.btn_group_delete.clicked.connect(self._remove_group)
        self.btn_group_save.clicked.connect(self._update_current_group)
        self.btn_group_test.clicked.connect(self._emit_group_test)
        self.btn_groups_apply.clicked.connect(lambda: self.sig_groups_changed.emit(self.groups()))

    def _build_templates_card(self, root: QtWidgets.QVBoxLayout) -> None:
        card = Card("Plantillas de mensaje")

        self.tabs_templates = QtWidgets.QTabWidget()
        self.edit_template_alarm = QtWidgets.QPlainTextEdit()
        self.edit_template_restore = QtWidgets.QPlainTextEdit()
        self.edit_template_test = QtWidgets.QPlainTextEdit()
        self.edit_template_general = QtWidgets.QPlainTextEdit()

        self._add_template_tab("Alarma", self.edit_template_alarm)
        self._add_template_tab("Restauracion", self.edit_template_restore)
        self._add_template_tab("Prueba", self.edit_template_test)
        self._add_template_tab("General", self.edit_template_general)

        card.body.addWidget(self.tabs_templates)

        hint = QtWidgets.QLabel("Variables soportadas: {zona}, {evento}, {hora}, {fecha}, {contenido}")
        hint.setProperty("muted", True)
        card.body.addWidget(hint)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        self.btn_templates_reset = QtWidgets.QPushButton("Restaurar predeterminado")
        self.btn_templates_reset.setProperty("ghost", True)
        self.btn_templates_save = QtWidgets.QPushButton("Guardar plantillas")
        self.btn_templates_save.setProperty("primary", True)
        buttons.addWidget(self.btn_templates_reset)
        buttons.addWidget(self.btn_templates_save)
        card.body.addLayout(buttons)

        root.addWidget(card)

        self.btn_templates_reset.clicked.connect(self.reset_templates)
        self.btn_templates_save.clicked.connect(lambda: self.sig_templates_saved.emit(self.templates()))

    # ------------------------------------------------------------------
    def channels(self) -> dict:
        return {
            "whatsapp": self.chk_whatsapp.isChecked(),
            "mobile": self.chk_mobile.isChecked(),
            "sms": self.chk_sms.isChecked(),
            "email": self.chk_email.isChecked(),
            "voice": self.chk_voice.isChecked(),
        }

    def set_channels(self, values: dict[str, object]) -> None:
        for key, widget in (
            ("whatsapp", self.chk_whatsapp),
            ("mobile", self.chk_mobile),
            ("sms", self.chk_sms),
            ("email", self.chk_email),
            ("voice", self.chk_voice),
        ):
            widget.setChecked(bool(values.get(key, widget is self.chk_whatsapp or widget is self.chk_mobile)))

    def reset_channels(self) -> None:
        defaults = {
            "whatsapp": True,
            "mobile": True,
            "sms": False,
            "email": False,
            "voice": False,
        }
        self.set_channels(defaults)

    def groups(self) -> list[dict[str, str]]:
        data: list[dict[str, str]] = []
        for index in range(self.lst_groups.count()):
            item = self.lst_groups.item(index)
            payload = item.data(QtCore.Qt.ItemDataRole.UserRole)
            if isinstance(payload, dict):
                name = str(payload.get("name", item.text()))
                number = str(payload.get("number", ""))
                notes = str(payload.get("notes", ""))
            else:
                name = item.text()
                number = ""
                notes = ""
            data.append({"name": name, "number": number, "notes": notes})
        return data

    def set_groups(self, groups: list[dict[str, object]]) -> None:
        self.lst_groups.clear()
        for entry in groups:
            name = str(entry.get("name", "Grupo"))
            item = QtWidgets.QListWidgetItem(name)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, {
                "name": name,
                "number": str(entry.get("number", "")),
                "notes": str(entry.get("notes", "")),
            })
            self.lst_groups.addItem(item)
        if self.lst_groups.count():
            self.lst_groups.setCurrentRow(0)
        else:
            self._clear_group_details()

    def reset_groups(self) -> None:
        self.set_groups(self._DEFAULT_GROUPS)

    def templates(self) -> dict[str, str]:
        return {
            "alarma": self.edit_template_alarm.toPlainText().strip(),
            "restauracion": self.edit_template_restore.toPlainText().strip(),
            "prueba": self.edit_template_test.toPlainText().strip(),
            "general": self.edit_template_general.toPlainText().strip(),
        }

    def set_templates(self, templates: dict[str, object]) -> None:
        self.edit_template_alarm.setPlainText(str(templates.get("alarma", self._DEFAULT_TEMPLATES["alarma"])))
        self.edit_template_restore.setPlainText(str(templates.get("restauracion", self._DEFAULT_TEMPLATES["restauracion"])))
        self.edit_template_test.setPlainText(str(templates.get("prueba", self._DEFAULT_TEMPLATES["prueba"])))
        self.edit_template_general.setPlainText(str(templates.get("general", self._DEFAULT_TEMPLATES["general"])))

    def reset_templates(self) -> None:
        self.set_templates(self._DEFAULT_TEMPLATES)

    # ------------------------------------------------------------------
    def _add_template_tab(self, title: str, editor: QtWidgets.QPlainTextEdit) -> None:
        editor.setPlaceholderText("Escribe el mensaje que recibira el usuario")
        editor.setTabStopDistance(4 * editor.fontMetrics().horizontalAdvance(" "))
        self.tabs_templates.addTab(editor, title)

    def _sync_group_details(self, index: int) -> None:
        if index < 0:
            self._clear_group_details()
            return
        item = self.lst_groups.item(index)
        payload = item.data(QtCore.Qt.ItemDataRole.UserRole)
        data = payload if isinstance(payload, dict) else {"name": item.text()}  # type: ignore[assignment]
        self.edit_group_name.setText(str(data.get("name", "")))
        self.edit_group_number.setText(str(data.get("number", "")))
        self.edit_group_notes.setPlainText(str(data.get("notes", "")))

    def _clear_group_details(self) -> None:
        self.edit_group_name.clear()
        self.edit_group_number.clear()
        self.edit_group_notes.clear()

    def _add_group(self) -> None:
        item = QtWidgets.QListWidgetItem("Nuevo grupo")
        item.setData(QtCore.Qt.ItemDataRole.UserRole, {"name": "Nuevo grupo", "number": "", "notes": ""})
        self.lst_groups.addItem(item)
        self.lst_groups.setCurrentItem(item)

    def _remove_group(self) -> None:
        row = self.lst_groups.currentRow()
        if row >= 0:
            self.lst_groups.takeItem(row)
            if self.lst_groups.count():
                self.lst_groups.setCurrentRow(min(row, self.lst_groups.count() - 1))
            else:
                self._clear_group_details()

    def _update_current_group(self) -> None:
        row = self.lst_groups.currentRow()
        if row < 0:
            return
        item = self.lst_groups.item(row)
        name = self.edit_group_name.text().strip() or "Grupo"
        item.setText(name)
        item.setData(QtCore.Qt.ItemDataRole.UserRole, {
            "name": name,
            "number": self.edit_group_number.text().strip(),
            "notes": self.edit_group_notes.toPlainText().strip(),
        })

    def _emit_group_test(self) -> None:
        row = self.lst_groups.currentRow()
        if row < 0:
            return
        item = self.lst_groups.item(row)
        payload = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if isinstance(payload, dict):
            self.sig_group_test.emit({
                "name": str(payload.get("name", item.text())),
                "number": str(payload.get("number", "")),
                "notes": str(payload.get("notes", "")),
            })


__all__ = ["PageNotifications"]

