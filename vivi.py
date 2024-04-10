# auto-transfer.py
"""Program to store continuous data readings from an ADC-8 board."""
"""Based off of adc8-transfer.py and noise-density.py"""
import serial, math, time, struct
from PyQt6.QtCore import (pyqtSignal, QObject)


class Board(QObject):
    status = str
    status_signal = pyqtSignal(str)
    # "NOT-READY", "LISTENING", "LIVE", "ACQUIRE", "STOPPING", "DISCONNECT"

    msg_out = pyqtSignal( str )
    live_data = pyqtSignal( list )
    acquire_data = pyqtSignal( list )
    elapsed_time = pyqtSignal( int )
    setting_changed = pyqtSignal()

    """Represent a single ADC-8 board."""
    def __init__(self):
        """
        Initialize an ADC-8 Board object.
        """
        super().__init__() #Inherit QObject

        self.set_board_type()

        self.dev = None
        self.msg_input = None
        self.status = "DISCONNECT"

    def connect_board( self, portname ):
        """  
        portname is the name of the board's USB serial port device, 
        which will be opened in exclusive mode.
        """
        self.msg_out.emit("Connecting...")
        if portname is None:
            #self.msg_out.emit("No serial port name specified")
            self.dev = None
            self.set_status( "NOT-READY" ) 
            return False
        else :
            self.dev = serial.Serial(portname, exclusive=True)
            time.sleep(0.8)
            # Verify that the device is an ADC-8 board running the
            # proper firmware
            msg = self.get_board_id()
            if msg.startswith("ADC-8x"):
                self.set_board_type("ADC-8x")
                self.dev.write(b'\n')

                boardmsg = "Connected to ADC-8x board: "+ portname +"\n"
                # boardmsg += "    Serial number: "+ self.serial_number+"\n"
                self.msg_out.emit( boardmsg )
                self.gains = [128, 128, 128, 128, 128, 128, 128, 128]
                self.sampling = 400
                self.set_status( "LISTENING" ) 
                return True
            elif msg.startswith("ADC-8"):
                self.set_board_type("ADC-8")
                self.dev.write(b'\n')

                boardmsg = "Connected to ADC-8 board: "+ portname +"\n"
                # boardmsg += "    Serial number: "+ self.serial_number+"\n"
                self.msg_out.emit( boardmsg )
                self.gains = [128, 128, 128, 128]
                self.sampling = 400
                self.set_status( "LISTENING" ) 
                return True
            else:
                print( msg)
                self.dev = None
                self.msg_out.emit("Device is not an ADC-8 board")
                self.set_status( "NOT-READY" ) 
                return False
            
    def set_board_type( self, board_type=None ):
        self.board_type = board_type
        if board_type == "ADC-8x":
            self.NUM_CHANNELS = 8
            self.HDR_LEN = 10 + self.NUM_CHANNELS * 2
            self.BIPOLAR = 2
            self.SCALE_24 = 1.0 / (1 << 24)
            self.VREF = 2.5 * 1.02		# Include 2% correction factor
        elif board_type == "ADC-8":
            self.NUM_CHANNELS = 4
            self.HDR_LEN = 16
            self.BIPOLAR = 2
            self.SCALE_24 = 1.0 / (1 << 24)
            self.VREF = 2.5 * 1.02		# Include 2% correction factor
        elif board_type is None:
            self.NUM_CHANNELS = 0
            self.HDR_LEN = 0
            self.BIPOLAR = 20
            self.SCALE_24 = 0
            self.VREF = 0

    def returnThreadToMain( self, main_thread ):
        self.moveToThread( main_thread )


    def close_board( self ):
        if self.status == "LIVE" or self.status == "ACQUIRE":
            self.set_status( "STOPPING" )
            while self.status == "STOPPING":
                time.sleep(0.01)
        self.send_command( "q" )
        time.sleep(0.01)
        self.set_status( "DISCONNECT")
        self.dev.close()
        self.dev = None

    def init_settings( self ):
        self.msg_out.emit('Setting Initial Settings')
        self.set_all_gains( 128 )
        time.sleep(0.1)
        self.set_sampling( 400 )

    def set_status( self, value ):
        if not (value=="LISTENING" or value=="NOT-READY" or value=="STOPPING" or value=="LIVE" or value=="ACQUIRE" or value=="DISCONNECT"):
            print( "INVALID STATUS SIGNAL")
        else:
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
        while True:
            counter += 1
            cur_status = self.status
            try:
                if cur_status == "LISTENING":
                    if not self.msg_input == None and isinstance( self.msg_input, str ):
                        self.msg_out.emit( self.msg_input )
                        write_msg = self.msg_input + "\n"

                        self.dev.write( write_msg.encode() )
                        ans_msg = self.dev.read(1500).decode()
                        self.parse_answer( ans_msg )
                        self.msg_out.emit( ans_msg )
                        self.msg_input = None
                elif cur_status == "LIVE":
                    self.start_live_view()
                elif cur_status == "ACQUIRE":
                    self.start_acquire()
            except Exception as e:
                print(e)
                self.run_emergency()
                return
                        
            if cur_status == "DISCONNECT":
                self.msg_out.emit( "Disconnecting..." )
                break
        
        self.set_status( "NOT-READY" )
        # Return Board to main thread before finishing
        self.moveToThread( self.thread_main )

    def run_emergency(self):
        print("Something Wrong, closing board")
        self.dev.close()
        self.dev = None
        self.moveToThread( self.thread_main )
        self.set_status("DISCONNECT")

    def parse_answer(self, msg):
        if msg.startswith("Sampling rate set to "):
            parts = msg.split(' ')
            self.sampling = float(parts[4])
            self.setting_changed.emit()
        elif msg.startswith("All ADCs set to gain "):
            parts = msg.split(' ')
            gain = int(parts[5][:-1])
            self.gains = [gain for i in range(4) ]
            self.setting_changed.emit()
        elif msg.startswith("ADC "):
            parts = msg.split(' ')
            ch = int(parts[1])
            gain = int(parts[5][:-1])
            self.gains[ch-1] = gain
            self.setting_changed.emit()


            
    def set_num_live_sample(self, value):
        self.num_live_sample = value

    def send_command(self, msg):
        # Send Serial Command and Listen
        if self.status == "LISTENING":
            self.msg_input = msg
        else:
            self.msg_out = "\nConnect an ADC-8 Board to Start"
    
    def get_board_status(self):
        self.send_command("c")
        
    def set_all_gains(self, gain):
        self.send_command(f"g 0 {gain}")
    
    def set_individual_gain(self, ch, gain):
        self.send_command(f"g {ch} {gain}")
    
    def set_sampling(self, sampling):
        self.send_command(f"s {sampling}")

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
            x = (block[j] + (block[j+1] << 8) + (block[j+2] << 16)) * self.SCALE_24
            if bipolar[i]:
                x = 2. * x - 1.
            volts[v] = round(x * self.VREF / g, 9)
            j += 3
            v += 1
        return volts
    
    def start_live_view(self):
        self.msg_out.emit("Starting Live View")

        self.dev.write(f"b0\n".encode())
        self.dev.timeout = 6
        self.dev.read_until(b"+")		# Skip initial text
        sig = b""
        h = self.dev.read(self.HDR_LEN)
        
        if len(h) == self.HDR_LEN:
            if self.board_type == 'ADC-8':
                fmt = f"<4sHBB {2 * self.NUM_CHANNELS}B"
            elif self.board_type == 'ADC-8x':
                fmt = f"<8sH {2 * self.NUM_CHANNELS}B"
            hdr = struct.unpack(fmt, h)
            sig = hdr[0]		# The signature
         
        if sig == b"ADC8":
            chans = hdr[4:]			# The ADC channel entries
        elif sig == b"ADC8x-1.":
            chans = hdr[2:]			# The ADC channel entries
        else:
            self.msg_out.emit("Invalid header received, transfer aborted")
            self.dev.write(b"\n")
            self.set_status( "LISTENING" )
            return -1

        num = 0
        gains = [chans[2 * i] for i in range(self.NUM_CHANNELS)]
        bipolar = [chans[2 * i + 1] & self.BIPOLAR for i in range(self.NUM_CHANNELS)]
        for g in gains:
            if g > 0:
                num += 1
        if num == 0:
            self.msg_out.emit("Header shows no active ADCs, transfer aborted")
            self.dev.write(b"\n")
            self.set_status( "LISTENING" )
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
                self.msg_out.emit("Timeout")
                break
            n = n[0]
            if n == 0:
                self.msg_out.emit("End of data")
                break

            d = self.dev.read(n)		# Read the buffer contents
            if len(d) < n:
                self.msg_out.emit("Short data buffer received")
                break
            
            if n % blocksize != 0:
                if not warned:
                    self.msg_out.emit("Warning: Invalid buffer length", n)
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

            if self.status == "STOPPING":
                self.msg_out.emit("Termination requested")
                break

        self.dev.write(b"\n")
        self.msg_out.emit("Transfer ended")
        self.msg_out.emit(f"{total_blocks} blocks received")

        self.dev.timeout = 0.01
        self.dev.read(1000)		# Flush any extra output
        
        self.set_status( "LISTENING" )
        return output_data
    
    def start_acquire(self):
        self.msg_out.emit("Acquiring")

        self.dev.write(f"b{self.acquire_time}\n".encode())
        self.dev.timeout = 6
        self.dev.read_until(b"+")		# Skip initial text

        sig = b""
        h = self.dev.read(self.HDR_LEN)
        
        if len(h) == self.HDR_LEN:
            if self.board_type == 'ADC-8':
                fmt = f"<4sHBB {2 * self.NUM_CHANNELS}B"
            elif self.board_type == 'ADC-8x':
                fmt = f"<8sH {2 * self.NUM_CHANNELS}B"
            hdr = struct.unpack(fmt, h)
            sig = hdr[0]		# The signature
         
        if sig == b"ADC8":
            chans = hdr[4:]			# The ADC channel entries
        elif sig == b"ADC8x-1.":
            chans = hdr[2:]			# The ADC channel entries
        else:
            self.msg_out.emit("Invalid header received, transfer aborted")
            self.dev.write(b"\n")
            self.set_status( "LISTENING" )
            return -1
        
        num = 0
        gains = [chans[2 * i] for i in range(self.NUM_CHANNELS)]
        bipolar = [chans[2 * i + 1] & self.BIPOLAR for i in range(self.NUM_CHANNELS)]
        for g in gains:
            if g > 0:
                num += 1
        if num == 0:
            self.msg_out.emit("Header shows no active ADCs, transfer aborted")
            self.dev.write(b"\n")
            self.set_status( "LISTENING" )
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
                self.elapsed_time.emit(time_elapsed)
                time_counter += 1
            n = self.dev.read(1)		# Read the buffer's length byte
            if len(n) == 0:
                self.msg_out.emit("Timeout")
                break
            n = n[0]
            if n == 0:
                self.msg_out.emit("End of data")
                break

            d = self.dev.read(n)		# Read the buffer contents
            if len(d) < n:
                self.msg_out.emit("Short data buffer received")
                break
            
            if n % blocksize != 0:
                if not warned:
                    self.msg_out.emit("Warning: Invalid buffer length", n)
                    warned = True
                n -= n % blocksize

            for i in range(0, n, blocksize):
                # Convert the block data to floats and write them out
                volts = self.convert_values(d[i:i + blocksize], gains, bipolar, num)
                output_data.append ( volts )

            total_blocks += n // blocksize

            if self.status == "STOPPING":
                self.msg_out.emit("Termination requested")
                break

        if self.status == "STOPPING":     
            self.dev.write(b"\n")
            self.acquire_data.emit( [-1] )
        else:
            self.dev.write(b"\n")
            self.msg_out.emit("Transfer ended")
            self.msg_out.emit(f"{total_blocks} blocks received")

            self.acquire_data.emit( output_data )

        self.dev.timeout = 0.01
        self.dev.read(1000)		# Flush any extra output
        self.set_status( "LISTENING" )
        return output_data
