from PyQt6 import QtWidgets


class VSpacer(QtWidgets.QWidget):
    """Thin vertical spacer used in side bar layouts."""

    def __init__(self, height: int = 8):
        super().__init__()
        self.setFixedHeight(height)


class HLine(QtWidgets.QFrame):
    """Light horizontal separator line for cards."""

    def __init__(self):
        super().__init__()
        self.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        self.setFixedHeight(1)
        self.setProperty("line", True)

