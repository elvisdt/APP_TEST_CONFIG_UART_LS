
"""
qc1_proto.py — Core parser/builder/dispatcher for the QC1 ASCII+XOR protocol.

Design goals:
- No external deps. Pure Python 3.9+.
- Clean separation: parsing, building frames, and dispatching handlers.
- CSV with quoted fields (values may contain commas, spaces).
- PWD policy: digits only, length 6..10, attached as "PWD=...".
- Ready to be plugged into a PyQt6 app (no UI/serial here).

Frame format (command & responses share shape):
    QC1,<model>,<dev>,<seq>,<ts>,<cmd>[,<arg1>...][,PWD=<digits>]*CS\r\n

Checksum:
    XOR of all bytes from the 'Q' of 'QC1' up to the char right before '*', then
    render as two uppercase hex digits.

Public API (summary):
    - parse_line(line: str) -> QC1Packet
    - build_command(model, dev, seq, ts, cmd, *positional, pwd=None, **kv) -> str
    - Dispatcher: QC1Dispatcher with register_handler(name, fn, flags=...)
    - Helpers: build_ok(...), build_err(...), build_evt(...)
    - Blob: QC1BlobSession for chunked uploads/downloads management

Author: <tu nombre>
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple, Any
import re
import base64

# ---------------------------
# Constants & flags
# ---------------------------

QC1_SIGNATURE = "QC1"
QC1_LINE_MAX = 2048
QC1_MAX_ARGS = 64

PWD_MIN = 6
PWD_MAX = 10

# Command flags
QCF_NONE       = 0x00
QCF_NEED_PWD   = 0x01   # requires PWD to be present & valid
QCF_READONLY   = 0x02   # does not mutate state
QCF_STREAM     = 0x04   # emits multiple responses

# Error codes
QC1_OK                 = 200
QC1_ERR_SYNTAX         = 400
QC1_ERR_AUTH           = 401
QC1_ERR_FORBIDDEN      = 403
QC1_ERR_NOTFOUND       = 404
QC1_ERR_CONFLICT       = 409
QC1_ERR_UNPROCESSABLE  = 422
QC1_ERR_INTERNAL       = 500


# ---------------------------
# Types
# ---------------------------

@dataclass
class QC1Header:
    model: str
    dev: str
    seq: int
    ts: int
    cmd: str

@dataclass
class QC1Packet:
    hdr: QC1Header
    # Split args into: positional list and dict of k=v pairs
    positional: List[str] = field(default_factory=list)
    kv: Dict[str, str] = field(default_factory=dict)
    pwd: str = ""

    def get_pos(self, idx: int) -> Optional[str]:
        return self.positional[idx] if 0 <= idx < len(self.positional) else None

    def get_kv(self, key: str) -> Optional[str]:
        return self.kv.get(key)

@dataclass
class QC1Response:
    """Parsed response frame (OK/ERR/EVT)."""
    prefix: str
    dev: str
    seq: int
    ts: int
    fields: List[str] = field(default_factory=list)

    def as_list(self) -> List[str]:
        return list(self.fields)

    def as_dict(self) -> Dict[str, str]:
        data: Dict[str, str] = {}
        for item in self.fields:
            if "=" in item:
                key, value = item.split("=", 1)
                data[key] = value
        return data

    def is_ok(self) -> bool:
        return self.prefix.upper() == "OK"

    def is_error(self) -> bool:
        return self.prefix.upper() == "ERR"

    def error_detail(self) -> Optional[Tuple[int, str]]:
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
# Handler signature
QC1Handler = Callable[[QC1Packet, "QC1Context"], List[str]]

@dataclass
class QC1Context:
    """Context object to pass around application state and policies.
       You can subclass or extend with your own fields later."""
    model_fabric: str = "-"
    dev_id: str = "-"
    # Password check callback (digits-only policy is pre-validated in parser/builder).
    check_pwd: Optional[Callable[[str], bool]] = None
    set_pwd: Optional[Callable[[str, str], bool]] = None  # (old, new) -> ok?


# ---------------------------
# Checksum & utils
# ---------------------------

def xor_checksum_ascii(s: str) -> str:
    acc = 0
    for b in s.encode("ascii", "strict"):
        acc ^= b
    return f"{acc:02X}"

_pwd_re = re.compile(r"^\d{6,10}$")

def validate_pwd(pwd: str) -> bool:
    return bool(_pwd_re.fullmatch(pwd))

def _rstrip_crlf(s: str) -> str:
    return s.rstrip("\r\n")


# ---------------------------
# CSV parsing with quotes
# ---------------------------

def csv_split_q(s: str) -> List[str]:
    """Split CSV with support for quoted fields. No escapes inside quotes;
    quotes must be balanced. Example: a,b,\"Hello, world\",c"""
    out: List[str] = []
    i, n = 0, len(s)
    while i < n:
        # skip commas
        if s[i] == ",":
            i += 1
            continue
        if s[i] == '"':
            # quoted field
            i += 1
            start = i
            while i < n and s[i] != '"':
                i += 1
            out.append(s[start:i])
            i += 1  # skip closing quote
            if i < n and s[i] == ",":
                i += 1
        else:
            start = i
            while i < n and s[i] != ",":
                i += 1
            out.append(s[start:i])
            if i < n and s[i] == ",":
                i += 1
    return out


# ---------------------------
# Parsing
# ---------------------------

class QC1ParseError(Exception):
    pass

def parse_line(line: str) -> QC1Packet:
    """
    Parse and verify a QC1 line. Returns QC1Packet.
    Raises QC1ParseError on failure.
    """
    if not isinstance(line, str):
        raise QC1ParseError("line must be str")
    line = _rstrip_crlf(line)
    if len(line) > QC1_LINE_MAX:
        raise QC1ParseError("line too long")

    try:
        star = line.index("*")
    except ValueError:
        raise QC1ParseError("missing '*'")
    if star + 2 >= len(line):
        raise QC1ParseError("missing checksum hex")
    cs_hex = line[star + 1: star + 3]
    payload = line[:star]
    calc = xor_checksum_ascii(payload)
    if calc.upper() != cs_hex.upper():
        raise QC1ParseError(f"checksum mismatch: have {cs_hex}, want {calc}")

    fields = csv_split_q(payload)
    if len(fields) < 6:
        raise QC1ParseError("need at least 6 fields: QC1,model,dev,seq,ts,cmd")

    if fields[0] != QC1_SIGNATURE:
        raise QC1ParseError("bad signature")

    model, dev = fields[1], fields[2]
    try:
        seq = int(fields[3])
    except Exception:
        raise QC1ParseError("bad seq")
    if seq < 1 or seq > 9999:
        raise QC1ParseError("seq out of range")

    try:
        ts = int(fields[4])
    except Exception:
        ts = 0

    cmd = fields[5]
    positional: List[str] = []
    kv: Dict[str, str] = {}
    pwd = ""

    for f in fields[6:]:
        if f.startswith("PWD="):
            pwd = f[4:]
            continue
        eq = f.find("=")
        if eq == -1:
            positional.append(f)
        else:
            key = f[:eq]
            val = f[eq+1:]
            kv[key] = val

    # PWD policy: if present, must be digits-only len 6..10
    if pwd and not validate_pwd(pwd):
        raise QC1ParseError("invalid PWD format")

    hdr = QC1Header(model=model, dev=dev, seq=seq, ts=ts, cmd=cmd)
    return QC1Packet(hdr=hdr, positional=positional, kv=kv, pwd=pwd)


# ---------------------------
# Building frames
# ---------------------------


def parse_response(line: str) -> QC1Response:
    """Parse device response line (OK/ERR/EVT frames)."""
    if not isinstance(line, str):
        raise QC1ParseError("line must be str")
    line = _rstrip_crlf(line)
    if not line:
        raise QC1ParseError("empty line")
    try:
        star = line.index("*")
    except ValueError:
        raise QC1ParseError("missing asterisk")
    if star + 2 >= len(line):
        raise QC1ParseError("missing checksum hex")
    cs_hex = line[star + 1: star + 3]
    payload = line[:star]
    calc = xor_checksum_ascii(payload)
    if calc.upper() != cs_hex.upper():
        raise QC1ParseError(f"checksum mismatch: have {cs_hex}, want {calc}")
    fields = csv_split_q(payload)
    if len(fields) < 4:
        raise QC1ParseError("need at least 4 fields: prefix,dev,seq,ts")
    prefix = fields[0]
    dev = fields[1]
    try:
        seq = int(fields[2])
    except Exception:
        raise QC1ParseError("bad seq")
    try:
        ts = int(fields[3])
    except Exception:
        raise QC1ParseError("bad ts")
    return QC1Response(prefix=prefix, dev=dev, seq=seq, ts=ts, fields=fields[4:])
def build_command(model: str, dev: str, seq: int, ts: int, cmd: str,
                  *positional: str,
                  pwd: Optional[str] = None,
                  **kv: str) -> str:
    """
    Build a QC1 command line with XOR checksum and CRLF.
    positional: any extra args without '='
    kv: key=value fields as kwargs
    pwd: optional numeric password (6..10). If passed, added as PWD=... at end.
    """
    if pwd is not None and not validate_pwd(pwd):
        raise ValueError("PWD must be digits length 6..10")
    parts: List[str] = [QC1_SIGNATURE, str(model), str(dev), f"{seq:04d}", str(ts), str(cmd)]
    parts += list(map(str, positional))
    # keep insertion order of kv
    for k, v in kv.items():
        parts.append(f"{k}={v}")
    if pwd is not None:
        parts.append(f"PWD={pwd}")
    payload = ",".join(parts)
    cs = xor_checksum_ascii(payload)
    return f"{payload}*{cs}\r\n"


# ---------------------------
# Responses builder
# ---------------------------

def _build_response(prefix: str, dev: str, seq: int, ts: int, *chunks: str) -> str:
    payload = ",".join([prefix, dev, f"{seq:04d}", str(ts)] + [c for c in chunks if c])
    cs = xor_checksum_ascii(payload)
    return f"{payload}*{cs}\r\n"

def build_ok(dev: str, seq: int, ts: int, *chunks: str) -> str:
    return _build_response("OK", dev, seq, ts, *chunks)

def build_err(dev: str, seq: int, ts: int, code: int, reason: str = "") -> str:
    payload = f"{code},{reason}" if reason else f"{code}"
    return _build_response("ERR", dev, seq, ts, payload)

def build_evt(dev: str, seq: int, ts: int, event: str, *kv: str) -> str:
    # kv already in form "k=v"
    payloads = [event] + list(kv)
    return _build_response("EVT", dev, seq, ts, *payloads)


# ---------------------------
# Dispatcher
# ---------------------------

@dataclass
class _CmdDesc:
    name: str
    fn: QC1Handler
    flags: int = QCF_NONE
    min_args: int = 0
    max_args: int = QC1_MAX_ARGS

class QC1Dispatcher:
    def __init__(self, ctx: QC1Context):
        self.ctx = ctx
        self._cmds: Dict[str, _CmdDesc] = {}

    def register_handler(self, name: str, fn: QC1Handler, *, flags: int = QCF_NONE,
                         min_args: int = 0, max_args: int = QC1_MAX_ARGS) -> None:
        self._cmds[name] = _CmdDesc(name=name, fn=fn, flags=flags,
                                    min_args=min_args, max_args=max_args)

    def dispatch(self, pkt: QC1Packet) -> List[str]:
        d = self._cmds.get(pkt.hdr.cmd)
        if not d:
            return [build_err(pkt.hdr.dev, pkt.hdr.seq, pkt.hdr.ts, QC1_ERR_NOTFOUND, "cmd")]

        argc = len(pkt.positional) + len(pkt.kv)
        if argc < d.min_args or argc > d.max_args:
            return [build_err(pkt.hdr.dev, pkt.hdr.seq, pkt.hdr.ts, QC1_ERR_UNPROCESSABLE, f"arg count {d.min_args}..{d.max_args}")]

        if (d.flags & QCF_NEED_PWD) and self.ctx.check_pwd is not None:
            if not pkt.pwd or not self.ctx.check_pwd(pkt.pwd):
                return [build_err(pkt.hdr.dev, pkt.hdr.seq, pkt.hdr.ts, QC1_ERR_AUTH, "PWD required/invalid")]

        try:
            out_lines = d.fn(pkt, self.ctx)
            return out_lines
        except Exception as e:
            return [build_err(pkt.hdr.dev, pkt.hdr.seq, pkt.hdr.ts, QC1_ERR_INTERNAL, str(e))]


# ---------------------------
# Blob upload/download session helper
# ---------------------------

@dataclass
class QC1BlobSession:
    """Minimal state holder for an ongoing BLOB upload/download."""
    type: str = ""
    slot: Optional[int] = None
    size: int = 0
    sha1: str = ""
    received: int = 0
    seq_next: int = 0
    chunks: List[bytes] = field(default_factory=list)

    def open(self, type_: str, slot: Optional[int], size: int, sha1: str) -> None:
        self.type = type_
        self.slot = slot
        self.size = size
        self.sha1 = sha1
        self.received = 0
        self.seq_next = 0
        self.chunks.clear()

    def feed(self, seq: int, b64: str) -> None:
        if seq != self.seq_next:
            raise ValueError("out-of-order chunk")
        data = base64.b64decode(b64.encode("ascii"))
        self.chunks.append(data)
        self.received += len(data)
        self.seq_next += 1

    def close(self) -> bytes:
        blob = b"".join(self.chunks)
        # SHA1 verification left to caller to keep lib-free (use hashlib.sha1 if desired)
        if len(blob) != self.size:
            raise ValueError("size mismatch")
        return blob


# ---------------------------
# Built-in demo handlers (stubs) — you can replace by real storage
# ---------------------------

def h_SYS_INFO(pkt: QC1Packet, ctx: QC1Context) -> List[str]:
    return [build_ok(pkt.hdr.dev, pkt.hdr.seq, pkt.hdr.ts, f"MODEL={ctx.model_fabric},DEV={ctx.dev_id},FW=1.0.0")]

def h_SEC_PWD_SET(pkt: QC1Packet, ctx: QC1Context) -> List[str]:
    old = pkt.get_pos(0)
    new = pkt.get_pos(1)
    if not old or not new:
        return [build_err(pkt.hdr.dev, pkt.hdr.seq, pkt.hdr.ts, QC1_ERR_UNPROCESSABLE, "need old,new")]
    if not validate_pwd(new):
        return [build_err(pkt.hdr.dev, pkt.hdr.seq, pkt.hdr.ts, QC1_ERR_UNPROCESSABLE, "PWD digits 6..10")]
    if ctx.set_pwd is None or not ctx.set_pwd(old, new):
        return [build_err(pkt.hdr.dev, pkt.hdr.seq, pkt.hdr.ts, QC1_ERR_AUTH, "old invalid")]
    return [build_ok(pkt.hdr.dev, pkt.hdr.seq, pkt.hdr.ts)]

def h_AUDIO_PLAY(pkt: QC1Packet, ctx: QC1Context) -> List[str]:
    slot = pkt.get_pos(0)
    onoff = pkt.get_pos(1)
    dur = pkt.get_kv("DUR")
    if not slot or onoff not in ("ON", "OFF"):
        return [build_err(pkt.hdr.dev, pkt.hdr.seq, pkt.hdr.ts, QC1_ERR_UNPROCESSABLE, "slot,ON|OFF")]
    if dur:
        try:
            d = int(dur)
            if d < 10 or d > 240:
                raise ValueError
        except Exception:
            return [build_err(pkt.hdr.dev, pkt.hdr.seq, pkt.hdr.ts, QC1_ERR_UNPROCESSABLE, "DUR 10..240")]
    # Here you would toggle audio engine...
    if onoff == "ON":
        return [build_ok(pkt.hdr.dev, pkt.hdr.seq, pkt.hdr.ts, f"PLAYING={slot}")]
    else:
        return [build_ok(pkt.hdr.dev, pkt.hdr.seq, pkt.hdr.ts, f"STOPPED={slot}")]


# ---------------------------
# Demo registry (you can ignore if wiring your own app)
# ---------------------------

def make_default_dispatcher(ctx: Optional[QC1Context] = None) -> QC1Dispatcher:
    if ctx is None:
        ctx = QC1Context(model_fabric="ALR-LTE", dev_id="A1B2C3",
                         check_pwd=lambda p: p == "123456",
                         set_pwd=lambda old,new: old=="123456")
    disp = QC1Dispatcher(ctx)
    disp.register_handler("SYS.INFO?", h_SYS_INFO, flags=QCF_READONLY)
    disp.register_handler("SEC.PWD.SET", h_SEC_PWD_SET, flags=QCF_NONE, min_args=2, max_args=2)
    disp.register_handler("AUDIO.PLAY", h_AUDIO_PLAY, flags=QCF_NEED_PWD, min_args=2, max_args=3)
    return disp


# ---------------------------
# Roundtrip test (manual)
# ---------------------------

if __name__ == "__main__":
    # Build a frame and parse it back
    cmd = build_command("ALR-LTE", "A1B2C3", 12, 0, "AUDIO.PLAY", "4", "ON", DUR=30, pwd="123456")
    print(cmd.strip())

    pkt = parse_line(cmd)
    print(pkt)

    disp = make_default_dispatcher()
    out = disp.dispatch(pkt)
    for line in out:
        print(line.strip())

