from __future__ import annotations

from collections.abc import Mapping, Sequence

from PyQt6 import QtCore, QtWidgets

from app.ui.widgets.card import Card


class PageAudio(QtWidgets.QWidget):
    """Audio management page with slot overview and quick actions."""

    sig_refresh_slots = QtCore.pyqtSignal()
    sig_control_slot = QtCore.pyqtSignal(int, str, int, bool)
    sig_stop_all = QtCore.pyqtSignal()
    sig_upload_audio = QtCore.pyqtSignal(int, str, bool)

    _TABLE_COLUMNS = ("slot", "type", "duration", "status", "size", "encrypted")

    def __init__(self) -> None:
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        self._build_slots_card(root)
        self._build_controls_card(root)
        self._build_upload_card(root)

        self.set_slots([])
        self._update_upload_enabled()

    # ------------------------------------------------------------------
    def _build_slots_card(self, root: QtWidgets.QVBoxLayout) -> None:
        card = Card("Audios - Slots (1..4)")

        actions = QtWidgets.QHBoxLayout()
        actions.addStretch(1)
        self.btn_refresh = QtWidgets.QPushButton("Actualizar")
        self.btn_refresh.setProperty("ghost", True)
        actions.addWidget(self.btn_refresh)
        card.body.addLayout(actions)

        self.tbl_slots = QtWidgets.QTableWidget(4, len(self._TABLE_COLUMNS))
        headers = ["Slot", "Tipo", "Dur (s)", "Estado", "Tam", "ENC"]
        self.tbl_slots.setHorizontalHeaderLabels(headers)
        self.tbl_slots.verticalHeader().setVisible(False)
        self.tbl_slots.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_slots.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tbl_slots.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_slots.setShowGrid(False)
        self.tbl_slots.setAlternatingRowColors(False)
        self.tbl_slots.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.tbl_slots.setMinimumHeight(160)
        header = self.tbl_slots.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        for col in range(1, len(self._TABLE_COLUMNS)):
            header.setSectionResizeMode(col, QtWidgets.QHeaderView.ResizeMode.Stretch)
        for row in range(self.tbl_slots.rowCount()):
            self.tbl_slots.setRowHeight(row, 32)
        card.body.addWidget(self.tbl_slots)

        root.addWidget(card)

        self.btn_refresh.clicked.connect(self.sig_refresh_slots.emit)
        self.tbl_slots.itemSelectionChanged.connect(self._sync_slot_from_selection)

    def _build_controls_card(self, root: QtWidgets.QVBoxLayout) -> None:
        card = Card("Controles rapidos")

        controls = QtWidgets.QHBoxLayout()
        controls.setSpacing(12)

        self.spin_slot = QtWidgets.QSpinBox()
        self.spin_slot.setRange(1, 4)
        self.spin_slot.setValue(1)

        self.combo_action = QtWidgets.QComboBox()
        self.combo_action.addItem("Reproducir", "play")
        self.combo_action.addItem("Detener", "stop")
        self.combo_action.addItem("Probar bocina", "test")

        self.spin_duration = QtWidgets.QSpinBox()
        self.spin_duration.setRange(5, 600)
        self.spin_duration.setSingleStep(5)
        self.spin_duration.setValue(60)
        self.spin_duration.setSuffix(" s")

        self.chk_loop = QtWidgets.QCheckBox("Loop")

        self.btn_execute = QtWidgets.QPushButton("Enviar orden")
        self.btn_execute.setProperty("primary", True)
        self.btn_stop_all = QtWidgets.QPushButton("Detener todo")
        self.btn_stop_all.setProperty("ghost", True)

        for label, widget in (
            ("Slot", self.spin_slot),
            ("Accion", self.combo_action),
            ("Duracion", self.spin_duration),
        ):
            col = QtWidgets.QVBoxLayout()
            lbl = QtWidgets.QLabel(label)
            lbl.setProperty("muted", True)
            col.addWidget(lbl)
            col.addWidget(widget)
            controls.addLayout(col)

        side = QtWidgets.QVBoxLayout()
        side.setSpacing(6)
        side.addWidget(self.chk_loop)
        side.addStretch(1)
        side.addWidget(self.btn_execute)
        side.addWidget(self.btn_stop_all)
        controls.addLayout(side)

        card.body.addLayout(controls)
        root.addWidget(card)

        self.btn_execute.clicked.connect(self._emit_control_slot)
        self.btn_stop_all.clicked.connect(self.sig_stop_all.emit)

    def _build_upload_card(self, root: QtWidgets.QVBoxLayout) -> None:
        card = Card("Subir audio")

        top_row = QtWidgets.QHBoxLayout()
        self.edit_file = QtWidgets.QLineEdit()
        self.edit_file.setPlaceholderText("Selecciona un archivo WAV o MP3")
        self.btn_browse = QtWidgets.QPushButton("Examinar")
        self.btn_browse.setProperty("ghost", True)
        top_row.addWidget(self.edit_file, 1)
        top_row.addWidget(self.btn_browse)
        card.body.addLayout(top_row)

        bottom_row = QtWidgets.QHBoxLayout()
        bottom_row.setSpacing(12)

        slot_col = QtWidgets.QVBoxLayout()
        slot_lbl = QtWidgets.QLabel("Slot destino")
        slot_lbl.setProperty("muted", True)
        self.spin_upload_slot = QtWidgets.QSpinBox()
        self.spin_upload_slot.setRange(1, 4)
        self.spin_upload_slot.setValue(4)
        slot_col.addWidget(slot_lbl)
        slot_col.addWidget(self.spin_upload_slot)
        bottom_row.addLayout(slot_col)

        self.chk_encrypt = QtWidgets.QCheckBox("Forzar cifrado")
        bottom_row.addWidget(self.chk_encrypt)
        bottom_row.addStretch(1)

        self.btn_upload = QtWidgets.QPushButton("Subir audio")
        self.btn_upload.setProperty("primary", True)
        bottom_row.addWidget(self.btn_upload)
        card.body.addLayout(bottom_row)

        root.addWidget(card)

        self.btn_browse.clicked.connect(self._choose_audio_file)
        self.btn_upload.clicked.connect(self._emit_upload_audio)
        self.edit_file.textChanged.connect(self._update_upload_enabled)

    # ------------------------------------------------------------------
    def set_slots(self, slots: Sequence[Mapping[str, object] | Sequence[object]]) -> None:
        """Fill the slots table with backend data."""
        total_cols = len(self._TABLE_COLUMNS)
        for row in range(self.tbl_slots.rowCount()):
            data: list[str] = [""] * total_cols
            if row < len(slots):
                entry = slots[row]
                if isinstance(entry, Mapping):
                    data = [self._format_cell(entry.get(key)) for key in self._TABLE_COLUMNS]
                else:
                    seq = list(entry)
                    seq = (seq + [""] * total_cols)[:total_cols]
                    data = [self._format_cell(value) for value in seq]
            data[0] = data[0] or str(row + 1)
            for col, value in enumerate(data):
                item = self.tbl_slots.item(row, col)
                if item is None:
                    item = QtWidgets.QTableWidgetItem()
                    self.tbl_slots.setItem(row, col, item)
                item.setText(value)

    def set_upload_path(self, path: str) -> None:
        self.edit_file.setText(path)

    def selected_slot(self) -> int | None:
        rows = self.tbl_slots.selectionModel().selectedRows()
        if not rows:
            return None
        return rows[0].row() + 1

    def clear_selection(self) -> None:
        self.tbl_slots.clearSelection()

    # ------------------------------------------------------------------
    def _format_cell(self, value: object) -> str:
        if isinstance(value, bool):
            return "Si" if value else "No"
        if value is None:
            return ""
        return str(value)

    def _sync_slot_from_selection(self) -> None:
        slot = self.selected_slot()
        if slot is not None:
            self.spin_slot.setValue(slot)
            self.spin_upload_slot.setValue(slot)

    def _emit_control_slot(self) -> None:
        slot = self.spin_slot.value()
        action = self.combo_action.currentData()
        duration = self.spin_duration.value()
        loop = self.chk_loop.isChecked()
        if isinstance(action, str):
            self.sig_control_slot.emit(slot, action, duration, loop)

    def _choose_audio_file(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Seleccionar audio",
            "",
            "Audio Files (*.wav *.mp3 *.ogg);;Todos (*.*)",
        )
        if path:
            self.set_upload_path(path)

    def _emit_upload_audio(self) -> None:
        path = self.edit_file.text().strip()
        if not path:
            self.edit_file.setFocus()
            return
        slot = self.spin_upload_slot.value()
        encrypt = self.chk_encrypt.isChecked()
        self.sig_upload_audio.emit(slot, path, encrypt)

    def _update_upload_enabled(self) -> None:
        has_path = bool(self.edit_file.text().strip())
        self.btn_upload.setEnabled(has_path)


__all__ = ["PageAudio"]