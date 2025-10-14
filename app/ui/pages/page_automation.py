from __future__ import annotations

from typing import cast

from PyQt6 import QtCore, QtWidgets

from app.ui.widgets.card import Card


class PageAutomation(QtWidgets.QWidget):
    """Configura entradas, salidas y ventanas horarias del equipo."""

    sig_apply_inputs = QtCore.pyqtSignal(list)
    sig_apply_outputs = QtCore.pyqtSignal(list)
    sig_apply_schedules = QtCore.pyqtSignal(list)
    sig_trigger_output = QtCore.pyqtSignal(str, str)

    _INPUT_NAMES = ["IN1", "IN2", "IN3", "IN4", "IN5", "IN6"]
    _OUTPUT_NAMES = ["OUT1", "OUT2", "OUT3", "OUT4"]

    _INPUT_FUNCTIONS = [
        "Armado/Desarmado",
        "Panico",
        "Intrusion",
        "Bajo voltaje",
        "Tamper",
        "Entrada libre",
    ]

    _OUTPUT_FUNCTIONS = [
        "Sirena",
        "Estrobo",
        "Mensaje de voz",
        "Rele auxiliar",
        "Reporte MQTT",
    ]

    _OUTPUT_MODES = [
        "Pulso",
        "Sostenido",
        "Seguimiento de evento",
    ]

    _SCHEDULE_DAY_OPTIONS = [
        "Siempre",
        "Lunes a viernes",
        "Sabados",
        "Domingos",
        "Personalizado",
    ]

    def __init__(self) -> None:
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        self._input_rows: list[dict[str, QtWidgets.QWidget]] = []
        self._output_rows: list[dict[str, QtWidgets.QWidget]] = []

        self._build_inputs_card(root)
        self._build_outputs_card(root)
        self._build_schedules_card(root)

        self.reset_inputs()
        self.reset_outputs()
        self.reset_schedules()

    # ------------------------------------------------------------------
    def _build_inputs_card(self, root: QtWidgets.QVBoxLayout) -> None:
        card = Card("Entradas digitales")

        self.tbl_inputs = QtWidgets.QTableWidget(len(self._INPUT_NAMES), 5)
        self.tbl_inputs.setHorizontalHeaderLabels([
            "Entrada",
            "Funcion",
            "Zona",
            "Retardo (s)",
            "Habilitada",
        ])
        self.tbl_inputs.verticalHeader().setVisible(False)
        self.tbl_inputs.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_inputs.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.tbl_inputs.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        header = self.tbl_inputs.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        for row, name in enumerate(self._INPUT_NAMES):
            item = QtWidgets.QTableWidgetItem(name)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tbl_inputs.setItem(row, 0, item)

            combo = QtWidgets.QComboBox()
            combo.addItems(self._INPUT_FUNCTIONS)

            zone = QtWidgets.QLineEdit()
            zone.setPlaceholderText("Zona / etiqueta")

            delay = QtWidgets.QSpinBox()
            delay.setRange(0, 600)
            delay.setSingleStep(5)
            delay.setValue(0)

            enabled = QtWidgets.QCheckBox()
            enabled.setChecked(True)
            enabled.setTristate(False)
            enabled.setStyleSheet("margin-left:12px;")

            self.tbl_inputs.setCellWidget(row, 1, combo)
            self.tbl_inputs.setCellWidget(row, 2, zone)
            self.tbl_inputs.setCellWidget(row, 3, delay)
            self.tbl_inputs.setCellWidget(row, 4, enabled)

            self._input_rows.append({
                "function": combo,
                "zone": zone,
                "delay": delay,
                "enabled": enabled,
            })

            self.tbl_inputs.setRowHeight(row, 36)

        card.body.addWidget(self.tbl_inputs)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        self.btn_inputs_reset = QtWidgets.QPushButton("Restaurar predeterminado")
        self.btn_inputs_reset.setProperty("ghost", True)
        self.btn_inputs_apply = QtWidgets.QPushButton("Aplicar entradas")
        self.btn_inputs_apply.setProperty("primary", True)
        buttons.addWidget(self.btn_inputs_reset)
        buttons.addWidget(self.btn_inputs_apply)
        card.body.addLayout(buttons)

        root.addWidget(card)

        self.btn_inputs_reset.clicked.connect(self.reset_inputs)
        self.btn_inputs_apply.clicked.connect(lambda: self.sig_apply_inputs.emit(self.inputs()))

    def _build_outputs_card(self, root: QtWidgets.QVBoxLayout) -> None:
        card = Card("Salidas / Actuadores")

        self.tbl_outputs = QtWidgets.QTableWidget(len(self._OUTPUT_NAMES), 5)
        self.tbl_outputs.setHorizontalHeaderLabels([
            "Salida",
            "Funcion",
            "Duracion (s)",
            "Modo",
            "Auto-restaurar",
        ])
        self.tbl_outputs.verticalHeader().setVisible(False)
        self.tbl_outputs.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_outputs.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.tbl_outputs.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)

        header = self.tbl_outputs.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        for row, name in enumerate(self._OUTPUT_NAMES):
            item = QtWidgets.QTableWidgetItem(name)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled)
            self.tbl_outputs.setItem(row, 0, item)

            combo_fn = QtWidgets.QComboBox()
            combo_fn.addItems(self._OUTPUT_FUNCTIONS)

            duration = QtWidgets.QSpinBox()
            duration.setRange(1, 900)
            duration.setValue(30)
            duration.setSuffix(" s")

            mode = QtWidgets.QComboBox()
            mode.addItems(self._OUTPUT_MODES)

            auto_reset = QtWidgets.QCheckBox()
            auto_reset.setChecked(True)
            auto_reset.setStyleSheet("margin-left:12px;")

            self.tbl_outputs.setCellWidget(row, 1, combo_fn)
            self.tbl_outputs.setCellWidget(row, 2, duration)
            self.tbl_outputs.setCellWidget(row, 3, mode)
            self.tbl_outputs.setCellWidget(row, 4, auto_reset)

            self._output_rows.append({
                "function": combo_fn,
                "duration": duration,
                "mode": mode,
                "auto_reset": auto_reset,
            })

            self.tbl_outputs.setRowHeight(row, 36)

        card.body.addWidget(self.tbl_outputs)

        controls = QtWidgets.QHBoxLayout()
        controls.setSpacing(8)
        lbl_test = QtWidgets.QLabel("Probar salida")
        lbl_test.setProperty("muted", True)
        self.combo_test_output = QtWidgets.QComboBox()
        self.combo_test_output.addItems(self._OUTPUT_NAMES)
        self.combo_test_mode = QtWidgets.QComboBox()
        self.combo_test_mode.addItems(["Activar", "Liberar"])
        self.btn_test_output = QtWidgets.QPushButton("Ejecutar prueba")
        self.btn_test_output.setProperty("ghost", True)
        controls.addStretch(1)
        controls.addWidget(lbl_test)
        controls.addWidget(self.combo_test_output)
        controls.addWidget(self.combo_test_mode)
        controls.addWidget(self.btn_test_output)
        card.body.addLayout(controls)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        self.btn_outputs_reset = QtWidgets.QPushButton("Restaurar predeterminado")
        self.btn_outputs_reset.setProperty("ghost", True)
        self.btn_outputs_apply = QtWidgets.QPushButton("Aplicar salidas")
        self.btn_outputs_apply.setProperty("primary", True)
        buttons.addWidget(self.btn_outputs_reset)
        buttons.addWidget(self.btn_outputs_apply)
        card.body.addLayout(buttons)

        root.addWidget(card)

        self.btn_outputs_reset.clicked.connect(self.reset_outputs)
        self.btn_outputs_apply.clicked.connect(lambda: self.sig_apply_outputs.emit(self.outputs()))
        self.btn_test_output.clicked.connect(self._emit_test_output)

    def _build_schedules_card(self, root: QtWidgets.QVBoxLayout) -> None:
        card = Card("Temporizadores y zonas horarias")

        self.tbl_schedules = QtWidgets.QTableWidget(0, 4)
        self.tbl_schedules.setHorizontalHeaderLabels([
            "Nombre",
            "Dias",
            "Inicio",
            "Fin",
        ])
        self.tbl_schedules.verticalHeader().setVisible(False)
        self.tbl_schedules.horizontalHeader().setStretchLastSection(True)
        self.tbl_schedules.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.tbl_schedules.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_schedules.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_schedules.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.tbl_schedules.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.tbl_schedules.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self.tbl_schedules.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)
        card.body.addWidget(self.tbl_schedules)

        toolbar = QtWidgets.QHBoxLayout()
        self.btn_schedule_add = QtWidgets.QPushButton("Agregar ventana")
        self.btn_schedule_add.setProperty("ghost", True)
        self.btn_schedule_remove = QtWidgets.QPushButton("Eliminar seleccion")
        self.btn_schedule_remove.setProperty("ghost", True)
        toolbar.addWidget(self.btn_schedule_add)
        toolbar.addWidget(self.btn_schedule_remove)
        toolbar.addStretch(1)
        card.body.addLayout(toolbar)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        self.btn_schedule_apply = QtWidgets.QPushButton("Aplicar horarios")
        self.btn_schedule_apply.setProperty("primary", True)
        buttons.addWidget(self.btn_schedule_apply)
        card.body.addLayout(buttons)

        root.addWidget(card)

        self.btn_schedule_add.clicked.connect(self._add_schedule_row)
        self.btn_schedule_remove.clicked.connect(self._remove_selected_schedule)
        self.btn_schedule_apply.clicked.connect(lambda: self.sig_apply_schedules.emit(self.schedules()))

    # ------------------------------------------------------------------
    def inputs(self) -> list[dict[str, object]]:
        data: list[dict[str, object]] = []
        for name, widgets in zip(self._INPUT_NAMES, self._input_rows):
            combo = cast(QtWidgets.QComboBox, widgets["function"])
            zone = cast(QtWidgets.QLineEdit, widgets["zone"])
            delay = cast(QtWidgets.QSpinBox, widgets["delay"])
            enabled = cast(QtWidgets.QCheckBox, widgets["enabled"])

            data.append({
                "name": name,
                "function": combo.currentText(),
                "zone": zone.text().strip(),
                "delay": delay.value(),
                "enabled": enabled.isChecked(),
            })
        return data

    def set_inputs(self, entries: list[dict[str, object]]) -> None:
        mapping = {item.get("name"): item for item in entries if isinstance(item, dict)}
        for name, widgets in zip(self._INPUT_NAMES, self._input_rows):
            payload = mapping.get(name, {})
            combo = cast(QtWidgets.QComboBox, widgets["function"])
            zone = cast(QtWidgets.QLineEdit, widgets["zone"])
            delay = cast(QtWidgets.QSpinBox, widgets["delay"])
            enabled = cast(QtWidgets.QCheckBox, widgets["enabled"])

            function = str(payload.get("function", self._INPUT_FUNCTIONS[0]))
            index = combo.findText(function)
            combo.setCurrentIndex(index if index >= 0 else 0)
            zone.setText(str(payload.get("zone", "")))
            delay.setValue(int(payload.get("delay", 0)))
            enabled.setChecked(bool(payload.get("enabled", True)))

    def reset_inputs(self) -> None:
        defaults = [
            {"name": name, "function": self._INPUT_FUNCTIONS[min(idx, len(self._INPUT_FUNCTIONS) - 1)]}
            for idx, name in enumerate(self._INPUT_NAMES)
        ]
        self.set_inputs(defaults)

    def outputs(self) -> list[dict[str, object]]:
        data: list[dict[str, object]] = []
        for name, widgets in zip(self._OUTPUT_NAMES, self._output_rows):
            combo_fn = cast(QtWidgets.QComboBox, widgets["function"])
            duration = cast(QtWidgets.QSpinBox, widgets["duration"])
            mode = cast(QtWidgets.QComboBox, widgets["mode"])
            auto_reset = cast(QtWidgets.QCheckBox, widgets["auto_reset"])

            data.append({
                "name": name,
                "function": combo_fn.currentText(),
                "duration": duration.value(),
                "mode": mode.currentText(),
                "auto_reset": auto_reset.isChecked(),
            })
        return data

    def set_outputs(self, entries: list[dict[str, object]]) -> None:
        mapping = {item.get("name"): item for item in entries if isinstance(item, dict)}
        for name, widgets in zip(self._OUTPUT_NAMES, self._output_rows):
            payload = mapping.get(name, {})
            combo_fn = cast(QtWidgets.QComboBox, widgets["function"])
            duration = cast(QtWidgets.QSpinBox, widgets["duration"])
            mode = cast(QtWidgets.QComboBox, widgets["mode"])
            auto_reset = cast(QtWidgets.QCheckBox, widgets["auto_reset"])

            function = str(payload.get("function", self._OUTPUT_FUNCTIONS[0]))
            idx_fn = combo_fn.findText(function)
            combo_fn.setCurrentIndex(idx_fn if idx_fn >= 0 else 0)
            duration.setValue(int(payload.get("duration", 30)))
            mode_val = str(payload.get("mode", self._OUTPUT_MODES[0]))
            idx_mode = mode.findText(mode_val)
            mode.setCurrentIndex(idx_mode if idx_mode >= 0 else 0)
            auto_reset.setChecked(bool(payload.get("auto_reset", True)))

    def reset_outputs(self) -> None:
        defaults = [
            {
                "name": name,
                "function": self._OUTPUT_FUNCTIONS[min(idx, len(self._OUTPUT_FUNCTIONS) - 1)],
                "duration": 30,
            }
            for idx, name in enumerate(self._OUTPUT_NAMES)
        ]
        self.set_outputs(defaults)

    def schedules(self) -> list[dict[str, object]]:
        results: list[dict[str, object]] = []
        for row in range(self.tbl_schedules.rowCount()):
            name_item = self.tbl_schedules.item(row, 0)
            day_widget = self.tbl_schedules.cellWidget(row, 1)
            start_widget = self.tbl_schedules.cellWidget(row, 2)
            end_widget = self.tbl_schedules.cellWidget(row, 3)

            name = name_item.text().strip() if name_item else f"Horario {row + 1}"
            days = day_widget.currentText() if isinstance(day_widget, QtWidgets.QComboBox) else ""
            start = start_widget.time().toString("HH:mm") if isinstance(start_widget, QtWidgets.QTimeEdit) else "00:00"
            end = end_widget.time().toString("HH:mm") if isinstance(end_widget, QtWidgets.QTimeEdit) else "23:59"

            results.append({
                "name": name,
                "days": days,
                "start": start,
                "end": end,
            })
        return results

    def set_schedules(self, items: list[dict[str, object]]) -> None:
        self.tbl_schedules.setRowCount(0)
        for entry in items:
            self._add_schedule_row(entry)

    def reset_schedules(self) -> None:
        defaults = [
            {"name": "Horario diurno", "days": "Lunes a viernes", "start": "06:00", "end": "22:00"},
            {"name": "Horario nocturno", "days": "Siempre", "start": "22:00", "end": "06:00"},
        ]
        self.set_schedules(defaults)

    # ------------------------------------------------------------------
    def _emit_test_output(self) -> None:
        name = self.combo_test_output.currentText()
        action = self.combo_test_mode.currentText()
        if name:
            self.sig_trigger_output.emit(name, action)

    def _add_schedule_row(self, preset: dict[str, object] | None = None) -> None:
        row = self.tbl_schedules.rowCount()
        self.tbl_schedules.insertRow(row)

        name = str((preset or {}).get("name", f"Horario {row + 1}"))
        days = str((preset or {}).get("days", self._SCHEDULE_DAY_OPTIONS[0]))
        start = str((preset or {}).get("start", "00:00"))
        end = str((preset or {}).get("end", "23:59"))

        name_item = QtWidgets.QTableWidgetItem(name)
        self.tbl_schedules.setItem(row, 0, name_item)

        days_combo = QtWidgets.QComboBox()
        days_combo.addItems(self._SCHEDULE_DAY_OPTIONS)
        idx_days = days_combo.findText(days)
        days_combo.setCurrentIndex(idx_days if idx_days >= 0 else 0)
        self.tbl_schedules.setCellWidget(row, 1, days_combo)

        start_time = QtWidgets.QTimeEdit()
        start_time.setDisplayFormat("HH:mm")
        start_time.setTime(QtCore.QTime.fromString(start, "HH:mm"))
        self.tbl_schedules.setCellWidget(row, 2, start_time)

        end_time = QtWidgets.QTimeEdit()
        end_time.setDisplayFormat("HH:mm")
        end_time.setTime(QtCore.QTime.fromString(end, "HH:mm"))
        self.tbl_schedules.setCellWidget(row, 3, end_time)

        self.tbl_schedules.setRowHeight(row, 34)

    def _remove_selected_schedule(self) -> None:
        row = self.tbl_schedules.currentRow()
        if row >= 0:
            self.tbl_schedules.removeRow(row)


__all__ = ["PageAutomation"]
