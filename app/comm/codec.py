from __future__ import annotations

from typing import Iterable, List, Optional

from app.core import qc1_proto

from .models import CommandFrame, FrameHeader, ResponseEnvelope


def encode_command(frame: CommandFrame) -> str:
    """Convierte un CommandFrame en una linea QC1 con checksum y CRLF."""
    frame.validate()
    positional = frame.positional
    kv = {f.name: frame.keyword[f.name] for f in frame.spec.keyword if f.name in frame.keyword}
    return qc1_proto.build_command(
        frame.header.model,
        frame.header.device_id,
        frame.header.sequence,
        frame.header.timestamp,
        frame.spec.name,
        *positional,
        pwd=frame.header.password,
        **kv,
    )


def encode_from_parts(
    header: FrameHeader,
    command_name: str,
    positional: Iterable[str] = (),
    *,
    keyword: Optional[dict] = None,
    password: Optional[str] = None,
) -> str:
    return qc1_proto.build_command(
        header.model,
        header.device_id,
        header.sequence,
        header.timestamp,
        command_name,
        *list(positional),
        pwd=password or header.password,
        **(keyword or {}),
    )


def decode_response(line: str) -> ResponseEnvelope:
    resp = qc1_proto.parse_response(line)
    return ResponseEnvelope(
        raw_line=line,
        prefix=resp.prefix,
        device=resp.dev,
        sequence=resp.seq,
        timestamp=resp.ts,
        fields=list(resp.fields),
    )


def decode_packet(line: str) -> qc1_proto.QC1Packet:
    return qc1_proto.parse_line(line)


__all__ = [
    "encode_command",
    "encode_from_parts",
    "decode_response",
    "decode_packet",
]
