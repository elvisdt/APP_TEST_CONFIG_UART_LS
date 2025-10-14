# from PyQt6 import QtCore

# from app.core import csv_service
# from app.ui.pages.page_contacts import PageContacts


# class ContactsController(QtCore.QObject):
#     def __init__(self, page: PageContacts):
#         super().__init__()
#         self.page = page
#         page.sig_import_auth.connect(self.on_import_auth)
#         page.sig_export_auth.connect(self.on_export_auth)
#         page.sig_import_gsm.connect(self.on_import_gsm)
#         page.sig_export_gsm.connect(self.on_export_gsm)

#     def on_import_auth(self, path: str) -> None:
#         self.page.fill_auth(csv_service.import_auth(path))

#     def on_export_auth(self, path: str) -> None:
#         csv_service.export_auth(path, self.page.read_auth())

#     def on_import_gsm(self, path: str) -> None:
#         self.page.fill_gsm(csv_service.import_gsm(path))

#     def on_export_gsm(self, path: str) -> None:
#         csv_service.export_gsm(path, self.page.read_gsm())
