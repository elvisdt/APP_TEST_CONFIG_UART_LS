from __future__ import annotations

import os
import signal
import sys
from pathlib import Path
from typing import Iterable, TYPE_CHECKING

from PyQt6 import QtCore, QtGui, QtWidgets

if TYPE_CHECKING:  # pragma: no cover - typing aids
    from app.core.settings import Settings
    from app.ui.main_window import MainWindow

try:
    from app.__version__ import __title__, __version__
except Exception:
    __title__, __version__ = "Linseg QC1", "0.0.0"


def _application_root() -> Path:
    """Return the directory where the Qt resources live."""
    if getattr(sys, "frozen", False):  # pragma: no cover - runtime guard
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent


def _set_windows_app_id(app_id: str = "Linseg.QC1") -> None:
    if os.name != "nt":
        return
    try:
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass


def _install_excepthook() -> None:
    def _handler(exc_type, exc, tb):
        import traceback

        text = "".join(traceback.format_exception(exc_type, exc, tb))
        if QtWidgets.QApplication.instance() is not None:
            QtWidgets.QMessageBox.critical(None, "Error no controlado", text)
        print(text, file=sys.stderr)

    sys.excepthook = _handler


def _configure_high_dpi() -> None:
    application_attr = getattr(QtCore.Qt, "ApplicationAttribute", None)
    if application_attr is not None:
        for name in ("AA_UseHighDpiPixmaps", "AA_EnableHighDpiScaling"):
            if hasattr(application_attr, name):
                QtWidgets.QApplication.setAttribute(getattr(application_attr, name), True)
    try:
        policy = getattr(QtCore.Qt, "HighDpiScaleFactorRoundingPolicy", None)
        if policy is not None and hasattr(policy, "PassThrough"):
            QtGui.QGuiApplication.setHighDpiScaleFactorRoundingPolicy(getattr(policy, "PassThrough"))
    except Exception:
        pass


def _normalize_argv(argv: Iterable[str] | None) -> list[str]:
    if argv is None:
        return sys.argv
    return list(argv)


def _apply_app_metadata(app: QtWidgets.QApplication) -> None:
    app.setOrganizationName("Linseg")
    app.setApplicationName(__title__)
    app.setApplicationVersion(__version__)


def _apply_style(app: QtWidgets.QApplication, root: Path) -> None:
    from app.ui.styles.styles import Styles

    app.setStyle("Fusion")
    #app.setStyleSheet(Styles.light())

    icon_path = root / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QtGui.QIcon(str(icon_path)))


def _install_signal_handlers() -> None:
    def _graceful_exit(*_: object) -> None:
        QtWidgets.QApplication.quit()

    signal.signal(signal.SIGINT, _graceful_exit)
    if hasattr(signal, "SIGTERM"):
        try:
            signal.signal(signal.SIGTERM, _graceful_exit)
        except Exception:
            pass


def _load_settings(root: Path) -> Settings:
    from app.core.settings import Settings

    return Settings.load(str(root / "data" / "settings.json"))


def _build_main_window(last_port: str) -> MainWindow:
    from app.ui.main_window import MainWindow

    return MainWindow(last_port=last_port)


def _wire_controllers(window: MainWindow, settings: Settings) -> None:
    from app.controllers.app_controller import AppController

    AppController(window, settings)


def main(argv: Iterable[str] | None = None) -> int:
    root = _application_root()
    project_root = root.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    os.chdir(root)

    _set_windows_app_id("Linseg.QC1")
    _install_excepthook()
    _configure_high_dpi()

    app = QtWidgets.QApplication(_normalize_argv(argv))
    _apply_app_metadata(app)
    _apply_style(app, root)
    _install_signal_handlers()

    settings = _load_settings(root)
    window = _build_main_window(settings.last_port)
    _wire_controllers(window, settings)

    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())


