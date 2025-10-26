from __future__ import annotations
from typing import cast, List, Dict, Any
from PyQt6 import QtCore, QtWidgets
from app.ui.widgets.card import Card
from app.ui.widgets.basics import HLine


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
    sig_show_history = QtCore.pyqtSignal()               # abrir historial local
    sig_run_selftest = QtCore.pyqtSignal()               # ejecutar auto-chequeo hardware

    _OUTPUT_NAMES: List[str] = ["ZN1", "SIR", "OUT1", "OUT2"]
    _OUTPUT_MODES: List[str] = ["Pulso", "Sostenido", "Seguimiento de evento"]
    _TRIGGER_COLUMNS: List[str] = ["RF1", "RF2", "RF3", "RF4", "Llamada"]
    _STATUS_BY_MODE: Dict[str, Dict[str, str]] = {
        "Pulso": {"label": "Temporizado", "bg": "#ca8a04", "fg": "#ffffff"},
        "Sostenido": {"label": "Manual", "bg": "#2563eb", "fg": "#ffffff"},
        "Seguimiento de evento": {"label": "Seguimiento", "bg": "#0f172a", "fg": "#e2e8f0"},
    }
    _REMOTE_LABELS: Dict[str, str] = {
        "RF1": "Sirena",
        "RF2": "Pánico",
        "RF3": "Auxilio",
        "RF4": "Desarme",
    }

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
        self._build_header(root)
        self._build_outputs_card(root)
        self._build_triggers_card(root)
        self._build_toolbar(root)

        # Defaults
        self.reset_outputs()
        self.reset_triggers()


    def _build_header(self, root: QtWidgets.QVBoxLayout) -> None:
        hero = Card()
        hero.setProperty("pageHero", True)
        hero.body.setSpacing(6)

        title = QtWidgets.QLabel("Automatización inteligente")
        title.setProperty("title3", True)
        hero.body.addWidget(title)

        subtitle = QtWidgets.QLabel(
            "Administra salidas físicas, disparadores inalámbricos y rutinas remotas desde un solo panel."
        )
        subtitle.setWordWrap(True)
        subtitle.setProperty("muted", True)
        hero.body.addWidget(subtitle)

        stats_row = QtWidgets.QHBoxLayout()
        stats_row.setSpacing(14)

        stats = [
            ("Salidas disponibles", len(self._OUTPUT_NAMES)),
            ("Disparadores configurables", len(self._TRIGGER_COLUMNS)),
            ("Modos de operación", len(self._OUTPUT_MODES)),
        ]
        for label, value in stats:
            chip = QtWidgets.QFrame()
            chip.setProperty("statTile", True)
            chip_layout = QtWidgets.QVBoxLayout(chip)
            chip_layout.setContentsMargins(12, 8, 12, 10)
            chip_layout.setSpacing(2)

            value_lbl = QtWidgets.QLabel(str(value))
            value_lbl.setProperty("title3", True)
            chip_layout.addWidget(value_lbl, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)

            label_lbl = QtWidgets.QLabel(label)
            label_lbl.setProperty("muted", True)
            label_lbl.setWordWrap(True)
            chip_layout.addWidget(label_lbl)

            stats_row.addWidget(chip)

        stats_row.addStretch(1)
        hero.body.addLayout(stats_row)

        root.addWidget(hero)


    # --------------------------------------------------------------
    #  Card: Salidas / Actuadores
    # --------------------------------------------------------------
    def _build_outputs_card(self, root: QtWidgets.QVBoxLayout) -> None:
        card = Card("Salidas / Actuadores")

        self._output_rows.clear()
        card.body.setSpacing(16)

        helper = QtWidgets.QLabel("Configura cada actuador con una vista más clara y controles contextuales.")
        helper.setProperty("muted", True)
        helper.setWordWrap(True)
        card.body.addWidget(helper)

        content = QtWidgets.QHBoxLayout()
        content.setSpacing(18)

        grid_container = QtWidgets.QWidget()
        grid_container.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Expanding,
            QtWidgets.QSizePolicy.Policy.Preferred,
        )
        self._outputs_container = QtWidgets.QGridLayout()
        self._outputs_container.setContentsMargins(0, 0, 0, 0)
        self._outputs_container.setHorizontalSpacing(16)
        self._outputs_container.setVerticalSpacing(16)
        for idx, name in enumerate(self._OUTPUT_NAMES):
            row_idx = idx // 2
            col_idx = idx % 2
            card_widget = self._create_output_row(idx, name)
            self._outputs_container.addWidget(card_widget, row_idx, col_idx)
        self._outputs_container.setColumnStretch(0, 1)
        self._outputs_container.setColumnStretch(1, 1)
        grid_container.setLayout(self._outputs_container)
        content.addWidget(grid_container, 1)

        side_panel = QtWidgets.QFrame()
        side_panel.setProperty("sidePanel", True)
        side_panel.setMaximumWidth(280)
        side_layout = QtWidgets.QVBoxLayout(side_panel)
        side_layout.setContentsMargins(16, 16, 16, 16)
        side_layout.setSpacing(12)

        side_title = QtWidgets.QLabel("Acciones rápidas")
        side_title.setProperty("title3", True)
        side_layout.addWidget(side_title)

        side_caption = QtWidgets.QLabel("Prueba salidas en caliente o sincroniza ajustes con el controlador.")
        side_caption.setWordWrap(True)
        side_caption.setProperty("muted", True)
        side_layout.addWidget(side_caption)

        form = QtWidgets.QFormLayout()
        form.setSpacing(6)
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.combo_test_output = QtWidgets.QComboBox()
        self.combo_test_output.setToolTip("Elige una salida para probar en caliente.")
        self.combo_test_output.addItems(self._OUTPUT_NAMES)
        self.combo_test_output.setMinimumWidth(140)
        form.addRow("Salida", self.combo_test_output)

        self.combo_test_mode = QtWidgets.QComboBox()
        self.combo_test_mode.setToolTip("Selecciona si deseas activar o liberar la salida.")
        self.combo_test_mode.addItems(["Activar", "Liberar"])
        form.addRow("Acción", self.combo_test_mode)

        side_layout.addLayout(form)

        self.btn_test_output = QtWidgets.QPushButton("Lanzar prueba")
        self.btn_test_output.setProperty("primary", True)
        self.btn_test_output.setToolTip("Dispara la acción inmediata sobre el actuador seleccionado.")
        self.btn_test_output.clicked.connect(self._emit_test_output)
        side_layout.addWidget(self.btn_test_output)

        side_layout.addWidget(HLine())

        sync_caption = QtWidgets.QLabel("Sincronizar ajustes")
        sync_caption.setProperty("muted", True)
        side_layout.addWidget(sync_caption)

        self.btn_outputs_apply = QtWidgets.QPushButton("Aplicar salidas")
        self.btn_outputs_apply.setProperty("primary", True)
        self.btn_outputs_apply.clicked.connect(lambda: self.sig_apply_outputs.emit(self.outputs()))

        self.btn_outputs_reset = QtWidgets.QPushButton("Restaurar predeterminado")
        self.btn_outputs_reset.setProperty("ghost", True)
        self.btn_outputs_reset.clicked.connect(self.reset_outputs)

        actions = QtWidgets.QVBoxLayout()
        actions.setSpacing(6)
        actions.addWidget(self.btn_outputs_apply)
        actions.addWidget(self.btn_outputs_reset)
        side_layout.addLayout(actions)

        side_layout.addStretch(1)
        content.addWidget(side_panel, 0)

        card.body.addLayout(content)
        root.addWidget(card)

    def _create_output_row(self, row: int, name: str) -> QtWidgets.QWidget:
        """Genera un bloque visual para cada salida configurada."""
        container = QtWidgets.QFrame()
        container.setProperty("outputTile", True)
        container.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)

        layout = QtWidgets.QVBoxLayout(container)
        layout.setContentsMargins(16, 14, 16, 16)
        layout.setSpacing(10)

        header = QtWidgets.QHBoxLayout()
        header.setSpacing(8)

        lbl_name = QtWidgets.QLabel(name)
        lbl_name.setProperty("title3", True)
        header.addWidget(lbl_name)
        header.addStretch(1)

        status = QtWidgets.QLabel("Seguimiento")
        status.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        status.setMinimumWidth(80)
        status.setFixedHeight(24)
        status.setStyleSheet(self._status_stylesheet("#0f172a", "#e2e8f0"))
        header.addWidget(status)

        layout.addLayout(header)

        helper = QtWidgets.QLabel("Ajusta duración, modo y restauración automática para esta salida.")
        helper.setWordWrap(True)
        helper.setProperty("muted", True)
        layout.addWidget(helper)

        form = QtWidgets.QGridLayout()
        form.setContentsMargins(0, 0, 0, 0)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(6)

        lbl_duration = QtWidgets.QLabel("Duración (s)")
        lbl_duration.setProperty("muted", True)
        form.addWidget(lbl_duration, 0, 0)

        duration = QtWidgets.QSpinBox()
        duration.setRange(1, 900)
        duration.setSuffix(" s")
        duration.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        duration.setToolTip("Tiempo en segundos que la salida permanece activa en modo Pulso.")
        duration.setMaximumWidth(120)
        form.addWidget(duration, 0, 1)

        lbl_mode = QtWidgets.QLabel("Modo de operación")
        lbl_mode.setProperty("muted", True)
        form.addWidget(lbl_mode, 1, 0)

        mode = QtWidgets.QComboBox()
        mode.addItems(self._OUTPUT_MODES)
        mode.setToolTip("Define el modo operativo: Pulso, Sostenido o Seguimiento de evento.")
        mode.setMinimumWidth(150)
        mode.setSizeAdjustPolicy(QtWidgets.QComboBox.SizeAdjustPolicy.AdjustToContents)
        form.addWidget(mode, 1, 1)
        form.setColumnStretch(0, 1)
        form.setColumnStretch(1, 1)

        layout.addLayout(form)

        auto_reset = QtWidgets.QCheckBox("Auto-restaurar automáticamente")
        auto_reset.setChecked(True)
        auto_reset.setToolTip("Si está activo, el sistema regresará la salida a OFF de forma automática.")
        layout.addWidget(auto_reset)

        self._output_rows.append({
            "name": name,
            "status": status,
            "duration": duration,
            "mode": mode,
            "auto_reset": auto_reset,
        })

        mode.currentIndexChanged.connect(lambda _=None, r=row: self._on_mode_changed(r))
        duration.valueChanged.connect(self._mark_dirty)
        auto_reset.stateChanged.connect(self._mark_dirty)

        return container

    def _status_stylesheet(self, bg: str, fg: str) -> str:
        return (
            f"background-color: {bg};"
            f"color: {fg};"
            "border-radius: 9px;"
            "padding: 2px 10px;"
            "font-size: 10px;"
            "font-weight: 600;"
        )

    def _on_trigger_matrix_changed(self, *_args) -> None:
        self._update_remote_summary()
        self._mark_dirty()

    def _current_assignments(self) -> Dict[str, List[str]]:
        assignments: Dict[str, List[str]] = {key: [] for key in self._REMOTE_LABELS}
        for output, widgets in zip(self._OUTPUT_NAMES, self._trigger_rows):
            for rf in self._REMOTE_LABELS:
                cb = cast(QtWidgets.QCheckBox, widgets.get(rf))
                if cb and cb.isChecked():
                    assignments[rf].append(output)
        return assignments

    def _update_remote_summary(self) -> None:
        assignments = self._current_assignments()
        for rf, btn in self._remote_buttons.items():
            outputs = assignments.get(rf, [])
            label = self._remote_map_labels.get(rf)
            if outputs:
                joined = ", ".join(outputs)
                btn.setToolTip(f"{rf} activará: {joined}")
                if label:
                    label.setText(joined)
            else:
                btn.setToolTip(f"{rf} sin asignaciones.")
                if label:
                    label.setText("Sin asignar")
        if not any(assignments.values()):
            self.lbl_remote_status.setText("Asignaciones RF pendientes. Marca salidas en la matriz inferior.")
        else:
            self.lbl_remote_status.setText("Pulsa un botón del mando para probar las salidas asignadas.")

    def _handle_remote_press(self, rf: str, pressed: bool) -> None:
        assignments = self._current_assignments()
        outputs = assignments.get(rf, [])
        if not outputs:
            self.lbl_remote_status.setText(f"{rf} no tiene salidas asignadas actualmente.")
            return
        action = "Activar" if pressed else "Liberar"
        for name in outputs:
            self.sig_trigger_output.emit(name, action)
        joined = ", ".join(outputs)
        verb = "Activando" if pressed else "Liberando"
        self.lbl_remote_status.setText(f"{verb} {joined} desde {rf}.")

    # --------------------------------------------------------------
    #  Card: Disparadores automáticos
    # --------------------------------------------------------------
    def _build_triggers_card(self, root: QtWidgets.QVBoxLayout) -> None:
        card = Card("Disparadores automáticos")

        self._trigger_rows.clear()
        self._remote_buttons: Dict[str, QtWidgets.QToolButton] = {}
        self._remote_map_labels: Dict[str, QtWidgets.QLabel] = {}

        intro = QtWidgets.QLabel(
            "Sincroniza los mandos RF y las llamadas automáticas con las salidas disponibles."
        )
        intro.setProperty("muted", True)
        intro.setWordWrap(True)
        card.body.addWidget(intro)

        content = QtWidgets.QHBoxLayout()
        content.setSpacing(18)

        remote_panel = QtWidgets.QFrame()
        remote_panel.setProperty("remotePanel", True)
        remote_layout = QtWidgets.QGridLayout(remote_panel)
        remote_layout.setContentsMargins(12, 12, 12, 12)
        remote_layout.setHorizontalSpacing(12)
        remote_layout.setVerticalSpacing(12)

        style = QtWidgets.QApplication.style()
        remote_icons = [
            QtWidgets.QStyle.StandardPixmap.SP_MediaVolume,
            QtWidgets.QStyle.StandardPixmap.SP_MessageBoxWarning,
            QtWidgets.QStyle.StandardPixmap.SP_DialogResetButton,
            QtWidgets.QStyle.StandardPixmap.SP_DialogOkButton,
        ]
        remote_keys = list(self._REMOTE_LABELS.keys())
        for idx, rf in enumerate(remote_keys):
            cell = QtWidgets.QFrame()
            cell_layout = QtWidgets.QVBoxLayout(cell)
            cell_layout.setContentsMargins(0, 0, 0, 0)
            cell_layout.setSpacing(6)

            btn = QtWidgets.QToolButton()
            btn.setText(self._REMOTE_LABELS[rf])
            btn.setIcon(style.standardIcon(remote_icons[idx]))
            btn.setIconSize(QtCore.QSize(28, 28))
            btn.setToolButtonStyle(QtCore.Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            btn.setMinimumSize(96, 96)
            btn.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
            btn.pressed.connect(lambda rf=rf: self._handle_remote_press(rf, True))
            btn.released.connect(lambda rf=rf: self._handle_remote_press(rf, False))

            map_label = QtWidgets.QLabel("Sin asignar")
            map_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            map_label.setProperty("muted", True)

            cell_layout.addWidget(btn, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
            cell_layout.addWidget(map_label)
            remote_layout.addWidget(cell, idx // 2, idx % 2)
            self._remote_buttons[rf] = btn
            self._remote_map_labels[rf] = map_label

        remote_layout.setColumnStretch(0, 1)
        remote_layout.setColumnStretch(1, 1)

        content.addWidget(remote_panel, 1)

        matrix_panel = QtWidgets.QFrame()
        matrix_panel.setProperty("matrixPanel", True)
        matrix_layout = QtWidgets.QVBoxLayout(matrix_panel)
        matrix_layout.setContentsMargins(16, 16, 16, 16)
        matrix_layout.setSpacing(12)

        matrix_title = QtWidgets.QLabel("Asignaciones del mando")
        matrix_title.setProperty("title3", True)
        matrix_layout.addWidget(matrix_title)

        self.lbl_remote_status = QtWidgets.QLabel("Pad RF listo para pruebas instantáneas.")
        self.lbl_remote_status.setWordWrap(True)
        self.lbl_remote_status.setProperty("muted", True)
        matrix_layout.addWidget(self.lbl_remote_status)
        matrix_layout.addWidget(HLine())

        matrix_wrapper = QtWidgets.QWidget()
        matrix = QtWidgets.QGridLayout()
        matrix.setContentsMargins(0, 0, 0, 0)
        matrix.setHorizontalSpacing(10)
        matrix.setVerticalSpacing(6)

        header_label = QtWidgets.QLabel("Salida")
        header_label.setProperty("muted", True)
        matrix.addWidget(header_label, 0, 0)

        for col, name in enumerate(self._TRIGGER_COLUMNS, start=1):
            lbl = QtWidgets.QLabel(name)
            lbl.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            lbl.setProperty("muted", True)
            matrix.addWidget(lbl, 0, col)

        for row, output in enumerate(self._OUTPUT_NAMES, start=1):
            lbl_name = QtWidgets.QLabel(output)
            matrix.addWidget(lbl_name, row, 0)

            row_widgets: Dict[str, QtWidgets.QWidget] = {}
            for col, tname in enumerate(self._TRIGGER_COLUMNS, start=1):
                cb = QtWidgets.QCheckBox()
                cb.setToolTip(f"{tname} dispara {output}.")
                cb.stateChanged.connect(self._on_trigger_matrix_changed)
                matrix.addWidget(cb, row, col, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
                row_widgets[tname] = cb
            self._trigger_rows.append(row_widgets)

        matrix_wrapper.setLayout(matrix)
        matrix_layout.addWidget(matrix_wrapper)

        button_bar = QtWidgets.QHBoxLayout()
        button_bar.addStretch(1)

        self.btn_triggers_apply = QtWidgets.QPushButton("Aplicar disparadores")
        self.btn_triggers_apply.setProperty("primary", True)
        self.btn_triggers_apply.clicked.connect(lambda: self.sig_apply_triggers.emit(self.triggers()))
        button_bar.addWidget(self.btn_triggers_apply)

        self.btn_triggers_reset = QtWidgets.QPushButton("Desactivar todos")
        self.btn_triggers_reset.setProperty("ghost", True)
        self.btn_triggers_reset.clicked.connect(self.reset_triggers)
        button_bar.addWidget(self.btn_triggers_reset)

        matrix_layout.addLayout(button_bar)
        content.addWidget(matrix_panel, 2)

        card.body.addLayout(content)
        root.addWidget(card)
        self._update_remote_summary()

    # --------------------------------------------------------------
    #  Barra inferior: Importar/Exportar / Estado
    # --------------------------------------------------------------
    def _build_toolbar(self, root: QtWidgets.QVBoxLayout) -> None:
        toolbar = QtWidgets.QFrame()
        toolbar.setProperty("footerBar", True)
        row = QtWidgets.QHBoxLayout(toolbar)
        row.setContentsMargins(16, 12, 16, 12)
        row.setSpacing(12)

        self.lbl_dirty = QtWidgets.QLabel("Configuración sincronizada.")
        self.lbl_dirty.setProperty("muted", True)
        row.addWidget(self.lbl_dirty)

        quick = QtWidgets.QHBoxLayout()
        quick.setSpacing(8)

        btn_history = QtWidgets.QPushButton("Historial local")
        btn_history.setProperty("ghost", True)
        btn_history.setToolTip("Abrir registros recientes de activaciones comunitarias.")
        btn_history.clicked.connect(lambda: self.sig_show_history.emit())
        quick.addWidget(btn_history)

        btn_selftest = QtWidgets.QPushButton("Auto-chequeo")
        btn_selftest.setProperty("ghost", True)
        btn_selftest.setToolTip("Ejecuta pruebas de salud sobre sirena, batería y módulos RF.")
        btn_selftest.clicked.connect(lambda: self.sig_run_selftest.emit())
        quick.addWidget(btn_selftest)

        row.addStretch(1)
        row.addLayout(quick)
        row.addSpacing(12)

        btn_import = QtWidgets.QPushButton("Importar perfil")
        btn_import.setProperty("ghost", True)
        btn_import.setToolTip("Traer un perfil de automatización desde archivo.")
        btn_import.clicked.connect(lambda: self.sig_import_export.emit("import", None))
        row.addWidget(btn_import)

        btn_export = QtWidgets.QPushButton("Exportar perfil")
        btn_export.setProperty("primary", True)
        btn_export.setToolTip("Guardar esta configuración para reutilizarla luego.")
        btn_export.clicked.connect(lambda: self.sig_import_export.emit("export", {"outputs": self.outputs(), "triggers": self.triggers()}))
        row.addWidget(btn_export)

        root.addWidget(toolbar)
    # --------------------------------------------------------------
    #  Lógica de UI
    # --------------------------------------------------------------
    def _on_mode_changed(self, row: int) -> None:
        """Habilita/deshabilita controles según el Modo."""
        widgets = self._output_rows[row]
        mode = cast(QtWidgets.QComboBox, widgets["mode"]).currentText()
        duration = cast(QtWidgets.QSpinBox, widgets["duration"])
        auto_reset = cast(QtWidgets.QCheckBox, widgets["auto_reset"])
        status = cast(QtWidgets.QLabel, widgets["status"])
        status_cfg = self._STATUS_BY_MODE.get(mode, {"label": mode, "bg": "#4b5563", "fg": "#f8fafc"})
        status.setText(status_cfg["label"])
        status.setStyleSheet(self._status_stylesheet(status_cfg["bg"], status_cfg["fg"]))

        if mode == "Pulso":
            duration.setEnabled(True)
            auto_reset.setEnabled(False)
            auto_reset.setChecked(True)   # irrelevante en pulso
            auto_reset.setToolTip("En modo Pulso no es necesario restaurar manualmente la salida.")
        elif mode == "Sostenido":
            duration.setEnabled(False)
            auto_reset.setEnabled(True)
            auto_reset.setToolTip("Permite que el controlador apague la salida luego de una llamada remota.")
        else:  # Seguimiento de evento
            duration.setEnabled(False)
            auto_reset.setEnabled(False)
            auto_reset.setChecked(True)
            auto_reset.setToolTip("El evento externo gobierna la salida; no aplica auto-restaurar.")

        self._mark_dirty()

    def _mark_dirty(self, *_args) -> None:
        self._dirty = True
        self.lbl_dirty.setText("Cambios pendientes de aplicar.")

    def _clear_dirty(self) -> None:
        self._dirty = False
        self.lbl_dirty.setText("Configuración sincronizada.")

    def _emit_test_output(self) -> None:
        name = self.combo_test_output.currentText()
        action = self.combo_test_mode.currentText()
        if name:
            self.sig_trigger_output.emit(name, action)

    # --------------------------------------------------------------
    #  Serialización
    # --------------------------------------------------------------
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

    # --------------------------------------------------------------
    #  Triggers
    # --------------------------------------------------------------
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
        self._update_remote_summary()
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



