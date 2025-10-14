from PyQt6 import QtCore

from app.core.settings import Settings
from app.ui.main_window import MainWindow
from app.controllers.device_controller import DeviceController
#from app.controllers.contact_controller import ContactsController


class AppController(QtCore.QObject):
    def __init__(self, win: MainWindow, settings: Settings):
        super().__init__()
        self.win = win
        self.settings = settings

        #self.contacts_ctl = ContactsController(self.win.page("Contactos"))

        self.device = DeviceController(win, settings)
        self.win.sig_theme_changed.connect(self._on_theme_changed)

    def _on_theme_changed(self, theme: str) -> None:
        self.settings.theme = theme
        self.settings.save("app/data/settings.json")
