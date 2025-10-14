from __future__ import annotations

from PyQt6 import QtCore, QtWidgets

from app.ui.styles.styles import get_qss
from app.ui.parts.topbar import TopBar
from app.ui.parts.sidebar import SideBar
from app.ui.parts.router import PageRouter, PageSpec

from app.ui.pages.page_dashboard import PageDashboard
from app.ui.pages.page_contacts import PageContacts
from app.ui.pages.page_automation import PageAutomation
from app.ui.pages.page_audio import PageAudio
from app.ui.pages.page_server import PageServer
from app.ui.pages.page_notifications import PageNotifications
from app.ui.pages.page_logs import PageLogs
# from app.ui.pages.page_system import PageSystem

from app.__version__ import __version__, __title__


class MainWindow(QtWidgets.QMainWindow):
    """Ventana principal con barra lateral y paginas de configuracion."""

    sig_theme_changed = QtCore.pyqtSignal(str)

    def __init__(self, last_port: str = "COM3") -> None:
        super().__init__()
        self.setWindowTitle(f"{__title__} v{__version__}")
        self.resize(1200, 640)

        # --- Definicion de paginas (el orden determina la barra lateral)
        self._pages = [
            PageSpec("Dashboard", PageDashboard),
            PageSpec("Contactos", PageContacts),
            PageSpec("Automatizacion", PageAutomation),
            PageSpec("Audio", PageAudio),
            PageSpec("Servidor", PageServer),
            PageSpec("Notificaciones", PageNotifications),
            PageSpec("Logs", PageLogs),
            # PageSpec("Sistema", PageSystem),
        ]

        # --- Layout principal
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        root = QtWidgets.QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.topbar = TopBar(title="Configurador QC1", last_port=last_port)
        root.addWidget(self.topbar)

        body = QtWidgets.QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        root.addLayout(body, 1)

        self.sidebar = SideBar([p.name for p in self._pages], app_name=__title__, version=f"v{__version__}")
        body.addWidget(self.sidebar)

        self.router = PageRouter(self._pages)
        body.addWidget(self.router, 1)

        dashboard = self.router.page("Dashboard")
        if isinstance(dashboard, PageDashboard):
            dashboard.sig_shortcut_requested.connect(self._on_page_requested)

        # Conexiones
        self.sidebar.pageRequested.connect(self._on_page_requested)
        self.topbar.connectRequested.connect(self._on_connect_requested)

        # Tema inicial
        self._apply_light_theme()

        # Cargar pagina por defecto
        self._on_page_requested("Dashboard")

    def page(self, name: str) -> QtWidgets.QWidget | None:
        return self.router.page(name)

    # ------------------------------------------------------------------
    def _on_page_requested(self, name: str) -> None:
        self.router.setActive(name)
        self.sidebar.setActive(name)

    def _on_connect_requested(self, port: str) -> None:
        QtWidgets.QMessageBox.information(self, "Conectar", f"Conectar a {port}")

    def _apply_light_theme(self) -> None:
        app = QtWidgets.QApplication.instance()
        if not app:
            return
        app.setStyle("Fusion")
        #app.setStyleSheet(get_qss())
        if hasattr(self.topbar, "setTheme"):
            self.topbar.setTheme("light")
        self.sig_theme_changed.emit("light")


__all__ = ["MainWindow"]






