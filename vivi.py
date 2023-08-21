# auto-transfer.py
"""Program to store continuous data readings from an ADC-8 board."""
"""Based off of adc8-transfer.py and noise-density.py"""
import serial
import time, math
from PyQt6.QtCore import (Qt, pyqtSignal, QTimer, QObject, QThread)
from PyQt6.QtWidgets import QWidget
import struct

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
    # -1 = Board is not Ready
    # 0 = Board is Ready
    # 1 = Board is Acquiring

    msg_out = pyqtSignal( str )
    live_data = pyqtSignal( list )

    stop = bool
    listening = bool
    acquire_mode = str
    """Represent a single ADC-8 board."""
    def __init__(self, portname=None):
        """
        Initialize an ADC-8 Board object.
        """
        super().__init__() #Inherit QObject

        self.NUM_CHANNELS = 4
        self.HDR_LEN = 16
        self.BIPOLAR = 2
        self.SCALE_24 = 1.0 / (1 << 24)
        self.VREF = 2.5 * 1.02		# Include 2% correction factor

        self.dev = None
        self.connected = False
        self.listening = False
        self.msg_input = None
        self.stop = False

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
            self.listening = False
        else :
            self.dev = serial.Serial(portname, exclusive=True)
            time.sleep(0.8)
            # Verify that the device is an ADC-8 board running the
            # proper firmware
            msg = self.get_board_id()
            if msg.startswith("ADC-8"):
                self.connected = True
                self.listening = True
                self.set_status( 0 ) 
            else:
                self.dev = None
                self.connected = False
                self.listening = False
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
    
    def start_comm(self):
        counter = 0
        self.set_listening( True )
        while True:
            time.sleep(0.3)
            counter += 1
            if self.listening:
                if self.msg_input == None:
                    print("{}: Board is Listening".format(counter))
                elif isinstance( self.msg_input, str ):
                    print("{}: Board received \n    {}".format(counter, self.msg_input) )

                    write_msg = self.msg_input + "\n"
                    self.dev.write( write_msg.encode() )
                    ans_msg = self.dev.read(1500)
                    self.msg_out.emit( ans_msg.decode() )
                    self.msg_input = None

            else:
                if self.acquire_mode == "live":
                    self.start_live_view() 
                    self.set_listening( True )
                elif self.acquire_mode == "capture":
                    self.start_acquire()
                    self.set_listening( True )


            if self.connected == False:
                self.msg_out.emit( "Disconnecting..." )
                break
            
    def set_num_live_sample(self, value):
        self.num_live_sample = value

    def set_acquire_mode(self, value):
        if value == "live" or value == "capture":
            self.acquire_mode = value
        else :
            print("Invalid Acquire Mode")

    def set_stop(self, value):
        self.stop = value

    def set_listening(self, value):
        self.listening = value

    def set_connected(self, value):
        self.connected = value
    
    def send_command(self, msg):
        # Send Serial Command and Listen
        if self.connected:
            self.msg_input = msg
        else:
            self.msg_out = "\nConnect an ADC-8 Board to Start"
    
    def get_board_status(self):
        self.send_command("c")
        
    def set_all_gains(self, gain):
        self.send_command("g 0 {}".format(gain))
    
    def set_individual_gain(self, ch, gain):
        self.send_command("g {} {}".format(ch, gain))
    
    def set_sampling(self, sampling):
        self.send_command("s {}".format(sampling))

    def set_acquire_time( self, value ):
        self.acquire_time = value
    
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
    
    def start_live_view(self):

        self.set_status( 1 )
        self.msg_out.emit("Starting Live View")

        self.dev.write(f"b0\n".encode())
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
            return -1

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
            return -1

        blocksize = num * 3

        total_blocks = 0
        warned = False

        output_data = []
        # Receive and store the data
        cont = True
        while cont:
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
                if len(output_data) == self.num_live_sample+1:
                    self.live_data.emit( output_data )
                    output_data = []
                    break
            


            total_blocks += n // blocksize

            if self.stop == True:
                print("Termination requested")
                self.set_stop(False)
                break

        self.dev.write(b"\n")
        print("Transfer ended")
        print(total_blocks, "blocks received")

        self.dev.timeout = 0.01
        self.dev.read(1000)		# Flush any extra output

        self.set_status( 0 )
        self.set_stop( False )
        return output_data
    
    def start_acquire(self):

        self.set_status( 1 )
        self.msg_out.emit("Acquiring")

        

        self.dev.write(f"b{self.acquire_time}\n".encode())
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
            return -1

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
            return -1

        blocksize = num * 3

        total_blocks = 0
        warned = False

        output_data = []
        # Receive and store the data

        time_start = time.time()
        time_counter = 0
        cont = True
        while cont:
            time_cur = time.time()
            time_elapsed = math.floor(time_cur - time_start)
            if time_elapsed == time_counter:
                print(time_elapsed)
                time_counter += 1
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
                self.set_stop(False)
                break

        self.dev.write(b"\n")
        print("Transfer ended")
        print(total_blocks, "blocks received")

        self.live_data.emit( output_data )

        self.dev.timeout = 0.01
        self.dev.read(1000)		# Flush any extra output
        self.set_stop( False )
        self.set_status( 0 )
        return output_data

    def start_transfer(self, acq_time=4):
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
            return -1

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
            return -1

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
                self.set_stop(False)
                break

        self.dev.write(b"\n")
        print("Transfer ended")
        print(total_blocks, "blocks received")

        self.dev.timeout = 0.01
        self.dev.read(1000)		# Flush any extra output

        self.set_status( 2 )
        self.set_status( 0 )
        return output_data