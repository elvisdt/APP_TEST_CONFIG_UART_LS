from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, Optional

from PyQt6 import QtCore

from app.core import qc1_proto

from . import codec, registry
from .models import CommandFrame, CommandSpec, FrameHeader, PendingCommand, ResponseEnvelope
from .serial_manager import SerialManager

PasswordProvider = Callable[[CommandSpec], Optional[str]]
TimestampProvider = Callable[[], int]


@dataclass
class _PendingEntry:
    command: PendingCommand
    timer: QtCore.QTimer


class SerialCommandService(QtCore.QObject):
    """Orquesta el envío/recepción de comandos QC1 sobre SerialManager."""

    frame_sent = QtCore.pyqtSignal(CommandFrame, str)
    raw_sent = QtCore.pyqtSignal(str)
    response_received = QtCore.pyqtSignal(ResponseEnvelope)
    packet_received = QtCore.pyqtSignal(qc1_proto.QC1Packet)
    parse_failed = QtCore.pyqtSignal(str)
    transport_error = QtCore.pyqtSignal(str, str)
    command_timed_out = QtCore.pyqtSignal(PendingCommand)

    def __init__(
        self,
        serial: SerialManager,
        *,
        model: str,
        device_id: str,
        password_provider: Optional[PasswordProvider] = None,
        timestamp_provider: Optional[TimestampProvider] = None,
        timeout_ms: int = 60_000,
    ) -> None:
        super().__init__()
        self._serial = serial
        self._model = model
        self._device_id = device_id
        self._password_provider = password_provider or (lambda _spec: None)
        self._timestamp_provider = timestamp_provider or (lambda: int(time.time()))
        self._timeout_ms = timeout_ms
        self._sequence = 0
        self._rx_buffer = ""
        self._pending: Dict[int, _PendingEntry] = {}

        self._serial.data_received.connect(self._on_serial_data)
        self._serial.error_occurred.connect(self.transport_error)

    # ------------------------------------------------------------------
    def next_sequence(self) -> int:
        self._sequence = (self._sequence + 1) % 10_000
        return self._sequence

    def send(
        self,
        command_name: str,
        positional: Optional[Iterable[str]] = None,
        keyword: Optional[dict] = None,
        *,
        password: Optional[str] = None,
        timestamp: Optional[int] = None,
        sequence: Optional[int] = None,
    ) -> PendingCommand:
        spec = registry.get_command(command_name)

        pwd = password if password is not None else self._password_provider(spec)

        header = FrameHeader(
            model=self._model,
            device_id=self._device_id,
            sequence=sequence if sequence is not None else self.next_sequence(),
            timestamp=timestamp if timestamp is not None else self._timestamp_provider(),
            password=pwd,
        )
        frame = CommandFrame(
            header=header,
            spec=spec,
            positional=list(positional or []),
            keyword=dict(keyword or {}),
        )
        raw = codec.encode_command(frame)
        self._write(raw)
        pending = PendingCommand(frame=frame, raw_line=raw)
        self._install_timeout(pending)
        self.frame_sent.emit(frame, raw)
        self.raw_sent.emit(raw)
        return pending

    def send_frame(self, frame: CommandFrame) -> PendingCommand:
        raw = codec.encode_command(frame)
        self._write(raw)
        pending = PendingCommand(frame=frame, raw_line=raw)
        self._install_timeout(pending)
        self.frame_sent.emit(frame, raw)
        self.raw_sent.emit(raw)
        return pending

    def pending(self) -> Dict[int, PendingCommand]:
        return {seq: entry.command for seq, entry in self._pending.items()}

    # ------------------------------------------------------------------
    def _install_timeout(self, pending: PendingCommand) -> None:
        timer = QtCore.QTimer(self)
        timer.setSingleShot(True)
        timer.setInterval(self._timeout_ms)
        seq = pending.frame.header.sequence
        timer.timeout.connect(lambda seq=seq: self._on_timeout(seq))
        timer.start()
        self._pending[seq] = _PendingEntry(command=pending, timer=timer)

    def _finalize_pending(self, seq: int) -> Optional[PendingCommand]:
        entry = self._pending.pop(seq, None)
        if entry is None:
            return None
        entry.timer.stop()
        entry.timer.deleteLater()
        return entry.command

    def _write(self, raw: str) -> None:
        if not self._serial.is_connected():
            raise RuntimeError("El puerto serial no está conectado")
        self._serial.send_data_bytes(raw.encode("ascii"))

    # ------------------------------------------------------------------
    def _on_serial_data(self, chunk: bytes, port: str) -> None:  # noqa: ARG002
        try:
            text = chunk.decode("ascii", errors="ignore")
        except Exception:
            text = chunk.decode("latin1", errors="ignore")
        self._rx_buffer += text
        while "\n" in self._rx_buffer:
            line, self._rx_buffer = self._consume_line(self._rx_buffer)
            if not line:
                continue
            self._dispatch_line(line)

    def _consume_line(self, buffer: str) -> tuple[str, str]:
        idx = buffer.find("\n")
        line = buffer[:idx].rstrip("\r")
        rest = buffer[idx + 1 :]
        return line, rest

    def _dispatch_line(self, line: str) -> None:
        try:
            if line.startswith(qc1_proto.QC1_SIGNATURE + ","):
                pkt = codec.decode_packet(line)
                self.packet_received.emit(pkt)
                self._finalize_pending(pkt.hdr.seq)
            else:
                resp = codec.decode_response(line)
                self.response_received.emit(resp)
                self._finalize_pending(resp.sequence)
        except Exception as exc:
            self.parse_failed.emit(f"No se pudo interpretar: {line} ({exc})")

    def _on_timeout(self, seq: int) -> None:
        command = self._finalize_pending(seq)
        if command is not None:
            self.command_timed_out.emit(command)


__all__ = ["SerialCommandService"]
