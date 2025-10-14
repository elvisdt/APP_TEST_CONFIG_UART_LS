from __future__ import annotations

from PyQt6 import QtCore, QtWidgets

from app.__version__ import __title__, __version__


class TopBar(QtWidgets.QFrame):
    """Header with branding, serial-port selector and connect action."""

    themeChanged = QtCore.pyqtSignal(str)
    connectRequested = QtCore.pyqtSignal(str)

    def __init__(
        self,
        title: str = "Configurador QC1",
        subtitle: str | None = None,
        last_port: str = "COM3",
        ports: list[str] | None = None,
        enable_theme_toggle: bool = False,
    ) -> None:
        super().__init__()
        self.setObjectName("TopBar")

        ports = ports or [last_port]
        if last_port not in ports:
            ports = [last_port, *ports]

        self._theme = "light"
        self._theme_toggle_enabled = enable_theme_toggle

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(12)

        branding = QtWidgets.QVBoxLayout()
        branding.setSpacing(2)

        title_label = QtWidgets.QLabel(title)
        title_label.setObjectName("TopTitle")
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        branding.addWidget(title_label)

        subtitle_label = QtWidgets.QLabel(subtitle or f"{__title__} v{__version__}")
        subtitle_label.setObjectName("TopSubtitle")
        subtitle_label.setProperty("muted", True)
        branding.addWidget(subtitle_label)

        layout.addLayout(branding)

        self.status_label = QtWidgets.QLabel("Sin conexión")
        self.status_label.setProperty("muted", True)
        layout.addWidget(self.status_label)
        layout.addStretch(1)

        self.btn_theme = QtWidgets.QPushButton("Oscuro")
        self.btn_theme.setCheckable(True)
        self.btn_theme.setProperty("ghost", True)
        self.btn_theme.toggled.connect(self._on_toggle_theme)
        self.btn_theme.setVisible(enable_theme_toggle)
        self.btn_theme.setEnabled(enable_theme_toggle)
        layout.addWidget(self.btn_theme)

        self.port_combo = QtWidgets.QComboBox()
        self.port_combo.setFixedWidth(160)
        self.port_combo.addItems(ports)
        self.port_combo.setCurrentText(last_port)
        layout.addWidget(self.port_combo)

        self.btn_connect = QtWidgets.QPushButton("Conectar")
        self.btn_connect.setProperty("primary", True)
        self.btn_connect.clicked.connect(self._emit_connect)
        layout.addWidget(self.btn_connect)

        self._sync_theme_btn()

    # --- Public API -------------------------------------------------
    def set_ports(self, ports: list[str], current: str | None = None) -> None:
        block = self.port_combo.blockSignals(True)
        self.port_combo.clear()
        self.port_combo.addItems(ports)
        if current:
            self.port_combo.setCurrentText(current)
        self.port_combo.blockSignals(block)

    def set_connection_state(self, connected: bool, port: str | None = None) -> None:
        self.btn_connect.setText("Desconectar" if connected else "Conectar")
        self.btn_connect.setProperty("primary", not connected)
        self.btn_connect.setProperty("ghost", connected)
        self.btn_connect.style().unpolish(self.btn_connect)
        self.btn_connect.style().polish(self.btn_connect)
        self.status_label.setText(f"Conectado: {port}" if connected and port else "Sin conexión")

    def setTheme(self, theme: str) -> None:  # noqa: N802 - Qt naming style
        if theme not in ("light", "dark"):
            return
        if theme != self._theme:
            self._theme = theme
            self._sync_theme_btn()

    def currentPort(self) -> str:  # noqa: N802 - Qt naming style
        return self.port_combo.currentText()

    # --- Internal helpers ------------------------------------------
    def _sync_theme_btn(self) -> None:
        self.btn_theme.setChecked(self._theme == "dark")
        self.btn_theme.setText("Claro" if self._theme == "dark" else "Oscuro")

    def _on_toggle_theme(self, checked: bool) -> None:
        if not self._theme_toggle_enabled:
            self.btn_theme.setChecked(False)
            return
        self._theme = "dark" if checked else "light"
        self._sync_theme_btn()
        self.themeChanged.emit(self._theme)

    def _emit_connect(self) -> None:
        self.connectRequested.emit(self.currentPort())
