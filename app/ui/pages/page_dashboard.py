from PyQt6 import QtCore, QtWidgets

from app.ui.widgets.card import Card


class PageDashboard(QtWidgets.QWidget):
    """Landing page with device status, communications and quick navigation."""

    sig_shortcut_requested = QtCore.pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        self._build_status_row(root)
        self._build_summary_row(root)
        self._build_timeline(root)

    # ------------------------------------------------------------------
    def _build_status_row(self, root: QtWidgets.QVBoxLayout) -> None:
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(12)
        root.addLayout(row)

        row.addWidget(self._make_status_card(), 1)
        row.addWidget(self._make_comms_card(), 1)
        row.addWidget(self._make_shortcuts_card(), 1)

    def _build_summary_row(self, root: QtWidgets.QVBoxLayout) -> None:
        row = QtWidgets.QHBoxLayout()
        row.setSpacing(12)
        root.addLayout(row)

        row.addWidget(self._make_summary_card(), 1)
        row.addWidget(self._make_pending_card(), 1)

    def _build_timeline(self, root: QtWidgets.QVBoxLayout) -> None:
        timeline = Card("Eventos recientes")
        self.timeline_list = QtWidgets.QListWidget()
        self.timeline_list.addItems([
            "09:41 Dispositivo encendido",
            "09:42 SIM detectada",
            "09:44 Conexion a servidor pendiente",
            "09:50 Ultimo ping MQTT correcto",
        ])
        timeline.body.addWidget(self.timeline_list)
        root.addWidget(timeline)

    # ------------------------------------------------------------------
    def _make_status_card(self) -> Card:
        card = Card("Estado del equipo")
        grid = QtWidgets.QGridLayout()
        grid.setVerticalSpacing(8)
        entries = [
            ("Modelo", "ALR-LTE"),
            ("ID", "A1B2C3"),
            ("FW", "1.0.0"),
            ("Bateria", "12.4 V"),
            ("Senal", "-68 dBm"),
        ]
        for idx, (label, value) in enumerate(entries):
            l_key = QtWidgets.QLabel(f"{label}:")
            l_key.setProperty("muted", True)
            l_val = QtWidgets.QLabel(value)
            grid.addWidget(l_key, idx, 0)
            grid.addWidget(l_val, idx, 1)
        card.body.addLayout(grid)
        return card

    def _make_comms_card(self) -> Card:
        card = Card("Comunicaciones")
        grid = QtWidgets.QGridLayout()
        grid.setVerticalSpacing(8)
        data = [
            ("MQTT", "LS Cloud", "En linea"),
            ("WhatsApp", "Grupo Seguridad", "Listo"),
            ("App movil", "12 usuarios", "Sincronizado"),
            ("Ultimo heartbeat", "09:48"),
        ]
        for row, entry in enumerate(data):
            if len(entry) == 3:
                channel, target, status = entry
                lbl_channel = QtWidgets.QLabel(channel)
                lbl_channel.setProperty("cardTitle", True)
                lbl_target = QtWidgets.QLabel(target)
                lbl_target.setProperty("muted", True)
                lbl_status = QtWidgets.QLabel(status)
                grid.addWidget(lbl_channel, row * 2, 0)
                grid.addWidget(lbl_status, row * 2, 1)
                grid.addWidget(lbl_target, row * 2 + 1, 0, 1, 2)
            else:
                label, value = entry
                lbl_label = QtWidgets.QLabel(label)
                lbl_label.setProperty("muted", True)
                lbl_value = QtWidgets.QLabel(value)
                grid.addWidget(lbl_label, row * 2, 0)
                grid.addWidget(lbl_value, row * 2, 1)
        card.body.addLayout(grid)
        return card

    def _make_shortcuts_card(self) -> Card:
        card = Card("Atajos rapidos")
        column = QtWidgets.QVBoxLayout()
        column.setSpacing(8)
        buttons = [
            ("Configurar entradas", "Automatizacion"),
            ("Gestionar grupos", "Notificaciones"),
            ("Cargar contactos", "Contactos"),
            ("Actualizar audios", "Audio"),
        ]
        for text, page in buttons:
            button = QtWidgets.QPushButton(text)
            button.setProperty("ghost", True)
            button.setProperty("shortcutTarget", page)
            button.clicked.connect(lambda _, target=page: self.sig_shortcut_requested.emit(target))
            column.addWidget(button)
        column.addStretch(1)
        card.body.addLayout(column)
        return card

    def _make_summary_card(self) -> Card:
        card = Card("Resumen de configuracion")
        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        form.addRow("Entradas activas", QtWidgets.QLabel("6"))
        form.addRow("Salidas configuradas", QtWidgets.QLabel("4"))
        form.addRow("Horarios", QtWidgets.QLabel("2"))
        form.addRow("Grupos WA", QtWidgets.QLabel("2"))
        card.body.addLayout(form)
        return card

    def _make_pending_card(self) -> Card:
        card = Card("Pendientes / Checklist")
        checklist = QtWidgets.QListWidget()
        checklist.addItems([
            "Verificar horarios de sirena",
            "Subir audio de mensaje vecinal",
            "Confirmar numeros autorizados",
        ])
        card.body.addWidget(checklist)
        return card


__all__ = ["PageDashboard"]
