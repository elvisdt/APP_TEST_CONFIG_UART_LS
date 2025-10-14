from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple


@dataclass(frozen=True)
class FrameHeader:
    """Metadata que antecede cada comando QC1."""

    model: str
    device_id: str
    sequence: int
    timestamp: int
    password: Optional[str] = None


@dataclass(frozen=True)
class CommandField:
    """Describe un argumento positional o clave-valor esperado por un comando."""

    name: str
    description: str = ""
    required: bool = True
    default: Optional[str] = None


@dataclass(frozen=True)
class CommandSpec:
    """Registro estandar de un comando soportado por el configurador."""

    name: str
    description: str
    category: str
    positional: Tuple[CommandField, ...] = ()
    keyword: Tuple[CommandField, ...] = ()
    requires_password: bool = False


@dataclass
class CommandFrame:
    """Comando listo para serializar y enviar."""

    header: FrameHeader
    spec: CommandSpec
    positional: List[str] = field(default_factory=list)
    keyword: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        # Posicionales
        expected_pos = self.spec.positional
        if len(self.positional) < sum(1 for f in expected_pos if f.required):
            raise ValueError(f"Faltan argumentos posicionales para {self.spec.name}")
        if len(self.positional) > len(expected_pos):
            raise ValueError(f"Demasiados argumentos posicionales para {self.spec.name}")

        # Keyword
        required_kw = {f.name for f in self.spec.keyword if f.required}
        provided_kw = set(self.keyword.keys())
        missing = required_kw - provided_kw
        if missing:
            raise ValueError(f"Faltan campos clave: {', '.join(sorted(missing))}")
        unexpected = provided_kw - {f.name for f in self.spec.keyword}
        if unexpected:
            raise ValueError(f"Campos no soportados: {', '.join(sorted(unexpected))}")

        # Password policy verificada por protocolo; aquí sólo consistencia
        if self.spec.requires_password and not self.header.password:
            raise ValueError("Este comando requiere contraseña (PWD)")


@dataclass
class PendingCommand:
    """Estado temporal de un comando en vuelo."""

    frame: CommandFrame
    raw_line: str


@dataclass
class ResponseEnvelope:
    """Respuesta parseada proveniente del dispositivo."""

    raw_line: str
    prefix: str
    device: str
    sequence: int
    timestamp: int
    fields: Sequence[str]

    def as_dict(self) -> Dict[str, str]:
        data: Dict[str, str] = {}
        for item in self.fields:
            if "=" in item:
                k, v = item.split("=", 1)
                data[k] = v
        return data

    def is_ok(self) -> bool:
        return self.prefix.upper() == "OK"

    def is_error(self) -> bool:
        return self.prefix.upper() == "ERR"

    def error_detail(self) -> tuple[int, str] | None:
        if not self.is_error() or not self.fields:
            return None
        first = self.fields[0]
        if "," in first:
            code_str, message = first.split(",", 1)
        else:
            code_str, message = first, ""
        try:
            return int(code_str), message
        except ValueError:
            return None


__all__ = [
    "FrameHeader",
    "CommandField",
    "CommandSpec",
    "CommandFrame",
    "PendingCommand",
    "ResponseEnvelope",
]
