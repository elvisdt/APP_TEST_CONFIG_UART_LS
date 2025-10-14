from __future__ import annotations

from typing import Optional, Dict, Any, List
from PyQt6.QtCore import QObject, QTimer, pyqtSignal, QIODevice
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo


class SerialManager(QObject):
    """
    Gestor de puerto serial robusto y eficiente con PyQt6.
    - Escanea puertos automÃ¡ticamente.
    - ConexiÃ³n automÃ¡tica y reconexiÃ³n opcional.
    - SeÃ±ales para comunicaciÃ³n con GUI o lÃ³gica de backend.
    - Cierre seguro del COM (flush/clear/wait + bajar DTR/RTS + deleteLater()).
    """

    # SeÃ±ales Qt
    data_received = pyqtSignal(bytes, str)           # datos, puerto
    data_sent = pyqtSignal(bytes, str)               # datos, puerto
    error_occurred = pyqtSignal(str, str)            # mensaje, puerto
    connection_changed = pyqtSignal(bool, str)       # estado, puerto
    ports_updated = pyqtSignal(list)                 # lista de puertos

    # ConfiguraciÃ³n por defecto
    DEFAULT_SETTINGS: Dict[str, Any] = {
        'baud_rate': 115200,
        'data_bits': QSerialPort.DataBits.Data8,
        'parity': QSerialPort.Parity.NoParity,
        'stop_bits': QSerialPort.StopBits.OneStop,
        'flow_control': QSerialPort.FlowControl.NoFlowControl,
    }

    # Mapa de errores comunes
    ERROR_MAP: Dict[QSerialPort.SerialPortError, str] = {
        QSerialPort.SerialPortError.DeviceNotFoundError: "Dispositivo no encontrado",
        QSerialPort.SerialPortError.PermissionError: "Permiso denegado",
        QSerialPort.SerialPortError.OpenError: "Error al abrir puerto",
        QSerialPort.SerialPortError.WriteError: "Error de escritura",
        QSerialPort.SerialPortError.ReadError: "Error de lectura",
        QSerialPort.SerialPortError.ResourceError: "Puerto desconectado",
        QSerialPort.SerialPortError.UnsupportedOperationError: "OperaciÃ³n no soportada",
        QSerialPort.SerialPortError.TimeoutError: "Timeout",
        QSerialPort.SerialPortError.NotOpenError: "Puerto no abierto",
    }

    def __init__(self, scan_interval_ms: int = 2000):
        super().__init__()
        self.serial: Optional[QSerialPort] = None
        self.port_name: str = ""
        self._last_ports: List[str] = []
        self._scan_interval_ms = scan_interval_ms
        self._shutting_down = False

        self._scan_timer = QTimer(self)
        self._scan_timer.timeout.connect(self._scan_ports)
        self._scan_timer.start(self._scan_interval_ms)

    # QObjects y __del__ no son confiables, pero lo dejamos de red de seguridad
    def __del__(self):
        try:
            self.shutdown()
        except Exception:
            pass

    # --- ESCANEO DE PUERTOS ---

    def _scan_ports(self):
        ports = self.get_list_ports()
        if ports != self._last_ports:
            self._last_ports = ports
            self.ports_updated.emit(ports)
        self._try_reconnect()

    def get_list_ports(self) -> list:
        """Devuelve los nombres de los puertos disponibles."""
        return [port.portName() for port in QSerialPortInfo.availablePorts()]

    def get_port_info(self, port_name: str) -> Dict[str, Any]:
        """Devuelve informaciÃ³n detallada de un puerto."""
        for port in QSerialPortInfo.availablePorts():
            if port.portName() == port_name:
                return {
                    'description': port.description(),
                    'manufacturer': port.manufacturer(),
                    'serial_number': port.serialNumber(),
                    'vendor_id': port.vendorIdentifier(),
                    'product_id': port.productIdentifier(),
                    'system_location': port.systemLocation()
                }
        return {}

    # --- CONEXIÃ“N ---

    def open_port(self, port_name: str, settings: Optional[Dict[str, Any]] = None) -> bool:
        """Abre un puerto con los ajustes dados o por defecto. Devuelve True/False."""
        if self.serial is None:
            self.serial = QSerialPort()
            self.serial.readyRead.connect(self._handle_ready_read)
            self.serial.errorOccurred.connect(self._handle_error)
        elif self.serial.isOpen():
            self.close_port()

        self.serial.setPortName(port_name)
        self.port_name = port_name
        config = {**self.DEFAULT_SETTINGS, **(settings or {})}

        self.serial.setBaudRate(config['baud_rate'])
        self.serial.setDataBits(config['data_bits'])
        self.serial.setParity(config['parity'])
        self.serial.setStopBits(config['stop_bits'])
        self.serial.setFlowControl(config['flow_control'])

        ok = self.serial.open(QIODevice.OpenModeFlag.ReadWrite)
        if ok:
            self.connection_changed.emit(True, port_name)
            self._scan_timer.stop()
            return True
        else:
            self.error_occurred.emit(f"Error al abrir {port_name}", port_name)
            try:
                self.serial.close()
            except Exception:
                pass
            return False

    def close_port(self, _restart_scan: bool = True):
        """Cierra el puerto si estÃ¡ abierto y limpia correctamente."""
        if self.serial:
            try:
                # Evita callbacks durante cierre
                try:
                    self.serial.readyRead.disconnect(self._handle_ready_read)
                except Exception:
                    pass
                try:
                    self.serial.errorOccurred.disconnect(self._handle_error)
                except Exception:
                    pass

                if self.serial.isOpen():
                    try:
                        self.serial.setDataTerminalReady(False)
                    except Exception:
                        pass
                    try:
                        self.serial.setRequestToSend(False)
                    except Exception:
                        pass
                    try:
                        self.serial.flush()
                    except Exception:
                        pass
                    # Limpia buffers RX/TX (segÃºn disponibilidad de firma)
                    try:
                        self.serial.clear(QSerialPort.Direction.AllDirections)
                    except Exception:
                        try:
                            self.serial.clear()
                        except Exception:
                            pass
                    try:
                        self.serial.waitForBytesWritten(150)
                    except Exception:
                        pass

                    port_name = self.port_name
                    self.serial.close()
                    self.connection_changed.emit(False, port_name)
            finally:
                try:
                    self.serial.deleteLater()
                except Exception:
                    pass
                self.serial = None
                self.port_name = ""

        if _restart_scan and not self._shutting_down:
            self._scan_timer.start(self._scan_interval_ms)

    def restart_connection(self):
        """Reabre el puerto actual, si existe."""
        if self.port_name:
            self.open_port(self.port_name)

    def auto_connect(self):
        """Se conecta automÃ¡ticamente al primer puerto 'vÃ¡lido' y se detiene."""
        ports = self.get_list_ports()
        if not ports:
            self.error_occurred.emit("No hay puertos disponibles", "")
            return
        
        blacklist = ("INTEL", "BLUETOOTH")
        prefer = ("USB", "CH340", "CP210", "FTDI", "SILABS", "PROLIFIC")

        # 1) prioriza los que parezcan USB-Serial, 2) el resto
        ordered = sorted(
            ports,
            key=lambda p: (
                0 if any(k in (self.get_port_info(p).get('description') or '').upper() for k in prefer) else 1
            )
        )

        for port in ordered:
            try:
                info = self.get_port_info(port)
                desc = (info.get('description') or '').upper()
                if any(b in desc for b in blacklist):
                    continue
                if self.open_port(port):
                    return
            except Exception as e:
                self.error_occurred.emit(f"Error analizando {port}: {e}", port)
        self.error_occurred.emit("No se pudo abrir ningÃºn puerto", "")



    def _try_reconnect(self):
        """Reconecta automÃ¡ticamente si el puerto reaparece."""
        if not self.is_connected() and self.port_name:
            available = self.get_list_ports()
            if self.port_name in available:
                self.open_port(self.port_name)

    # --- ESTADO ---
    def is_connected(self) -> bool:
        return self.serial is not None and self.serial.isOpen()

    def get_port_name(self) -> str:
        return self.port_name or ""

    def get_current_settings(self) -> Dict[str, Any]:
        if not self.is_connected():
            return {}
        return {
            'baud_rate': self.serial.baudRate(),
            'data_bits': self.serial.dataBits(),
            'parity': self.serial.parity(),
            'stop_bits': self.serial.stopBits(),
            'flow_control': self.serial.flowControl()
        }

    # --- ENVÃO ---

    def send_data_bytes(self, data: bytes) -> None:
        """EnvÃ­a datos en bytes (sin modificar)."""
        if not self.serial or not self.serial.isOpen():
            return
        n = self.serial.write(data)
        if n == -1:
            self.error_occurred.emit("Error al escribir datos", self.port_name)
            return
        try:
            self.serial.waitForBytesWritten(100)  # asegurar salida
        except Exception:
            pass
        if n == len(data):
            self.data_sent.emit(data, self.port_name)
        else:
            self.error_occurred.emit(f"Datos enviados parcialmente ({n}/{len(data)})", self.port_name)

    def send_data_str(self, data: str) -> None:
        """EnvÃ­a datos como string (con `\\n` si falta)."""
        if not data.endswith('\n'):
            data += '\n'
        self.send_data_bytes(data.encode('utf-8'))

    # --- RECEPCIÃ“N ---

    def _handle_ready_read(self):
        if self.serial and self.serial.isOpen():
            data = bytes(self.serial.readAll())
            if data:
                self.data_received.emit(data, self.port_name)

    # --- ERRORES ---

    def _handle_error(self, error):
        if error == QSerialPort.SerialPortError.NoError:
            return

        error_msg = self.ERROR_MAP.get(error, f"Error desconocido ({error})")
        self.error_occurred.emit(error_msg, self.port_name)

        if error in (QSerialPort.SerialPortError.ResourceError,
                     QSerialPort.SerialPortError.DeviceNotFoundError):
            self.close_port()

    # --- APAGADO GLOBAL ---

    def shutdown(self):
        """Cierra y destruye recursos sin reactivar el escaneo."""
        self._shutting_down = True
        try:
            self._scan_timer.stop()
        except Exception:
            pass
        self.close_port(_restart_scan=False)
