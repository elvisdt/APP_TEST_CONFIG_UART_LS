from __future__ import annotations
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Palette:
    primary: str = "#1F7AE0"
    primary_hover: str = "#1862B8"
    primary_soft: str = "#E6F0FF"
    text: str = "#1E293B"
    text_subtle: str = "#334155"
    muted: str = "#64748B"
    background: str = "#F4F6F9"
    surface: str = "#FFFFFF"
    surface_alt: str = "#F8FAFC"
    surface_hover: str = "#EEF2F8"
    border: str = "#D0D7E2"
    border_strong: str = "#B8C2D3"
    focus: str = "#1F7AE0"
    success: str = "#0F9D58"
    warning: str = "#F59E0B"
    error: str = "#DC2626"
    scrollbar: str = "#C7D2E8"
    scrollbar_hover: str = "#A5B4CF"
    divider: str = "#E2E8F0"
    font_stack: str = "'Inter', 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif"


def _light_template() -> str:
    return """
/* Base */
* {{
    font-family: {font_stack};
    font-size: 13px;
    color: {text};
}}
QMainWindow, QWidget {{
    background-color: {background};
}}

/* Top bar */
#TopBar {{
    background-color: {surface};
    border-bottom: 1px solid {border};
}}
#TopTitle {{
    color: {text_subtle};
    font-weight: 600;
    font-size: 16px;
}}
#TopSubtitle {{
    color: {muted};
    font-size: 12px;
}}

/* Sidebar */
#SideBar {{
    background-color: {surface};
    border-right: 1px solid {border};
}}
QPushButton[sideBtn="true"] {{
    background-color: transparent;
    color: {muted};
    padding: 10px 14px;
    border: none;
    border-radius: 8px;
    text-align: left;
}}
QPushButton[sideBtn="true"]:hover {{
    background-color: {surface_hover};
    color: {text_subtle};
}}
QPushButton[sideBtn="true"][active="true"],
QPushButton[sideBtn="true"]:checked {{
    background-color: {primary_soft};
    color: {primary};
    font-weight: 600;
}}

/* Cards */
QFrame[card="true"] {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 14px;
    padding: 14px;
}}
QLabel[cardTitle="true"] {{
    color: {text_subtle};
    font-weight: 600;
    font-size: 13px;
    margin-bottom: 6px;
}}
QFrame[card="true"] QLabel[muted="true"],
QLabel[muted="true"] {{
    color: {muted};
}}

/* Separadores */
QFrame[line="true"] {{
    background-color: {divider};
    max-height: 1px;
    min-height: 1px;
}}

/* Inputs */
QLineEdit, QPlainTextEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 6px 8px;
}}
QLineEdit:focus, QPlainTextEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus {{
    border: 2px solid {focus};
}}
QComboBox QAbstractItemView {{
    background-color: {surface};
    border: 1px solid {border};
    selection-background-color: {primary};
    selection-color: #ffffff;
}}

/* Buttons */
QPushButton {{
    background-color: {primary};
    color: #ffffff;
    border-radius: 8px;
    padding: 8px 16px;
    border: none;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {primary_hover};
}}
QPushButton:disabled {{
    background-color: {border};
    color: {muted};
}}
QPushButton[ghost="true"] {{
    background-color: transparent;
    border: 1px solid {border};
    color: {text_subtle};
}}
QPushButton[ghost="true"]:hover {{
    background-color: {surface_alt};
}}

/* Lists & tables */
QListWidget, QTableWidget, QTableView {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 10px;
}}
QListWidget::item {{
    padding: 6px 10px;
}}
QListWidget::item:selected {{
    background-color: {primary_soft};
    color: {primary_hover};
}}
QHeaderView::section {{
    background-color: {surface_alt};
    color: {muted};
    border: none;
    padding: 8px;
}}

/* Tabs */
QTabBar::tab {{
    background-color: {surface_alt};
    color: {muted};
    padding: 8px 14px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    border: 1px solid {border};
}}
QTabBar::tab:selected {{
    background-color: {primary};
    color: #ffffff;
    border-color: {primary};
}}
QTabWidget::pane {{
    border: 1px solid {border};
    background-color: {surface};
}}

/* Scrollbars */
QScrollBar:vertical {{
    background-color: transparent;
    width: 12px;
}}
QScrollBar::handle:vertical {{
    background-color: {scrollbar};
    border-radius: 6px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background-color: {scrollbar_hover};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background-color: transparent;
    height: 12px;
}}
QScrollBar::handle:horizontal {{
    background-color: {scrollbar};
    border-radius: 6px;
    min-width: 24px;
}}
QScrollBar::handle:horizontal:hover {{
    background-color: {scrollbar_hover};
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}
""".strip()


def build_light_qss(palette: Palette | None = None) -> str:
    palette = palette or Palette()
    return _light_template().format(**asdict(palette))


class Styles:
    @staticmethod
    def palette() -> Palette:
        return Palette()

    @staticmethod
    def light() -> str:
        return build_light_qss(Styles.palette())

    @staticmethod
    def dark() -> str:
        return Styles.light()


def get_qss() -> str:
    return Styles.light()
