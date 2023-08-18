import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QWidget,
    QGroupBox
)
from PyQt6.QtGui import QPalette, QColor, QFont, QFontDatabase
import os

class Color(QWidget):

    def __init__(self, color):
        super(Color, self).__init__()
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(color))
        self.setPalette(palette)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vivi")
        self.setFixedSize(QSize(1280, 700))

        group_top = QGroupBox("Vivi")
        group_top.setFixedSize(QSize(1280, 200))
        layout_top = QHBoxLayout()
        group_top.setLayout(layout_top)

        group_bot = QGroupBox("Viviewer")
        layout_bot = QHBoxLayout()
        group_bot.setLayout(layout_bot)

        layout = QVBoxLayout()
        layout.addWidget( group_top )
        layout.addWidget( group_bot )

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget( widget )
app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()