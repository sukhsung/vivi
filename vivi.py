# auto-transfer.py
"""Program to store continuous data readings from an ADC-8 board."""
"""Based off of adc8-transfer.py and noise-density.py"""
import serial
import threading
import time
from PyQt6.QtCore import (Qt, pyqtSignal)
from PyQt6.QtWidgets import QWidget

VERSION = "3"

NUM_CHANNELS = 4
HDR_LEN = 16
BIPOLAR = 2
SCALE_24 = 1.0 / (1 << 24)
VREF = 2.5 * 1.02		# Include 2% correction factor

stdin_available = threading.Event()

def poll_stdin():
    """Signal when data is available on stdin."""

    input("")
    stdin_available.set()

def get_port_list():
    """\
    Return a list of USB serial port devices.

    Entries in the list are ListPortInfo objects from the
    serial.tools.list_ports module.  Fields of interest include:

        device:  The device's full path name.
        vid:     The device's USB vendor ID value.
        pid:     The device's USB product ID value.
    """

    import serial.tools.list_ports
    return [p for p in serial.tools.list_ports.comports() if p.vid]

class Board(QWidget):
    valueChanged = pyqtSignal(object)
    """Represent a single ADC-8 board."""

    def __init__(self, portname=None, parent=None):
        super(Board, self).__init__(parent)
        self._msg = ""
        """
        Initialize an ADC-8 Board object.  portname is the name of
        the board's USB serial port device, which will be opened in
        exclusive mode.
        """
        self.connected = False

        if portname is None:
            #print("No serial port name specified")
            self.dev = None
        else :
            self.dev = serial.Serial(portname, exclusive=True)
            time.sleep(0.8)

            # Verify that the device is an ADC-8 board running the
            # proper firmware
            self.msg = self.get_board_id()
            if self.msg.startswith("ADC-8"):
                # self.close()

                self.read = self.dev.read
                self.read_until = self.dev.read_until
                self.write = self.dev.write
                self.connected = True

            else:
                self.dev = None
                print("Device is not an ADC-8 board")

    
    @property
    def msg(self):
        return self._msg
    
    @msg.setter
    def msg(self, value):
        self._msg = value
        self.valueChanged.emit(value)

    def __repr__(self):
        """String representation of adc8 Board."""

        return "<Board id=0x{:X}, port={!r}>".format(id(self), self.dev.port)

    def close(self):
        """Close the board's serial port device."""

        self.dev.close()

    def get_board_id(self):
        """Return the board's identification string and store its serial_number."""
        self.dev.timeout = 0.01
        self.dev.write(b'\n')
        self.dev.reset_input_buffer()
        self.dev.read(1000)		# Wait for timeout

        self.dev.write(b'*\n')
        id = self.dev.read_until(size=80)
        n = id.rfind(b"   ")
        if n < 0:
            self.serial_number = ""
        else:
            # Remove the final '\n' and convert to an ASCII string
            self.serial_number = id[n + 3:-1].decode()
        return id[:n].decode()
    