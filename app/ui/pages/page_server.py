from PyQt6 import QtWidgets

from app.ui.widgets.card import Card


class PageServer(QtWidgets.QWidget):
    """Server connection parameters form."""

    def __init__(self) -> None:
        super().__init__()
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        card = Card("Servidor de reporte")
        form = QtWidgets.QGridLayout()
        form.setVerticalSpacing(8)

        labels = [
            "Modo",
            "Host",
            "Puerto",
            "TLS",
            "Usuario",
            "Clave",
            "Topic pub",
            "Topic sub",
        ]
        widgets: list[QtWidgets.QWidget] = [
            QtWidgets.QComboBox(),
            QtWidgets.QLineEdit(),
            QtWidgets.QSpinBox(),
            QtWidgets.QComboBox(),
            QtWidgets.QLineEdit(),
            QtWidgets.QLineEdit(),
            QtWidgets.QLineEdit(),
            QtWidgets.QLineEdit(),
        ]

        mode_widget = widgets[0]
        if isinstance(mode_widget, QtWidgets.QComboBox):
            mode_widget.addItems(["MQTT", "TCP", "UDP", "HTTP"])
        tls_widget = widgets[3]
        if isinstance(tls_widget, QtWidgets.QComboBox):
            tls_widget.addItems(["0", "1"])
        port_widget = widgets[2]
        if isinstance(port_widget, QtWidgets.QSpinBox):
            port_widget.setRange(1, 65535)
            port_widget.setValue(1883)

        for row, (label, widget) in enumerate(zip(labels, widgets)):
            lbl = QtWidgets.QLabel(label)
            lbl.setProperty("muted", True)
            form.addWidget(lbl, row, 0)
            form.addWidget(widget, row, 1)

        buttons = QtWidgets.QHBoxLayout()
        buttons.addStretch(1)
        btn_test = QtWidgets.QPushButton("Probar")
        btn_test.setProperty("ghost", True)
        btn_save = QtWidgets.QPushButton("Guardar")
        btn_save.setProperty("primary", True)
        buttons.addWidget(btn_test)
        buttons.addWidget(btn_save)

        card.body.addLayout(form)
        card.body.addLayout(buttons)
        root.addWidget(card)
