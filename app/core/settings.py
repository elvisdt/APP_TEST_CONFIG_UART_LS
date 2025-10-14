import json
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class Settings:
    theme: str = "light"
    last_port: str = "COM3"
    device_model: str = "ALR-LTE"
    device_id: str = "A1B2C3"
    device_password: str = "123456"

    @classmethod
    def load(cls, path: str) -> "Settings":
        p = Path(path)
        try:
            return cls(**json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            p.parent.mkdir(parents=True, exist_ok=True)
            s = cls()
            p.write_text(json.dumps(asdict(s), indent=2), encoding="utf-8")
            return s

    def save(self, path: str) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")

