# auto-transfer.py
"""Program to store continuous data readings from an ADC-8 board."""
"""Based off of adc8-transfer.py and noise-density.py"""
import serial
import threading
import time
from PyQt6.QtCore import (Qt, pyqtSignal, QTimer, QObject)
from PyQt6.QtWidgets import QWidget

import struct
import sys



class TO(QObject):
    """Represent a single ADC-8 board."""
    def __init__(self,name):
        super().__init__() #Inherit QObject to send Qt signal
        self.name = name
        self.stop = False

    def start_comm(self):
        counter = 0
        while True:
            time.sleep(0.03)
            counter += 1
            print("{} is Listening {}".format(self.name, counter))

            if self.stop:
                print("Halting")
                break