from __future__ import annotations

import json
from datetime import datetime
from typing import Any

from PyQt6 import QtCore, QtWidgets

from app.comm import SerialManager
from app.core.settings import Settings
from app.ui.main_window import MainWindow


class DeviceController(QtCore.QObject):
    """Une la UI con el backend QC1 sobre serial."""

    def __init__(self, win: MainWindow, settings: Settings):
        super().__init__()
        self.win = win
        self.settings = settings

        self.serial = SerialManager()
        # Comandos serial deshabilitados temporalmente mientras se ajusta la UI.
        self._commands_enabled = False

        self.logs = None
        self._bind_topbar()
        self._bind_pages()
        self.serial.ports_updated.connect(self._on_ports_updated)
        self.serial.connection_changed.connect(self._on_connection_changed)
        self.serial.error_occurred.connect(self._on_transport_error)

    # ------------------------------------------------------------------
    def _bind_topbar(self) -> None:
        self.win.topbar.connectRequested.connect(self._on_connect_requested)
        ports = self.serial.get_list_ports() or [self.settings.last_port]
        combo = self.win.topbar.port_combo
        combo.clear()
        combo.addItems(ports)
        combo.setCurrentText(self.settings.last_port)
        if hasattr(self.win.topbar, "set_connection_state"):
            self.win.topbar.set_connection_state(False, None)

    def _bind_pages(self) -> None:
        dashboard = self.win.page("Dashboard")
        if dashboard and hasattr(dashboard, "sig_shortcut_requested"):
            dashboard.sig_shortcut_requested.connect(self.win._on_page_requested)  # type: ignore[attr-defined]

        logs_page = self.win.page("Logs")
        if logs_page and hasattr(logs_page, "append_line"):
            self.logs = logs_page
            if hasattr(logs_page, "sig_send_command"):
                logs_page.sig_send_command.connect(self._send_manual_command)

        automation = self.win.page("Automatizacion")
        if automation:
            if hasattr(automation, "sig_apply_outputs"):
                automation.sig_apply_outputs.connect(self._apply_outputs)
            if hasattr(automation, "sig_apply_triggers"):
                automation.sig_apply_triggers.connect(self._apply_triggers)
            if hasattr(automation, "sig_trigger_output"):
                automation.sig_trigger_output.connect(self._trigger_output)

        audio = self.win.page("Audio")
        if audio:
            audio.sig_refresh_slots.connect(lambda: self._send_simple("AUDIO.SLOTS?"))
            audio.sig_control_slot.connect(self._control_audio)
            audio.sig_stop_all.connect(lambda: self._send("AUDIO.PLAY", ["ALL", "OFF"], {}))
            audio.sig_upload_audio.connect(self._upload_audio)

        notifications = self.win.page("Notificaciones")
        if notifications:
            notifications.sig_channels_changed.connect(self._set_channels)
            notifications.sig_groups_changed.connect(self._set_groups)
            notifications.sig_group_test.connect(self._test_group)
            notifications.sig_templates_saved.connect(self._set_templates)

        server = self.win.page("Servidor")
        if server:
            buttons = server.findChildren(QtWidgets.QPushButton)
            for btn in buttons:
                label = btn.text().lower()
                if label.startswith("guardar"):
                    btn.clicked.connect(lambda _, w=server: self._save_server_form(w))
                elif label.startswith("probar"):
                    btn.clicked.connect(lambda _, w=server: self._test_server_form(w))

        contacts = self.win.page("Contactos")
        if contacts and hasattr(contacts, "btn_save"):
            contacts.btn_save.clicked.connect(lambda: self._push_contacts(contacts))
        if contacts and hasattr(contacts, "sig_rf_scan"):
            contacts.sig_rf_scan.connect(self._scan_rf_remote)
        if contacts and hasattr(contacts, "sig_rf_link"):
            contacts.sig_rf_link.connect(self._link_rf_contact)

    # ------------------------------------------------------------------
    def _on_connect_requested(self, port: str) -> None:
        if self.serial.is_connected() and self.serial.get_port_name() == port:
            self.serial.close_port()
            return
        if not port:
            self._log("[serial] Selecciona un puerto")
            return
        if self.serial.open_port(port):
            self.settings.last_port = port
            self.settings.save("app/data/settings.json")
        else:
            self._log(f"[serial] No se pudo abrir {port}")

    def _on_ports_updated(self, ports: list[str]) -> None:
        combo = self.win.topbar.port_combo
        block = combo.blockSignals(True)
        combo.clear()
        combo.addItems(ports)
        if self.serial.get_port_name() in ports:
            combo.setCurrentText(self.serial.get_port_name())
        elif ports:
            combo.setCurrentIndex(0)
        combo.blockSignals(block)
        if hasattr(self.win.topbar, "set_ports"):
            self.win.topbar.set_ports(ports, self.serial.get_port_name())

    def _on_connection_changed(self, connected: bool, port: str) -> None:
        if hasattr(self.win.topbar, "set_connection_state"):
            self.win.topbar.set_connection_state(connected, port)
        text = f"Conectado a {port}" if connected else "Desconectado"
        self._log(f"[serial] {text}")

    def _on_transport_error(self, message: str, port: str) -> None:
        self._log(f"[serial] {message} ({port})")

    # ------------------------------------------------------------------
    def _send_simple(self, name: str) -> None:
        self._send(name, [], {})

    def _send(self, command_name: str, positional: list[str], keyword: dict[str, str]) -> None:
        if not self._commands_enabled:
            self._log(f"[serial] Comando '{command_name}' omitido (serial deshabilitado).")
            return

    # Automatización
    def _apply_outputs(self, rows: list[dict[str, Any]]) -> None:
        self._send("IO.OUTPUT.MAP", [], {"MAP": json.dumps(rows)})

    def _apply_triggers(self, rows: list[dict[str, Any]]) -> None:
        self._send("IO.TRIGGER.SET", [], {"LIST": json.dumps(rows)})

    def _apply_schedules(self, sched: list[dict[str, Any]]) -> None:
        self._send("IO.SCHEDULE.SET", [], {"LIST": json.dumps(sched)})

    def _trigger_output(self, name: str, action: str) -> None:
        self._send("IO.OUTPUT.TRIGGER", [name], {"ACTION": action.upper()})

    # Audio
    def _control_audio(self, slot: int, action: str, duration: int, loop: bool) -> None:
        action = action.lower()
        mapped = {
            "play": "ON",
            "stop": "OFF",
            "test": "ON",
        }.get(action, "ON")
        kv: dict[str, str] = {}
        if mapped == "ON":
            kv["DUR"] = str(duration)
            if loop and action == "play":
                kv["LOOP"] = "1"
        self._send("AUDIO.PLAY", [str(slot), mapped], kv)

    def _upload_audio(self, slot: int, path: str, encrypt: bool) -> None:
        self._log(f"[audio] Subida diferida: slot={slot} path={path} enc={encrypt}")

    # Notificaciones
    def _set_channels(self, flags: dict[str, object]) -> None:
        kv = {key.upper(): "1" if bool(value) else "0" for key, value in flags.items()}
        self._send("NTF.CHANNEL.SET", [], kv)

    def _set_groups(self, groups: list[dict[str, str]]) -> None:
        self._send("CONTACT.GROUP.BULK", [], {"LIST": json.dumps(groups)})

    def _test_group(self, data: dict[str, str]) -> None:
        group = data.get("name", "")
        self._send("CONTACT.GROUP.TEST", [group], {})

    def _set_templates(self, templates: dict[str, str]) -> None:
        for name, body in templates.items():
            self._send("NTF.TEMPLATE.SET", [name], {"BODY": body})

    # Contactos
    def _push_contacts(self, page) -> None:
        numbers = page.read_auth()
        self._send("CONTACT.AUTH.SET", [], {"LIST": ";".join(numbers)})

    def _scan_rf_remote(self) -> None:
        self._log("[rf] Escaneo solicitado.")
        page = self.win.page("Contactos")
        if page and hasattr(page, "rf_scan_finished"):
            page.rf_scan_finished(False, "Función no disponible con serial deshabilitado.")

    def _link_rf_contact(self, rf_id: str, contact: str) -> None:
        self._log(f"[rf] Vincular {rf_id} -> {contact}")
        self._send("RF.CONTACT.LINK", [rf_id], {"CONTACT": contact})
        page = self.win.page("Contactos")
        if page and hasattr(page, "append_rf_entry"):
            page.append_rf_entry(rf_id, contact)

    # Servidor
    def _save_server_form(self, page) -> None:
        fields = self._extract_form(page)
        if fields:
            self._send("SRV.MQTT.SET", [], fields)

    def _test_server_form(self, page) -> None:
        self._send("SRV.MQTT.TEST", [], {})

    def _extract_form(self, page) -> dict[str, str]:
        fields: dict[str, str] = {}
        combos = page.findChildren(QtWidgets.QComboBox)
        line_edits = page.findChildren(QtWidgets.QLineEdit)
        spins = page.findChildren(QtWidgets.QSpinBox)
        if combos:
            fields["MODE"] = combos[0].currentText()
            if len(combos) > 1:
                fields["TLS"] = combos[1].currentText()
        if spins:
            fields["PORT"] = str(spins[0].value())
        mapping = ["HOST", "USER", "PASS", "TOPIC_UP", "TOPIC_DOWN"]
        for key, widget in zip(mapping, line_edits):
            fields[key] = widget.text().strip()
        return fields

    # ------------------------------------------------------------------
    def _send_manual_command(self, command: str) -> None:
        raw = command.strip()
        if not raw:
            return
        if not self.serial.is_connected():
            self._log("[serial] No hay un puerto conectado; comando ignorado.")
            return
        self._log(f"[serial] >> {raw}")
        try:
            self.serial.send_data_str(raw)
        except Exception as exc:
            self._log(f"[serial] Error enviando '{raw}': {exc}")

    # ------------------------------------------------------------------
    def _log(self, text: str) -> None:
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] {text}"
        if self.logs and hasattr(self.logs, "append_line"):
            self.logs.append_line(line)
        else:
            print(line)
