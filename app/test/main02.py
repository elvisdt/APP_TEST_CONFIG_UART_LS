from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Siempre al frente")
        # --- Lo importante ---
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        # Ajusta tamaño
        self.resize(400, 300)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
