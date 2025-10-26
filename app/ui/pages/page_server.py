from __future__ import annotations

from typing import Dict, List

from PyQt6 import QtWidgets

from app.ui.widgets.card import Card


class PageServer(QtWidgets.QWidget):
    """Layout de configuracion de servidores y APN."""

    def __init__(self) -> None:
        super().__init__()
        self._toggle_groups: Dict[str, QtWidgets.QButtonGroup] = {}

        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        cards_grid = QtWidgets.QGridLayout()
        cards_grid.setSpacing(12)
        root.addLayout(cards_grid)

        cards_grid.addWidget(self._build_gprs_card(), 0, 0)
        cards_grid.addWidget(self._build_primary_server_card(), 0, 1)
        cards_grid.addWidget(self._build_auto_apn_card(), 1, 0)
        cards_grid.addWidget(self._build_secondary_server_card(), 1, 1)
        cards_grid.setColumnStretch(0, 1)
        cards_grid.setColumnStretch(1, 1)

        actions = QtWidgets.QHBoxLayout()
        actions.addStretch(1)
        self.btn_ping = QtWidgets.QPushButton("Probar enlace")
        self.btn_ping.setProperty("ghost", True)
        self.btn_ping.setToolTip("Envio rapido de ping o handshake al servidor principal.")
        self.btn_save = QtWidgets.QPushButton("Guardar cambios")
        self.btn_save.setProperty("primary", True)
        self.btn_save.setToolTip("Aplica y persiste todos los parametros de conectividad.")
        actions.addWidget(self.btn_ping)
        actions.addWidget(self.btn_save)
        root.addLayout(actions)

        root.addStretch(1)

    # ------------------------------------------------------------------
    #  Tarjetas
    # ------------------------------------------------------------------
    def _build_gprs_card(self) -> Card:
        card = Card("Conexion GPRS")
        grid = QtWidgets.QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        grid.addWidget(self._muted_label("Contexto GPRS"), 0, 0)
        grid.addWidget(self._build_toggle("gprs_context", ["Desactivar", "Activar"], 1), 0, 1)

        grid.addWidget(self._muted_label("APN"), 1, 0)
        self.input_apn = QtWidgets.QLineEdit()
        self.input_apn.setPlaceholderText("internet.claro.com")
        grid.addWidget(self.input_apn, 1, 1)

        grid.addWidget(self._muted_label("Usuario APN"), 2, 0)
        self.input_apn_user = QtWidgets.QLineEdit()
        grid.addWidget(self.input_apn_user, 2, 1)

        grid.addWidget(self._muted_label("Clave APN"), 3, 0)
        self.input_apn_pass = QtWidgets.QLineEdit()
        self.input_apn_pass.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        grid.addWidget(self.input_apn_pass, 3, 1)

        grid.addWidget(self._muted_label("Limitar errores"), 4, 0)
        grid.addWidget(self._build_toggle("gprs_limit", ["Permitir", "Limitar"], 1), 4, 1)

        grid.addWidget(self._muted_label("Autenticacion"), 5, 0)
        grid.addWidget(self._build_toggle("gprs_auth", ["Ninguna", "Normal (PAP)", "Segura (CHAP)"], 1), 5, 1)

        card.body.addLayout(grid)
        return card

    def _build_auto_apn_card(self) -> Card:
        card = Card("Auto APN")
        grid = QtWidgets.QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        grid.addWidget(self._muted_label("Busqueda automatica"), 0, 0)
        grid.addWidget(self._build_toggle("auto_apn", ["Desactivar", "Activar"], 1), 0, 1)

        grid.addWidget(self._muted_label("Archivo de base"), 1, 0)
        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)
        self.lbl_apn_file = QtWidgets.QLabel("Sin archivo seleccionado")
        self.lbl_apn_file.setProperty("muted", True)
        self.btn_apn_upload = QtWidgets.QPushButton("Subir archivo")
        self.btn_apn_upload.setProperty("ghost", True)
        self.btn_apn_upload.setToolTip("Selecciona un archivo CSV/XML con perfiles APN.")
        row.addWidget(self.lbl_apn_file, 1)
        row.addWidget(self.btn_apn_upload, 0)
        grid.addLayout(row, 1, 1)

        card.body.addLayout(grid)
        return card

    def _build_primary_server_card(self) -> Card:
        card = Card("Servidor principal")
        grid = QtWidgets.QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        grid.addWidget(self._muted_label("Dominio / IP"), 0, 0)
        self.input_domain = QtWidgets.QLineEdit()
        self.input_domain.setPlaceholderText("srv.alarmas.com")
        self.input_domain.setToolTip("Direccion del servidor principal donde reporta la central.")
        grid.addWidget(self.input_domain, 0, 1)

        grid.addWidget(self._muted_label("Puerto"), 1, 0)
        self.input_port = QtWidgets.QSpinBox()
        self.input_port.setRange(1, 65535)
        self.input_port.setValue(1883)
        self.input_port.setToolTip("Puerto asociado al servicio remoto.")
        grid.addWidget(self.input_port, 1, 1)

        grid.addWidget(self._muted_label("Protocolo"), 2, 0)
        grid.addWidget(self._build_toggle("primary_protocol", ["TCP", "UDP", "MQTT"], 0), 2, 1)

        grid.addWidget(self._muted_label("Cifrado TLS"), 3, 0)
        grid.addWidget(self._build_toggle("primary_tls", ["Ninguno", "TLS/DTLS"], 0), 3, 1)

        grid.addWidget(self._muted_label("Usuario"), 4, 0)
        self.input_user = QtWidgets.QLineEdit()
        self.input_user.setToolTip("Usuario para autenticacion del enlace principal.")
        grid.addWidget(self.input_user, 4, 1)

        grid.addWidget(self._muted_label("Clave"), 5, 0)
        self.input_pass = QtWidgets.QLineEdit()
        self.input_pass.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self.input_pass.setToolTip("Clave o token para el usuario configurado.")
        grid.addWidget(self.input_pass, 5, 1)

        grid.addWidget(self._muted_label("Topic publicacion"), 6, 0)
        self.input_topic_pub = QtWidgets.QLineEdit()
        self.input_topic_pub.setToolTip("Topic MQTT donde se publican los eventos (opcional).")
        grid.addWidget(self.input_topic_pub, 6, 1)

        grid.addWidget(self._muted_label("Topic suscripcion"), 7, 0)
        self.input_topic_sub = QtWidgets.QLineEdit()
        self.input_topic_sub.setToolTip("Topic MQTT para comandos entrantes (opcional).")
        grid.addWidget(self.input_topic_sub, 7, 1)

        card.body.addLayout(grid)
        return card

    def _build_secondary_server_card(self) -> Card:
        card = Card("Servidor secundario")
        grid = QtWidgets.QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(8)

        grid.addWidget(self._muted_label("Modo"), 0, 0)
        grid.addWidget(self._build_toggle("secondary_mode", ["Deshabilitado", "Backup", "Duplicado"], 0), 0, 1)

        grid.addWidget(self._muted_label("Dominio / IP"), 1, 0)
        self.input_domain_secondary = QtWidgets.QLineEdit()
        self.input_domain_secondary.setToolTip("Servidor alterno para contingencia o duplicacion.")
        grid.addWidget(self.input_domain_secondary, 1, 1)

        grid.addWidget(self._muted_label("Puerto"), 2, 0)
        self.input_port_secondary = QtWidgets.QSpinBox()
        self.input_port_secondary.setRange(1, 65535)
        self.input_port_secondary.setToolTip("Puerto del servidor secundario.")
        grid.addWidget(self.input_port_secondary, 2, 1)

        grid.addWidget(self._muted_label("Protocolo"), 3, 0)
        grid.addWidget(self._build_toggle("secondary_protocol", ["TCP", "UDP", "MQTT"], 0), 3, 1)

        grid.addWidget(self._muted_label("Cifrado TLS"), 4, 0)
        grid.addWidget(self._build_toggle("secondary_tls", ["Ninguno", "TLS/DTLS"], 0), 4, 1)

        card.body.addLayout(grid)
        return card

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------
    def _muted_label(self, text: str) -> QtWidgets.QLabel:
        label = QtWidgets.QLabel(text)
        label.setProperty("muted", True)
        return label

    def _build_toggle(
        self,
        key: str,
        options: List[str],
        default_index: int = 0,
    ) -> QtWidgets.QWidget:
        container = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        group = QtWidgets.QButtonGroup(self)
        group.setExclusive(True)

        for idx, label in enumerate(options):
            btn = QtWidgets.QPushButton(label)
            btn.setCheckable(True)
            btn.setChecked(idx == default_index)
            btn.setProperty("segmented", True)
            btn.setMinimumWidth(72)
            group.addButton(btn, idx)
            layout.addWidget(btn)

        layout.addStretch(1)
        self._toggle_groups[key] = group
        return container


__all__ = ["PageServer"]
