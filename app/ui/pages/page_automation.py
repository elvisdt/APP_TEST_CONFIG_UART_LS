from __future__ import annotations
from typing import cast, List, Dict, Any
from PyQt6 import QtCore, QtWidgets
from app.ui.widgets.card import Card


class PageAutomation(QtWidgets.QWidget):
    """
    Configura salidas (Duración, Modo, Auto-restaurar)
    y disparadores automáticos (RF1..RF4, Llamada).

    - No hay "Función"
    - No hay "Schedule"
    - Distribución horizontal por porcentajes y responsive
    """

    # Señales hacia backend/controlador
    sig_apply_outputs = QtCore.pyqtSignal(list)          # list[dict]: configuración de salidas
    sig_apply_triggers = QtCore.pyqtSignal(list)         # list[dict]: configuración de disparadores
    sig_import_export = QtCore.pyqtSignal(str, object)   # ("import"|"export", payload)
    sig_trigger_output = QtCore.pyqtSignal(str, str)     # (name, "Activar"|"Liberar")

    _OUTPUT_NAMES: List[str] = ["ZN1", "SIR", "OUT1", "OUT2"]
    _OUTPUT_MODES: List[str] = ["Pulso", "Sostenido", "Seguimiento de evento"]
    _TRIGGER_COLUMNS: List[str] = ["RF1", "RF2", "RF3", "RF4", "Llamada"]

    # Índices de columnas (salidas)
    COL_NAME = 0
    COL_DUR = 1
    COL_MODE = 2
    COL_AUTORST = 3

    def __init__(self) -> None:
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        self._dirty = False
        self._output_rows: List[Dict[str, QtWidgets.QWidget]] = []
        self._trigger_rows: List[Dict[str, QtWidgets.QWidget]] = []

        # Tarjetas
        self._build_outputs_card(root)
        self._build_triggers_card(root)
        self._build_toolbar(root)

        # Defaults
        self.reset_outputs()
        self.reset_triggers()

        # Event filters para recalcular anchos al redimensionar
        self.tbl_outputs.viewport().installEventFilter(self)
        self.tbl_triggers.viewport().installEventFilter(self)
        self._autosize_outputs_columns()
        self._autosize_triggers_columns()

    # ──────────────────────────────────────────────────────────────
    #  Card: Salidas / Actuadores
    # ──────────────────────────────────────────────────────────────
    def _build_outputs_card(self, root: QtWidgets.QVBoxLayout) -> None:
        card = Card("Salidas / Actuadores")

        # 4 columnas: Salida | Duración | Modo | Auto-restaurar
        self.tbl_outputs = QtWidgets.QTableWidget(len(self._OUTPUT_NAMES), 4)
        self.tbl_outputs.setHorizontalHeaderLabels(["Salida", "Duración (s)", "Modo", "Auto-restaurar"])
        self.tbl_outputs.verticalHeader().setVisible(False)
        self.tbl_outputs.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_outputs.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.tbl_outputs.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.tbl_outputs.setWordWrap(False)
        self.tbl_outputs.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)

        header = self.tbl_outputs.horizontalHeader()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(80)
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)  # control manual

        for row, name in enumerate(self._OUTPUT_NAMES):
            # Columna: Nombre
            item = QtWidgets.QTableWidgetItem(name)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled)
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
            self.tbl_outputs.setItem(row, self.COL_NAME, item)

            # Columna: Duración (centrada)
            duration = QtWidgets.QSpinBox()
            duration.setRange(1, 900)
            duration.setValue(30)
            duration.setSuffix(" s")
            duration.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self._place_centered_widget(self.tbl_outputs, row, self.COL_DUR, duration)

            # Columna: Modo (centrado)
            mode = QtWidgets.QComboBox()
            mode.addItems(self._OUTPUT_MODES)
            self._place_centered_widget(self.tbl_outputs, row, self.COL_MODE, mode)

            # Columna: Auto-restaurar (checkbox centrado)
            auto_reset = QtWidgets.QCheckBox()
            auto_reset.setChecked(True)
            self._place_centered_widget(self.tbl_outputs, row, self.COL_AUTORST, auto_reset)

            # Guardar referencias + lógica
            self._output_rows.append({"duration": duration, "mode": mode, "auto_reset": auto_reset})
            mode.currentIndexChanged.connect(lambda _=None, r=row: self._on_mode_changed(r))
            duration.valueChanged.connect(self._mark_dirty)
            auto_reset.stateChanged.connect(self._mark_dirty)
            self.tbl_outputs.setRowHeight(row, 36)

        # Controles de prueba rápida
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
        self.btn_test_output.clicked.connect(self._emit_test_output)
        controls.addStretch(1)
        controls.addWidget(lbl_test)
        controls.addWidget(self.combo_test_output)
        controls.addWidget(self.combo_test_mode)
        controls.addWidget(self.btn_test_output)

        # Botones aplicar / reset
        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        self.btn_outputs_reset = QtWidgets.QPushButton("Restaurar predeterminado")
        self.btn_outputs_reset.setProperty("ghost", True)
        self.btn_outputs_apply = QtWidgets.QPushButton("Aplicar salidas")
        self.btn_outputs_apply.setProperty("primary", True)
        self.btn_outputs_reset.clicked.connect(self.reset_outputs)
        self.btn_outputs_apply.clicked.connect(lambda: self.sig_apply_outputs.emit(self.outputs()))
        buttons.addWidget(self.btn_outputs_reset)
        buttons.addWidget(self.btn_outputs_apply)

        card.body.addWidget(self.tbl_outputs)
        card.body.addLayout(controls)
        card.body.addLayout(buttons)
        root.addWidget(card)

    # ──────────────────────────────────────────────────────────────
    #  Card: Disparadores automáticos
    # ──────────────────────────────────────────────────────────────
    def _build_triggers_card(self, root: QtWidgets.QVBoxLayout) -> None:
        card = Card("Disparadores automáticos")

        # Columnas: Salida | RF1 | RF2 | RF3 | RF4 | Llamada
        cols = 1 + len(self._TRIGGER_COLUMNS)
        self.tbl_triggers = QtWidgets.QTableWidget(len(self._OUTPUT_NAMES), cols)
        self.tbl_triggers.setHorizontalHeaderLabels(["Salida"] + self._TRIGGER_COLUMNS)
        self.tbl_triggers.verticalHeader().setVisible(False)
        self.tbl_triggers.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tbl_triggers.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.tbl_triggers.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.tbl_triggers.setWordWrap(False)

        header = self.tbl_triggers.horizontalHeader()
        header.setStretchLastSection(False)
        header.setMinimumSectionSize(70)
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)

        for row, name in enumerate(self._OUTPUT_NAMES):
            # Nombre
            item = QtWidgets.QTableWidgetItem(name)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled)
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
            self.tbl_triggers.setItem(row, 0, item)

            # Checkboxes RF/Llamada (centrados)
            row_widgets: Dict[str, QtWidgets.QWidget] = {}
            for col, tname in enumerate(self._TRIGGER_COLUMNS, start=1):
                cb = QtWidgets.QCheckBox()
                self._place_centered_widget(self.tbl_triggers, row, col, cb)
                cb.stateChanged.connect(self._mark_dirty)
                row_widgets[tname] = cb
            self.tbl_triggers.setRowHeight(row, 32)
            self._trigger_rows.append(row_widgets)

        # Botones aplicar / reset
        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        self.btn_triggers_reset = QtWidgets.QPushButton("Desactivar todos")
        self.btn_triggers_reset.setProperty("ghost", True)
        self.btn_triggers_apply = QtWidgets.QPushButton("Aplicar disparadores")
        self.btn_triggers_apply.setProperty("primary", True)
        self.btn_triggers_reset.clicked.connect(self.reset_triggers)
        self.btn_triggers_apply.clicked.connect(lambda: self.sig_apply_triggers.emit(self.triggers()))
        buttons.addWidget(self.btn_triggers_reset)
        buttons.addWidget(self.btn_triggers_apply)

        card.body.addWidget(self.tbl_triggers)
        card.body.addLayout(buttons)
        root.addWidget(card)

    # ──────────────────────────────────────────────────────────────
    #  Barra inferior: Importar/Exportar / Estado
    # ──────────────────────────────────────────────────────────────
    def _build_toolbar(self, root: QtWidgets.QVBoxLayout) -> None:
        
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(2)

        self.lbl_dirty = QtWidgets.QLabel("")  # “Cambios sin aplicar…”
        self.lbl_dirty.setProperty("muted", True)

        btn_export = QtWidgets.QPushButton("Exportar JSON")
        btn_import = QtWidgets.QPushButton("Importar JSON")
        btn_export.clicked.connect(lambda: self.sig_import_export.emit("export", {"outputs": self.outputs(), "triggers": self.triggers()}))
        btn_import.clicked.connect(lambda: self.sig_import_export.emit("import", None))

        row.addWidget(self.lbl_dirty)
        row.addStretch(1)
        row.addWidget(btn_import)
        row.addWidget(btn_export)
        root.addLayout(row)

    # ──────────────────────────────────────────────────────────────
    #  Helpers de distribución / centrado
    # ──────────────────────────────────────────────────────────────
    def _place_centered_widget(self, table: QtWidgets.QTableWidget, row: int, col: int, w: QtWidgets.QWidget) -> None:
        """Centra un widget dentro de la celda usando un contenedor."""
        container = QtWidgets.QWidget()
        lay = QtWidgets.QHBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        lay.addStretch(1)
        lay.addWidget(w)
        lay.addStretch(1)
        table.setCellWidget(row, col, container)

    def eventFilter(self, obj: QtCore.QObject, ev: QtCore.QEvent) -> bool:
        """Recalcula anchos cuando se redimensiona el viewport."""
        if obj is self.tbl_outputs.viewport() and ev.type() == QtCore.QEvent.Type.Resize:
            self._autosize_outputs_columns()
        elif obj is self.tbl_triggers.viewport() and ev.type() == QtCore.QEvent.Type.Resize:
            self._autosize_triggers_columns()
        return super().eventFilter(obj, ev)

    def _autosize_outputs_columns(self) -> None:
        """Salida 18% | Duración 16% | Modo 46% | Auto 20% (con mínimos)."""
        total = self.tbl_outputs.viewport().width()
        widths = [
            int(total * 0.18),  # Salida
            int(total * 0.16),  # Duración
            int(total * 0.46),  # Modo
            max(90, int(total * 0.20)),  # Auto-restaurar
        ]
        # mínimos para legibilidad
        widths[0] = max(widths[0], 110)
        widths[1] = max(widths[1], 120)
        widths[2] = max(widths[2], 220)
        for i, w in enumerate(widths):
            self.tbl_outputs.setColumnWidth(i, w)

    def _autosize_triggers_columns(self) -> None:
        """Salida 22% | RF1..RF4 12% c/u | Llamada 30% (con mínimos)."""
        total = self.tbl_triggers.viewport().width()
        base = [
            int(total * 0.20),  # Salida
            int(total * 0.15),  # RF1
            int(total * 0.15),  # RF2
            int(total * 0.15),  # RF3
            int(total * 0.15),  # RF4
            int(total * 0.20),  # Llamada
        ]
        mins = [120, 80, 80, 80, 80, 120]
        for i, w in enumerate(base):
            self.tbl_triggers.setColumnWidth(i, max(w, mins[i]))

    # ──────────────────────────────────────────────────────────────
    #  Lógica de UI
    # ──────────────────────────────────────────────────────────────
    def _on_mode_changed(self, row: int) -> None:
        """Habilita/deshabilita controles según el Modo."""
        widgets = self._output_rows[row]
        mode = cast(QtWidgets.QComboBox, widgets["mode"]).currentText()
        duration = cast(QtWidgets.QSpinBox, widgets["duration"])
        auto_reset = cast(QtWidgets.QCheckBox, widgets["auto_reset"])

        if mode == "Pulso":
            duration.setEnabled(True)
            auto_reset.setEnabled(False)
            auto_reset.setChecked(True)   # irrelevante en pulso
            auto_reset.setToolTip("No aplica en Pulso.")
        elif mode == "Sostenido":
            duration.setEnabled(False)
            auto_reset.setEnabled(True)
            auto_reset.setToolTip("Si está activo, el sistema puede revertir a OFF automáticamente.")
        else:  # Seguimiento de evento
            duration.setEnabled(False)
            auto_reset.setEnabled(False)
            auto_reset.setChecked(True)
            auto_reset.setToolTip("No aplica en Seguimiento de evento.")

        self._mark_dirty()

    def _mark_dirty(self, *_args) -> None:
        self._dirty = True
        self.lbl_dirty.setText("Cambios sin aplicar…")

    def _clear_dirty(self) -> None:
        self._dirty = False
        self.lbl_dirty.setText("")

    def _emit_test_output(self) -> None:
        name = self.combo_test_output.currentText()
        action = self.combo_test_mode.currentText()
        if name:
            self.sig_trigger_output.emit(name, action)

    # ──────────────────────────────────────────────────────────────
    #  Serialización
    # ──────────────────────────────────────────────────────────────
    def outputs(self) -> List[Dict[str, Any]]:
        data: List[Dict[str, Any]] = []
        for name, widgets in zip(self._OUTPUT_NAMES, self._output_rows):
            duration = cast(QtWidgets.QSpinBox, widgets["duration"])
            mode = cast(QtWidgets.QComboBox, widgets["mode"])
            auto_reset = cast(QtWidgets.QCheckBox, widgets["auto_reset"])
            data.append({
                "name": name,
                "duration": duration.value(),
                "mode": mode.currentText(),
                "auto_reset": auto_reset.isChecked(),
            })
        self._clear_dirty()
        return data

    def set_outputs(self, entries: List[Dict[str, Any]]) -> None:
        mapping = {str(item.get("name")): item for item in entries if isinstance(item, dict)}
        for r, (name, widgets) in enumerate(zip(self._OUTPUT_NAMES, self._output_rows)):
            payload = mapping.get(name, {})
            duration = cast(QtWidgets.QSpinBox, widgets["duration"])
            mode = cast(QtWidgets.QComboBox, widgets["mode"])
            auto_reset = cast(QtWidgets.QCheckBox, widgets["auto_reset"])

            duration.setValue(int(payload.get("duration", 30)))
            mode_val = str(payload.get("mode", self._OUTPUT_MODES[0]))
            idx_mode = mode.findText(mode_val)
            mode.setCurrentIndex(idx_mode if idx_mode >= 0 else 0)
            auto_reset.setChecked(bool(payload.get("auto_reset", True)))

            self._on_mode_changed(r)

        self._clear_dirty()

    def reset_outputs(self) -> None:
        defaults = []
        for name in self._OUTPUT_NAMES:
            defaults.append({
                "name": name,
                "duration": 30,
                "mode": self._OUTPUT_MODES[0],  # Pulso
                "auto_reset": True,
            })
        self.set_outputs(defaults)

    # ──────────────────────────────────────────────────────────────
    #  Triggers
    # ──────────────────────────────────────────────────────────────
    def triggers(self) -> List[Dict[str, Any]]:
        data: List[Dict[str, Any]] = []
        for row, name in enumerate(self._OUTPUT_NAMES):
            widgets = self._trigger_rows[row]
            entry = {"name": name, "triggers": {}}
            for tname in self._TRIGGER_COLUMNS:
                cb = cast(QtWidgets.QCheckBox, widgets[tname])
                entry["triggers"][tname] = cb.isChecked()
            data.append(entry)
        self._clear_dirty()
        return data

    def set_triggers(self, entries: List[Dict[str, Any]]) -> None:
        mapping = {str(item.get("name")): item for item in entries if isinstance(item, dict)}
        for row, name in enumerate(self._OUTPUT_NAMES):
            payload = mapping.get(name, {})
            widgets = self._trigger_rows[row]
            trigs = payload.get("triggers", {}) if isinstance(payload.get("triggers"), dict) else {}
            for tname in self._TRIGGER_COLUMNS:
                cb = cast(QtWidgets.QCheckBox, widgets[tname])
                cb.setChecked(bool(trigs.get(tname, False)))
        self._clear_dirty()

    def reset_triggers(self) -> None:
        defaults = []
        for name in self._OUTPUT_NAMES:
            defaults.append({
                "name": name,
                "triggers": {"RF1": False, "RF2": False, "RF3": False, "RF4": False, "Llamada": False}
            })
        self.set_triggers(defaults)


__all__ = ["PageAutomation"]
