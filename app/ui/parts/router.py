from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Type
from PyQt6 import QtWidgets

@dataclass(frozen=True)
class PageSpec:
    name: str
    factory: Callable[[], QtWidgets.QWidget]  # o Type[QtWidgets.QWidget]


class PageRouter(QtWidgets.QStackedWidget):
    """
    Administra el stack de páginas y permite activar por nombre.
    """
    def __init__(self, specs: list[PageSpec]):
        super().__init__()
        self._index_by_name: dict[str, int] = {}
        for spec in specs:
            widget = spec.factory() if callable(spec.factory) else spec.factory()
            idx = self.addWidget(widget)
            self._index_by_name[spec.name] = idx

    def setActive(self, name: str) -> None:
        idx = self._index_by_name.get(name)
        if idx is not None:
            self.setCurrentIndex(idx)

    def page(self, name: str) -> QtWidgets.QWidget | None:
        idx = self._index_by_name.get(name)
        return self.widget(idx) if idx is not None else None

    def names(self) -> list[str]:
        return list(self._index_by_name.keys())
