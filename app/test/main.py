"""
PyQt6 — UI base moderna (modular, sin lógica)
- Diseño: sidebar + topbar + páginas en QStackedWidget
- Estilo: QSS (paleta en Linseg Perú: rojo #C1121F, crema #F6E7D8, gris #1E1E1E)
- Modular: clases separadas para cada página; fácil de extraer a archivos
- Sin dependencias externas (solo PyQt6)
- Ready para integrar qc1_proto.py y backend serial posteriormente

Para dividir en módulos luego:
  - mover class Styles -> styles.py
  - mover MainWindow -> main_window.py
  - mover Page* -> pages/*.py
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from PyQt6 import QtWidgets, QtGui, QtCore

# --------------------
# Estilos y constantes
# --------------------
@dataclass
class Palette:
    red: str = "#C1121F"     # Linseg red
    cream: str = "#F6E7D8"   # soft cream accent
    dark: str = "#1E1E1E"    # near-black bg
    mid: str = "#2A2A2A"     # cards / surfaces
    light: str = "#F5F5F7"   # text on dark
    gray: str = "#8A8F98"     # muted text
    blue: str = "#2272FF"    # focus/selection

class Styles:
    PAL = Palette()

    GLOBAL_QSS = f"""
    /* Fuentes y defaults */
    * {{
        font-family: Inter, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        font-size: 13px;
    }}

    QMainWindow {{ background: {PAL.dark}; }}

    /* Topbar */
    #TopBar {{ background: {PAL.mid}; border-bottom: 1px solid #3A3A3A; }}
    #TopTitle {{ color: {PAL.light}; font-weight: 600; font-size: 14px; }}
    #TopSubtitle {{ color: {PAL.gray}; font-size: 12px; }}

    /* Sidebar */
    #SideBar {{ background: #141414; border-right: 1px solid #242424; }}
    QPushButton[sideBtn="true"] {{
        color: {PAL.light}; text-align: left; padding: 10px 12px; border: none; border-radius: 8px;
    }}
    QPushButton[sideBtn="true"]:hover {{ background: #1F1F1F; }}
    QPushButton[sideBtn="true"][active="true"] {{ background: {PAL.red}; color: white; }}

    /* Tarjetas */
    QFrame[card="true"] {{ background: {PAL.mid}; border-radius: 14px; border: 1px solid #333; }}
    QLabel[cardTitle="true"] {{ color: {PAL.light}; font-weight: 600; }}
    QLabel[muted="true"] {{ color: {PAL.gray}; }}
    QLineEdit, QComboBox, QSpinBox {{
        background: #171717; color: {PAL.light}; border: 1px solid #363636; border-radius: 8px; padding: 8px;
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{ border: 1px solid {PAL.blue}; }}
    QTextEdit {{ background: #171717; color: {PAL.light}; border: 1px solid #363636; border-radius: 12px; padding: 8px; }}

    QScrollArea {{ border: none; }}

    /* Botones primarios */
    QPushButton[primary="true"] {{
        background: {PAL.red}; color: white; border: none; border-radius: 10px; padding: 9px 14px; font-weight: 600;
    }}
    QPushButton[primary="true"]:hover {{ filter: brightness(1.1); }}

    /* Botones fantasma */
    QPushButton[ghost="true"] {{
        background: transparent; color: {PAL.light}; border: 1px solid #333; border-radius: 10px; padding: 9px 14px;
    }}
    QPushButton[ghost="true"]:hover {{ border-color: #444; }}

    QTabWidget::pane {{ border: none; }}
    QTabBar::tab {{ background: transparent; color: {PAL.light}; padding: 8px 12px; }}
    QTabBar::tab:selected {{ border-bottom: 2px solid {PAL.red}; }}
    """

# --------------------
# Widgets utilitarios
# --------------------
class VSpacer(QtWidgets.QWidget):
    def __init__(self, h=8):
        super().__init__()
        self.setFixedHeight(h)

class HLine(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.setStyleSheet("color: #2F2F2F;")

class Card(QtWidgets.QFrame):
    def __init__(self, title: str | None = None):
        super().__init__()
        self.setProperty("card", True)
        lay = QtWidgets.QVBoxLayout(self)
        lay.setContentsMargins(14, 14, 14, 14)
        lay.setSpacing(10)
        if title:
            t = QtWidgets.QLabel(title)
            t.setProperty("cardTitle", True)
            lay.addWidget(t)
            lay.addWidget(HLine())
        self.body = lay

# --------------------
# Páginas (solo UI)
# --------------------
class PageDashboard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        row = QtWidgets.QHBoxLayout()
        row.setSpacing(12)
        # Card: Estado del equipo
        c1 = Card("Estado del equipo")
        grid = QtWidgets.QGridLayout()
        grid.setVerticalSpacing(8)
        for i, (k, v) in enumerate([
            ("Modelo", "ALR-LTE"),
            ("ID", "A1B2C3"),
            ("FW", "1.0.0"),
            ("Señal", "- dBm"),
        ]):
            lk = QtWidgets.QLabel(k + ":")
            lk.setProperty("muted", True)
            lv = QtWidgets.QLabel(v)
            grid.addWidget(lk, i, 0)
            grid.addWidget(lv, i, 1)
        c1.body.addLayout(grid)

        # Card: Acciones rápidas
        c2 = Card("Acciones rápidas")
        btnRow = QtWidgets.QHBoxLayout()
        for txt in ("Ping", "Info", "Guardar", "Reiniciar"):
            b = QtWidgets.QPushButton(txt)
            b.setProperty("ghost", True)
            btnRow.addWidget(b)
        c2.body.addLayout(btnRow)

        row.addWidget(c1, 1)
        row.addWidget(c2, 1)

        # Lista de eventos
        c3 = Card("Eventos recientes")
        self.events = QtWidgets.QTextEdit()
        self.events.setReadOnly(True)
        self.events.setPlaceholderText("EVT,DEV,SEQ,TS,evento,k=v …")
        c3.body.addWidget(self.events)

        root.addLayout(row)
        root.addWidget(c3)

class PageAudio(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Slots
        cSlots = Card("Audios — Slots (1..4)")
        table = QtWidgets.QTableWidget(4, 6)
        table.setHorizontalHeaderLabels(["Slot", "Tipo", "Dur (s)", "Estado", "Size", "ENC"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(False)
        table.setShowGrid(False)
        table.horizontalHeader().setStretchLastSection(True)
        for r in range(4):
            for c in range(6):
                item = QtWidgets.QTableWidgetItem("–")
                table.setItem(r, c, item)
        cSlots.body.addWidget(table)

        # Controles
        cCtrl = Card("Controles")
        form = QtWidgets.QHBoxLayout()
        self.editSlot = QtWidgets.QSpinBox(); self.editSlot.setRange(1,4)
        self.comboAction = QtWidgets.QComboBox(); self.comboAction.addItems(["ON", "OFF"]) 
        self.editDur = QtWidgets.QSpinBox(); self.editDur.setRange(10,240); self.editDur.setValue(60)
        self.btnSend = QtWidgets.QPushButton("Enviar")
        self.btnSend.setProperty("primary", True)
        for w, name in [
            (self.editSlot, "Slot"), (self.comboAction, "Acción"), (self.editDur, "Duración"), (self.btnSend, " ")]:
            v = QtWidgets.QVBoxLayout();
            lab = QtWidgets.QLabel(name); lab.setProperty("muted", True)
            v.addWidget(lab); v.addWidget(w)
            form.addLayout(v)
        cCtrl.body.addLayout(form)

        # Subida
        cUp = Card("Subir audio (slot 4)")
        upForm = QtWidgets.QHBoxLayout()
        self.filePath = QtWidgets.QLineEdit(); self.filePath.setPlaceholderText("Selecciona archivo…")
        self.btnBrowse = QtWidgets.QPushButton("Examinar…"); self.btnBrowse.setProperty("ghost", True)
        self.btnUpload = QtWidgets.QPushButton("Subir"); self.btnUpload.setProperty("primary", True)
        upForm.addWidget(self.filePath, 1); upForm.addWidget(self.btnBrowse); upForm.addWidget(self.btnUpload)
        cUp.body.addLayout(upForm)

        root.addWidget(cSlots)
        root.addWidget(cCtrl)
        root.addWidget(cUp)

class PageContacts(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        cAdmins = Card("Administradores (0 y 1)")
        grid = QtWidgets.QGridLayout(); grid.setVerticalSpacing(8)
        for idx in (0,1):
            grid.addWidget(QtWidgets.QLabel(f"Admin {idx}"), idx, 0)
            for col, label in enumerate(["TEL", "NAME", "LOC", "RF", "FLAGS"]):
                le = QtWidgets.QLineEdit(); le.setPlaceholderText(label)
                grid.addWidget(le, idx, col+1)
        cAdmins.body.addLayout(grid)

        cUsers = Card("Usuarios / Policía / Grupo")
        row = QtWidgets.QHBoxLayout()
        self.findBox = QtWidgets.QLineEdit(); self.findBox.setPlaceholderText("Filtro: tel:9* | name:Jose | rf:001 …")
        self.btnSearch = QtWidgets.QPushButton("Buscar"); self.btnSearch.setProperty("ghost", True)
        self.btnAdd = QtWidgets.QPushButton("Agregar"); self.btnAdd.setProperty("primary", True)
        row.addWidget(self.findBox, 1); row.addWidget(self.btnSearch); row.addWidget(self.btnAdd)
        cUsers.body.addLayout(row)
        table = QtWidgets.QTableWidget(0, 7)
        table.setHorizontalHeaderLabels(["ID", "ROLE", "TEL", "NAME", "LOC", "RF", "FLAGS"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        table.horizontalHeader().setStretchLastSection(True)
        cUsers.body.addWidget(table)

        root.addWidget(cAdmins)
        root.addWidget(cUsers)

class PageServer(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16,16,16,16)
        root.setSpacing(12)

        c = Card("Servidor de reporte")
        form = QtWidgets.QGridLayout(); form.setVerticalSpacing(8)
        labels = ["Modo (TCP/UDP/MQTT/HTTP)", "Host", "Puerto", "TLS", "User", "Pass", "Topic pub", "Topic sub"]
        widgets = [QtWidgets.QComboBox(), QtWidgets.QLineEdit(), QtWidgets.QSpinBox(), QtWidgets.QComboBox(),
                   QtWidgets.QLineEdit(), QtWidgets.QLineEdit(), QtWidgets.QLineEdit(), QtWidgets.QLineEdit()]
        widgets[0].addItems(["MQTT", "TCP", "UDP", "HTTP"]) ; widgets[3].addItems(["0","1"])
        widgets[2].setRange(1,65535)
        for i,(lab,w) in enumerate(zip(labels, widgets)):
            l = QtWidgets.QLabel(lab); l.setProperty("muted", True)
            form.addWidget(l, i, 0); form.addWidget(w, i, 1)
        btns = QtWidgets.QHBoxLayout()
        bTest = QtWidgets.QPushButton("Probar"); bTest.setProperty("ghost", True)
        bSave = QtWidgets.QPushButton("Guardar"); bSave.setProperty("primary", True)
        btns.addStretch(1); btns.addWidget(bTest); btns.addWidget(bSave)
        c.body.addLayout(form); c.body.addLayout(btns)
        root.addWidget(c)

class PageSystem(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16,16,16,16)
        root.setSpacing(12)

        c = Card("Sistema")
        grid = QtWidgets.QGridLayout(); grid.setVerticalSpacing(8)
        for i,(k,v) in enumerate([
            ("Baudios", "115200"), ("Firma", "QC1"), ("Modelo", "ALR-LTE"), ("Dev ID", "A1B2C3"),
        ]):
            l = QtWidgets.QLabel(k); l.setProperty("muted", True)
            e = QtWidgets.QLineEdit(v)
            grid.addWidget(l, i, 0); grid.addWidget(e, i, 1)
        c.body.addLayout(grid)

        row = QtWidgets.QHBoxLayout()
        bDefaults = QtWidgets.QPushButton("Restaurar fábrica"); bDefaults.setProperty("ghost", True)
        bSave = QtWidgets.QPushButton("Guardar NVS"); bSave.setProperty("primary", True)
        row.addStretch(1); row.addWidget(bDefaults); row.addWidget(bSave)
        c.body.addLayout(row)

        root.addWidget(c)

class PageLogs(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16,16,16,16)
        root.setSpacing(12)

        c = Card("Console / Logs")
        self.txt = QtWidgets.QTextEdit(); self.txt.setReadOnly(True)
        c.body.addWidget(self.txt)
        root.addWidget(c)

# --------------------
# Ventana principal
# --------------------
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configurador QC1 — Linseg")
        self.resize(1150, 720)
        self.setWindowIcon(QtGui.QIcon())

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)

        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(0)

        layout.addWidget(self._make_topbar())
        body = QtWidgets.QHBoxLayout(); body.setContentsMargins(0,0,0,0); body.setSpacing(0)
        layout.addLayout(body, 1)

        self.side = self._make_sidebar()
        body.addWidget(self.side)

        self.pages = QtWidgets.QStackedWidget()
        self.page_map = {
            "Dashboard": PageDashboard(),
            "Audio": PageAudio(),
            "Contactos": PageContacts(),
            "Servidor": PageServer(),
            "Sistema": PageSystem(),
            "Logs": PageLogs(),
        }
        for w in self.page_map.values():
            self.pages.addWidget(w)
        body.addWidget(self.pages, 1)

        # Activa Dashboard por defecto
        self._set_active("Dashboard")

    def _make_topbar(self) -> QtWidgets.QWidget:
        top = QtWidgets.QFrame(); top.setObjectName("TopBar")
        lay = QtWidgets.QHBoxLayout(top)
        lay.setContentsMargins(14,10,14,10)
        title = QtWidgets.QLabel("Configurador QC1") ; title.setObjectName("TopTitle")
        sub = QtWidgets.QLabel("Interfaz base — PyQt6") ; sub.setObjectName("TopSubtitle")
        box = QtWidgets.QVBoxLayout(); box.setSpacing(0)
        box.addWidget(title); box.addWidget(sub)
        lay.addLayout(box)
        lay.addStretch(1)
        # Placeholder: selector de puerto, conexión
        port = QtWidgets.QComboBox(); port.addItems(["/dev/ttyUSB0", "COM3", "COM7"]) ; port.setFixedWidth(160)
        btn = QtWidgets.QPushButton("Conectar"); btn.setProperty("primary", True)
        lay.addWidget(port); lay.addWidget(btn)
        return top

    def _make_sidebar(self) -> QtWidgets.QWidget:
        side = QtWidgets.QFrame(); side.setObjectName("SideBar")
        lay = QtWidgets.QVBoxLayout(side)
        lay.setContentsMargins(12,12,12,12); lay.setSpacing(8)
        logo = QtWidgets.QLabel("🛡️ Linseg")
        logo.setStyleSheet("color: white; font-weight:700; font-size:16px;")
        lay.addWidget(logo)
        lay.addWidget(VSpacer(8))
        for name in ["Dashboard", "Audio", "Contactos", "Servidor", "Sistema", "Logs"]:
            b = QtWidgets.QPushButton(name)
            b.setProperty("sideBtn", True)
            b.clicked.connect(lambda _, n=name: self._set_active(n))
            lay.addWidget(b)
        lay.addStretch(1)
        foot = QtWidgets.QLabel("v1.0.0") ; foot.setProperty("muted", True)
        lay.addWidget(foot)
        return side

    def _set_active(self, name: str):
        # cambia página
        idx = list(self.page_map.keys()).index(name)
        self.pages.setCurrentIndex(idx)
        # marca botón activo
        for i in range(self.side.layout().count()):
            w = self.side.layout().itemAt(i).widget()
            if isinstance(w, QtWidgets.QPushButton) and w.property("sideBtn"):
                w.setProperty("active", w.text() == name)
                w.style().unpolish(w); w.style().polish(w)

# --------------------
# main
# --------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    # Forzar a Qt a NO usar el tema oscuro nativo
    app.setStyle("Fusion")
    app.setStyleSheet(Styles.GLOBAL_QSS)

    w = MainWindow()
    w.show()
    sys.exit(app.exec())
