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

        # Device Manager
        group_vivi = QGroupBox("Vivi")
        group_vivi.setFixedSize(QSize(500, 650))

        layout_vivi = QVBoxLayout()
        layout_dev = QHBoxLayout()
        self.dev_list = QComboBox(  )
        self.port_list = vivi.get_port_list()
        self.dev_list.addItems( [p.device for p in self.port_list] )
        self.dev_list.addItems( ["1","2"] )
        self.dev_list.currentIndexChanged.connect( self.dev_changed )

        self.dev_connect = QPushButton( "Connect!" )
        self.dev_connect.pressed.connect( self.connect_device )
        self.dev_status = QLabel( "HELLO" )

        self.board = vivi.Board( None )
        self.board.valueChanged.connect( self.msg_received )

        self.msg_received( )

        layout_dev.addWidget( self.dev_list )
        layout_dev.addWidget( self.dev_connect )
        layout_vivi.addLayout( layout_dev )
        layout_vivi.addWidget( self.dev_status )
        group_vivi.setLayout( layout_vivi )

        group_bot = QGroupBox("Viviewer")
        layout_bot = QHBoxLayout()
        group_bot.setLayout(layout_bot)

        layout = QHBoxLayout()
        layout.addWidget( group_vivi )
        layout.addWidget( group_bot )

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget( widget )

    def msg_received(self):
        self.dev_status.setText( self.board.msg )

    def connect_device(self):
        if self.board.connected:
            self.board.dev.close()
            self.board = vivi.Board( None )

        try:
            portname = self.port_list[self.dev_list.currentIndex()].device
            self.board = vivi.Board( portname=portname )
            boardmsg = "Connected to ADC-8 board: "+ portname +"\n"
            boardmsg += "           Serial number: "+ self.board.serial_number
            self.dev_status.setText( boardmsg )
        except:
            self.board = vivi.Board( None )


    def dev_changed(self):
        print( "Selected: "+self.dev_list.currentText())
        self.connect_device(  )
        

app = QApplication(sys.argv)

# import serial.tools.list_ports
# ports =  vivi.get_port_list()
# for p in ports:
#     print( p.device )

window = MainWindow()
window.show()



app.exec()