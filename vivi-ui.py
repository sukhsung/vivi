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
    QGroupBox,
    QComboBox
)
from PyQt6.QtGui import QPalette, QColor, QFont, QFontDatabase

import sys
import os
import vivi



class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vivi")
        self.setFixedSize(QSize(1280, 700))

        group_top = QGroupBox("Vivi")
        group_top.setFixedSize(QSize(1280, 200))
        layout_top = QHBoxLayout()
        self.dev_list = QComboBox(  )
        self.dev_list.addItems( [p.device for p in vivi.get_port_list()] )
        # print( self.dev_list.currentText() )
        self.board = vivi.Board( self.dev_list.currentText())

        layout_top.addWidget( self.dev_list )
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

# import serial.tools.list_ports
# ports =  vivi.get_port_list()
# for p in ports:
#     print( p.device )

window = MainWindow()
window.show()



app.exec()