"""
Configurador QC1 — PyQt6 (tema claro/oscuro Hunter + CSV contactos)
- Toggle de tema en tiempo real (Claro/Oscuro)
- Contactos tipo Teltonika con Importar/Exportar CSV (en memoria)
- Sin serial; listo para integrar backend
"""
from __future__ import annotations

import sys, csv
from dataclasses import dataclass
from PyQt6 import QtWidgets, QtGui, QtCore

# =============================
# Estilos (temas Hunter)
# =============================
@dataclass
class Palette:
    red: str = "#C1121F"     # Hunter red
    cream: str = "#FDF7F2"   # crema clara
    light: str = "#FFFFFF"   # fondo base
    dark_text: str = "#222"  # texto principal
    gray: str = "#666"       # texto secundario
    border: str = "#DDD"     # bordes
    blue: str = "#2272FF"    # focus

    # Dark
    d_bg: str = "#1E1E1E"
    d_mid: str = "#2A2A2A"
    d_text: str = "#F5F5F7"
    d_muted: str = "#A0A4AA"
    d_border: str = "#343434"

class Styles:
    PAL = Palette()

    @classmethod
    def light(cls) -> str:
        P = cls.PAL
        return f"""
        * {{ font-family: Inter, 'Segoe UI', Roboto, sans-serif; font-size: 13px; }}
        QMainWindow {{ background: {P.light}; }}
        #TopBar {{ background: {P.cream}; border-bottom: 1px solid {P.border}; }}
        #TopTitle {{ color: {P.dark_text}; font-weight: 600; font-size: 14px; }}
        #TopSubtitle {{ color: {P.gray}; font-size: 12px; }}
        #SideBar {{ background: {P.cream}; border-right: 1px solid {P.border}; }}
        QPushButton[sideBtn="true"] {{ color: {P.dark_text}; text-align: left; padding: 10px 12px; border: none; border-radius: 8px; }}
        QPushButton[sideBtn="true"]:hover {{ background: #EEE; }}
        QPushButton[sideBtn="true"][active="true"] {{ background: {P.red}; color: white; }}
        QFrame[card="true"] {{ background: {P.cream}; border-radius: 14px; border: 1px solid {P.border}; }}
        QLabel[cardTitle="true"] {{ color: {P.dark_text}; font-weight: 600; }}
        QLabel[muted="true"] {{ color: {P.gray}; }}
        QLineEdit, QComboBox, QSpinBox {{ background: white; color: {P.dark_text}; border: 1px solid {P.border}; border-radius: 8px; padding: 6px; }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{ border: 1px solid {P.blue}; }}
        QTextEdit {{ background: white; color: {P.dark_text}; border: 1px solid {P.border}; border-radius: 12px; padding: 6px; }}
        QPushButton[primary="true"] {{ background: {P.red}; color: white; border: none; border-radius: 10px; padding: 8px 14px; font-weight: 600; }}
        QPushButton[primary="true"]:hover {{ filter: brightness(1.1); }}
        QPushButton[ghost="true"] {{ background: transparent; color: {P.dark_text}; border: 1px solid {P.border}; border-radius: 10px; padding: 8px 14px; }}
        QPushButton[ghost="true"]:hover {{ background: #FAFAFA; }}
        QTableWidget {{ background: white; border: 1px solid {P.border}; border-radius: 10px; }}
        QHeaderView::section {{ background: #FAFAFA; border: 1px solid {P.border}; padding: 6px; }}
        QTabWidget::pane {{ border: none; }}
        QTabBar::tab {{ background: transparent; color: {P.dark_text}; padding: 8px 12px; }}
        QTabBar::tab:selected {{ border-bottom: 2px solid {P.red}; }}
        """

    @classmethod
    def dark(cls) -> str:
        P = cls.PAL
        return f"""
        * {{ font-family: Inter, 'Segoe UI', Roboto, sans-serif; font-size: 13px; }}
        QMainWindow {{ background: {P.d_bg}; }}
        #TopBar {{ background: {P.d_mid}; border-bottom: 1px solid {P.d_border}; }}
        #TopTitle {{ color: {P.d_text}; font-weight: 600; font-size: 14px; }}
        #TopSubtitle {{ color: {P.d_muted}; font-size: 12px; }}
        #SideBar {{ background: #141414; border-right: 1px solid {P.d_border}; }}
        QPushButton[sideBtn="true"] {{ color: {P.d_text}; text-align: left; padding: 10px 12px; border: none; border-radius: 8px; }}
        QPushButton[sideBtn="true"]:hover {{ background: #1F1F1F; }}
        QPushButton[sideBtn="true"][active="true"] {{ background: {P.red}; color: white; }}
        QFrame[card="true"] {{ background: {P.d_mid}; border-radius: 14px; border: 1px solid {P.d_border}; }}
        QLabel[cardTitle="true"] {{ color: {P.d_text}; font-weight: 600; }}
        QLabel[muted="true"] {{ color: {P.d_muted}; }}
        QLineEdit, QComboBox, QSpinBox {{ background: #171717; color: {P.d_text}; border: 1px solid {P.d_border}; border-radius: 8px; padding: 8px; }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{ border: 1px solid {P.blue}; }}
        QTextEdit {{ background: #171717; color: {P.d_text}; border: 1px solid {P.d_border}; border-radius: 12px; padding: 8px; }}
        QPushButton[primary="true"] {{ background: {P.red}; color: white; border: none; border-radius: 10px; padding: 9px 14px; font-weight: 600; }}
        QPushButton[ghost="true"] {{ background: transparent; color: {P.d_text}; border: 1px solid {P.d_border}; border-radius: 10px; padding: 9px 14px; }}
        QTableWidget {{ background: #171717; border: 1px solid {P.d_border}; border-radius: 10px; }}
        QHeaderView::section {{ background: #1E1E1E; border: 1px solid {P.d_border}; padding: 6px; color: {P.d_text}; }}
        QTabWidget::pane {{ border: none; }}
        QTabBar::tab {{ background: transparent; color: {P.d_text}; padding: 8px 12px; }}
        QTabBar::tab:selected {{ border-bottom: 2px solid {P.red}; }}
        """

# =============================
# Utilitarios de UI
# =============================
class VSpacer(QtWidgets.QWidget):
    def __init__(self, h=8):
        super().__init__()
        self.setFixedHeight(h)

class HLine(QtWidgets.QFrame):
    def __init__(self):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.setStyleSheet("color: #E5E5E5;")

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

# =============================
# Páginas (solo visual, con CSV en Contactos)
# =============================
class PageDashboard(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        row = QtWidgets.QHBoxLayout(); row.setSpacing(12)
        c1 = Card("Estado del equipo")
        grid = QtWidgets.QGridLayout(); grid.setVerticalSpacing(8)
        for i, (k, v) in enumerate([("Modelo","ALR-LTE"),("ID","A1B2C3"),("FW","1.0.0"),("Señal","- dBm")]):
            lk = QtWidgets.QLabel(k + ":"); lk.setProperty("muted", True)
            lv = QtWidgets.QLabel(v)
            grid.addWidget(lk, i, 0); grid.addWidget(lv, i, 1)
        c1.body.addLayout(grid)

        c2 = Card("Acciones rápidas")
        btnRow = QtWidgets.QHBoxLayout()
        for txt in ("Ping", "Info", "Guardar", "Reiniciar"):
            b = QtWidgets.QPushButton(txt); b.setProperty("ghost", True); btnRow.addWidget(b)
        c2.body.addLayout(btnRow)

        row.addWidget(c1, 1); row.addWidget(c2, 1)

        c3 = Card("Eventos recientes")
        self.events = QtWidgets.QTextEdit(); self.events.setReadOnly(True)
        self.events.setPlaceholderText("EVT,DEV,SEQ,TS,evento,k=v …")
        c3.body.addWidget(self.events)

        root.addLayout(row); root.addWidget(c3)

class PageContacts(QtWidgets.QWidget):
    """Diseño tipo Teltonika con colores Hunter — Import/Export CSV."""
    def __init__(self):
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        # Barra superior (Load/Save to file)
        topBar = QtWidgets.QHBoxLayout()
        self.btnLoad = QtWidgets.QPushButton("Cargar desde archivo…"); self.btnLoad.setProperty("ghost", True)
        self.btnSave = QtWidgets.QPushButton("Guardar a archivo…"); self.btnSave.setProperty("ghost", True)
        topBar.addWidget(self.btnLoad); topBar.addWidget(self.btnSave); topBar.addStretch(1)
        root.addLayout(topBar)

        mainRow = QtWidgets.QHBoxLayout(); mainRow.setSpacing(12)

        # ===== Columna izquierda =====
        left = QtWidgets.QVBoxLayout(); left.setSpacing(12)

        cSend = Card("Opciones de envío")
        grid = QtWidgets.QGridLayout(); grid.setVerticalSpacing(8)
        lblAllow = QtWidgets.QLabel("Permitir envío de reportes"); lblAllow.setProperty("muted", True)
        self.swAllow = QtWidgets.QComboBox(); self.swAllow.addItems(["Deshabilitar", "Habilitar"])  # switch visual
        grid.addWidget(lblAllow, 0, 0); grid.addWidget(self.swAllow, 0, 1)
        lblOrder = QtWidgets.QLabel("Orden de reporte"); lblOrder.setProperty("muted", True)
        self.cbOrder = QtWidgets.QComboBox(); self.cbOrder.addItems(["WP → Ubicación → Llamada", "WP → Llamada → Ubicación"]) 
        grid.addWidget(lblOrder, 1, 0); grid.addWidget(self.cbOrder, 1, 1)
        cSend.body.addLayout(grid)
        left.addWidget(cSend)

        cCall = Card("Llamada entrante")
        rowBtns = QtWidgets.QHBoxLayout()
        for txt in ("No hacer nada", "Colgar", "Reportar posición", "Auto-Respuesta"):
            b = QtWidgets.QPushButton(txt); b.setProperty("ghost", True); rowBtns.addWidget(b)
        cCall.body.addLayout(rowBtns)
        left.addWidget(cCall)

        cGroup = Card("Grupo / Alias")
        grpRow = QtWidgets.QHBoxLayout()
        self.grpName = QtWidgets.QLineEdit(); self.grpName.setPlaceholderText("Nombre del grupo (p.ej. ALARM_SMP)")
        self.grpSave = QtWidgets.QPushButton("Guardar"); self.grpSave.setProperty("primary", True)
        grpRow.addWidget(self.grpName, 1); grpRow.addWidget(self.grpSave)
        cGroup.body.addLayout(grpRow)
        left.addWidget(cGroup)

        mainRow.addLayout(left, 1)

        # ===== Columna derecha =====
        right = QtWidgets.QVBoxLayout(); right.setSpacing(12)

        # Números autorizados (20 filas)
        cAuth = Card("Números autorizados")
        self.tblAuth = QtWidgets.QTableWidget(20, 1)
        self.tblAuth.setHorizontalHeaderLabels(["Número (E.164)"])
        self.tblAuth.horizontalHeader().setStretchLastSection(True)
        self.tblAuth.verticalHeader().setVisible(True)
        self.tblAuth.verticalHeader().setDefaultAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.tblAuth.setShowGrid(False)
        for r in range(20):
            self.tblAuth.setItem(r, 0, QtWidgets.QTableWidgetItem(""))
        cAuth.body.addWidget(self.tblAuth)
        authBtns = QtWidgets.QHBoxLayout(); authBtns.addStretch(1)
        self.bImpA = QtWidgets.QPushButton("Importar CSV"); self.bImpA.setProperty("ghost", True)
        self.bExpA = QtWidgets.QPushButton("Exportar CSV"); self.bExpA.setProperty("ghost", True)
        authBtns.addWidget(self.bImpA); authBtns.addWidget(self.bExpA)
        cAuth.body.addLayout(authBtns)
        right.addWidget(cAuth)

        # Números predefinidos (10 filas, etiqueta + número)
        cGsm = Card("Números predefinidos")
        self.tblGsm = QtWidgets.QTableWidget(10, 2)
        self.tblGsm.setHorizontalHeaderLabels(["Etiqueta", "Número"]) 
        self.tblGsm.horizontalHeader().setStretchLastSection(True)
        self.tblGsm.verticalHeader().setVisible(True)
        self.tblGsm.setShowGrid(False)
        for r in range(10):
            self.tblGsm.setItem(r, 0, QtWidgets.QTableWidgetItem(""))
            self.tblGsm.setItem(r, 1, QtWidgets.QTableWidgetItem(""))
        cGsm.body.addWidget(self.tblGsm)
        gsmBtns = QtWidgets.QHBoxLayout(); gsmBtns.addStretch(1)
        self.bImpG = QtWidgets.QPushButton("Importar CSV"); self.bImpG.setProperty("ghost", True)
        self.bExpG = QtWidgets.QPushButton("Exportar CSV"); self.bExpG.setProperty("ghost", True)
        gsmBtns.addWidget(self.bImpG); gsmBtns.addWidget(self.bExpG)
        cGsm.body.addLayout(gsmBtns)
        right.addWidget(cGsm)

        mainRow.addLayout(right, 1)
        root.addLayout(mainRow)

        # === Conexiones CSV ===
        self.bImpA.clicked.connect(self.import_auth_csv)
        self.bExpA.clicked.connect(self.export_auth_csv)
        self.bImpG.clicked.connect(self.import_gsm_csv)
        self.bExpG.clicked.connect(self.export_gsm_csv)
        # Botones superiores (placeholder: podrías guardar todo el pack de contactos)
        self.btnLoad.clicked.connect(self.import_auth_csv)
        self.btnSave.clicked.connect(self.export_auth_csv)

    # ------- Helpers CSV -------
    def import_auth_csv(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Importar números autorizados", "", "CSV (*.csv)")
        if not path: return
        try:
            with open(path, newline='', encoding='utf-8') as f:
                rdr = csv.reader(f)
                rows = [r for r in rdr if any(cell.strip() for cell in r)]
            # acepta con o sin cabecera: si primera celda no es número, trátala como cabecera
            start = 1 if rows and rows[0] and not rows[0][0].strip().lstrip('+').isdigit() else 0
            nums = [rows[i][0].strip() if rows[i] else "" for i in range(start, min(start+20, len(rows)))]
            # volcar a la tabla
            for r in range(20):
                val = nums[r] if r < len(nums) else ""
                self.tblAuth.item(r,0).setText(val)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error CSV", str(e))

    def export_auth_csv(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Exportar números autorizados", "autorizados.csv", "CSV (*.csv)")
        if not path: return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(["number"])  # cabecera simple
                for r in range(20):
                    val = self.tblAuth.item(r,0).text().strip()
                    if val:
                        w.writerow([val])
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error CSV", str(e))

    def import_gsm_csv(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Importar números predefinidos", "", "CSV (*.csv)")
        if not path: return
        try:
            with open(path, newline='', encoding='utf-8') as f:
                rdr = csv.reader(f)
                rows = [r for r in rdr if any(cell.strip() for cell in r)]
            # cabecera opcional: si texto en columna 1 no parece etiqueta, igual aceptamos
            start = 1 if rows and rows[0] and (rows[0][0].lower() in ("label","etiqueta")) else 0
            pairs = []
            for i in range(start, min(start+10, len(rows))):
                lab = rows[i][0].strip() if len(rows[i])>0 else ""
                num = rows[i][1].strip() if len(rows[i])>1 else ""
                pairs.append((lab, num))
            for r in range(10):
                lab, num = pairs[r] if r < len(pairs) else ("", "")
                self.tblGsm.item(r,0).setText(lab)
                self.tblGsm.item(r,1).setText(num)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error CSV", str(e))

    def export_gsm_csv(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Exportar números predefinidos", "predefinidos.csv", "CSV (*.csv)")
        if not path: return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as f:
                w = csv.writer(f)
                w.writerow(["label","number"])  # cabecera
                for r in range(10):
                    lab = self.tblGsm.item(r,0).text().strip()
                    num = self.tblGsm.item(r,1).text().strip()
                    if lab or num:
                        w.writerow([lab, num])
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "Error CSV", str(e))

class PageAudio(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        root = QtWidgets.QVBoxLayout(self); root.setContentsMargins(16,16,16,16); root.setSpacing(12)
        c = Card("Audio (placeholder)")
        c.body.addWidget(QtWidgets.QLabel("Próximamente controles de AUDIO.PLAY y subida BLOB"))
        root.addWidget(c)

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
        for i,(k,v) in enumerate([("Baudios","115200"),("Firma","QC1"),("Modelo","ALR-LTE"),("Dev ID","A1B2C3")]):
            l = QtWidgets.QLabel(k); l.setProperty("muted", True)
            e = QtWidgets.QLineEdit(v)
            grid.addWidget(l, i, 0); grid.addWidget(e, i, 1)
        c.body.addLayout(grid)
        row = QtWidgets.QHBoxLayout(); row.addStretch(1)
        bDefaults = QtWidgets.QPushButton("Restaurar fábrica"); bDefaults.setProperty("ghost", True)
        bSave = QtWidgets.QPushButton("Guardar NVS"); bSave.setProperty("primary", True)
        row.addWidget(bDefaults); row.addWidget(bSave)
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

# =============================
# Ventana principal: toggle de tema
# =============================
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configurador QC1 — Hunter")
        self.resize(1180, 740)
        self.setWindowIcon(QtGui.QIcon())

        self.theme = 'light'

        central = QtWidgets.QWidget(); self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central); layout.setContentsMargins(0,0,0,0); layout.setSpacing(0)

        layout.addWidget(self._make_topbar())
        body = QtWidgets.QHBoxLayout(); body.setContentsMargins(0,0,0,0); body.setSpacing(0)
        layout.addLayout(body, 1)

        self.side = self._make_sidebar(); body.addWidget(self.side)

        self.pages = QtWidgets.QStackedWidget()
        self.page_map = {
            "Dashboard": PageDashboard(),
            "Contactos": PageContacts(),
            "Audio": PageAudio(),
            "Servidor": PageServer(),
            "Sistema": PageSystem(),
            "Logs": PageLogs(),
        }
        for w in self.page_map.values():
            self.pages.addWidget(w)
        body.addWidget(self.pages, 1)

        self._set_active("Contactos")
        self.apply_theme()

    def _make_topbar(self) -> QtWidgets.QWidget:
        top = QtWidgets.QFrame(); top.setObjectName("TopBar")
        lay = QtWidgets.QHBoxLayout(top); lay.setContentsMargins(14,10,14,10)
        title = QtWidgets.QLabel("Configurador QC1") ; title.setObjectName("TopTitle")
        sub = QtWidgets.QLabel("PyQt6 — tema claro/oscuro + CSV") ; sub.setObjectName("TopSubtitle")
        box = QtWidgets.QVBoxLayout(); box.setSpacing(0)
        box.addWidget(title); box.addWidget(sub)
        lay.addLayout(box); lay.addStretch(1)
        # Toggle tema
        self.btnTheme = QtWidgets.QPushButton("Oscuro")
        self.btnTheme.setCheckable(True)
        self.btnTheme.setProperty("ghost", True)
        self.btnTheme.toggled.connect(self.toggle_theme)
        # Puerto/Conectar (placeholder)
        port = QtWidgets.QComboBox(); port.addItems(["/dev/ttyUSB0", "COM3", "COM7"]) ; port.setFixedWidth(160)
        btn = QtWidgets.QPushButton("Conectar"); btn.setProperty("primary", True)
        lay.addWidget(self.btnTheme); lay.addWidget(port); lay.addWidget(btn)
        return top

    def _make_sidebar(self) -> QtWidgets.QWidget:
        side = QtWidgets.QFrame(); side.setObjectName("SideBar")
        lay = QtWidgets.QVBoxLayout(side); lay.setContentsMargins(12,12,12,12); lay.setSpacing(8)
        logo = QtWidgets.QLabel("🛡️ Hunter"); logo.setStyleSheet("font-weight:700; font-size:16px;")
        lay.addWidget(logo); lay.addWidget(VSpacer(8))
        for name in ["Dashboard", "Contactos", "Audio", "Servidor", "Sistema", "Logs"]:
            b = QtWidgets.QPushButton(name); b.setProperty("sideBtn", True)
            b.clicked.connect(lambda _, n=name: self._set_active(n))
            lay.addWidget(b)
        lay.addStretch(1)
        foot = QtWidgets.QLabel("v1.0.0") ; foot.setProperty("muted", True)
        lay.addWidget(foot)
        return side

    def _set_active(self, name: str):
        idx = list(self.page_map.keys()).index(name)
        self.pages.setCurrentIndex(idx)
        for i in range(self.side.layout().count()):
            w = self.side.layout().itemAt(i).widget()
            if isinstance(w, QtWidgets.QPushButton) and w.property("sideBtn"):
                w.setProperty("active", w.text() == name)
                w.style().unpolish(w); w.style().polish(w)

    # ===== Theme API =====
    def apply_theme(self):
        qss = Styles.light() if self.theme == 'light' else Styles.dark()
        QtWidgets.QApplication.instance().setStyleSheet(qss)
        self.btnTheme.setText("Oscuro" if self.theme=='light' else "Claro")

    def toggle_theme(self, checked: bool):
        self.theme = 'dark' if checked else 'light'
        self.apply_theme()

# =============================
# main
# =============================
if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    app.setStyle("Fusion")
    w = MainWindow(); w.show()
    sys.exit(app.exec())
