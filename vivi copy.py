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

VERSION = "3"

NUM_CHANNELS = 4
HDR_LEN = 16
BIPOLAR = 2
SCALE_24 = 1.0 / (1 << 24)
VREF = 2.5 * 1.02		# Include 2% correction factor

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

class Board(QObject):
    status = int
    status_signal = pyqtSignal(int)
    finished = pyqtSignal()
    stop = bool
    # -1 = Board is not Ready
    # 0 = Board is Ready
    # 1 = Board is Acquiring
    # 2 = Board finished acquring
    """Represent a single ADC-8 board."""
    def __init__(self, portname=None):
        """
        Initialize an ADC-8 Board object.
        """
        super().__init__() #Inherit QWidget to send Qt signal

        self.NUM_CHANNELS = 4
        self.HDR_LEN = 16
        self.BIPOLAR = 2
        self.SCALE_24 = 1.0 / (1 << 24)
        self.VREF = 2.5 * 1.02		# Include 2% correction factor

        self.dev = None
        self.connected = False
        # self.

    def connect_board( self, portname ):
        """  
        portname is the name of the board's USB serial port device, 
        which will be opened in exclusive mode.
        """
        if portname is None:
            #print("No serial port name specified")
            self.dev = None
            self.connected = False
            self.set_status( -1 ) 
        else :
            self.dev = serial.Serial(portname, exclusive=True)
            time.sleep(0.8)
            # Verify that the device is an ADC-8 board running the
            # proper firmware
            msg = self.get_board_id()
            if msg.startswith("ADC-8"):
                self.connected = True
                self.set_status( 0 )
            else:
                self.dev = None
                self.connected = False
                self.set_status( -1 ) 
                print("Device is not an ADC-8 board")

    def close_board( self ):
        self.dev.close()
        self.dev = None
        self.connected = False
        self.set_status( -1 ) 

    def set_status( self, value ):
        self.status = value
        self.status_signal.emit( value )

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
    
    def send_command(self, msg):
        # Send Serial Command and Listen
        if self.connected:
            write_msg = msg + "\n"
            self.dev.write( write_msg.encode() )
            a = self.dev.read(1500)
        else:
            a = "\nConnect an ADC-8 Board to Start"
            a = a.encode()
        return a
    
    def get_board_status(self):
        return self.send_command("c")
        
    def set_all_gains(self, gain):
        return self.send_command("g 0 {}".format(gain))
    
    def set_individual_gain(self, ch, gain):
        return self.send_command("g {} {}".format(ch, gain))
    
    def set_sampling(self, sampling):
        return self.send_command("s {}".format(sampling))
    
    def convert_values(self, block, gains, bipolar, num):
        """Convert the 24-bit values in block to floating-point numbers
        and store them in the global variable volts."""

        j = v = 0
        volts = [0.] * num
        for i, g in enumerate(gains):
            if g == 0:
                continue
            x = (block[j] + (block[j+1] << 8) + (block[j+2] << 16)) * SCALE_24
            if bipolar[i]:
                x = 2. * x - 1.
            volts[v] = round(x * VREF / g, 9)
            j += 3
            v += 1
        return volts
    
    def start_transfer(self, acq_time=2):
        self.set_status( 1 )

        self.dev.write(f"b{acq_time}\n".encode())
        self.dev.timeout = 6
        self.dev.read_until(b"+")		# Skip initial text

        sig = b""
        h = self.dev.read(HDR_LEN)
        if len(h) == HDR_LEN:
            hdr = struct.unpack(f"<4sHBB {2 * self.NUM_CHANNELS}B", h)
            sig = hdr[0]		# The signature
        if sig != b"ADC8":
            print("Invalid header received, transfer aborted")
            self.dev.write(b"\n")
            self.set_status( 0 )
            sys.exit()

        chans = hdr[4:]			# The ADC channel entries
        num = 0
        gains = [chans[2 * i] for i in range(self.NUM_CHANNELS)]
        bipolar = [chans[2 * i + 1] & self.BIPOLAR for i in range(self.NUM_CHANNELS)]
        for g in gains:
            if g > 0:
                num += 1
        if num == 0:
            print("Header shows no active ADCs, transfer aborted")
            self.dev.write(b"\n")
            self.set_status( 0 )
            sys.exit()

        blocksize = num * 3

        total_blocks = 0
        warned = False

        # threading.Thread(target=poll_stdin, daemon=True).start()
        output_data = []
        # Receive and store the data
        cont = True
        counter = 0
        while cont:
            counter +=1
            print(counter)
            n = self.dev.read(1)		# Read the buffer's length byte
            if len(n) == 0:
                print("Timeout")
                break
            n = n[0]
            if n == 0:
                print("End of data")
                break

            d = self.dev.read(n)		# Read the buffer contents
            if len(d) < n:
                print("Short data buffer received")
                break
            
            if n % blocksize != 0:
                if not warned:
                    print("Warning: Invalid buffer length", n)
                    warned = True
                n -= n % blocksize


            for i in range(0, n, blocksize):
                # Convert the block data to floats and write them out
                volts = self.convert_values(d[i:i + blocksize], gains, bipolar, num)
                output_data.append ( volts )
            


            total_blocks += n // blocksize

            if self.stop == True:
                print("Termination requested")
                break
            # if stdin_available.is_set():
            #     print("Termination requested")
            #     break

        self.dev.write(b"\n")
        print("Transfer ended")
        print(total_blocks, "blocks received")

        self.dev.timeout = 0.01
        self.dev.read(1000)		# Flush any extra output

        self.set_status( 2 )
        self.set_status( 0 )
        return output_data