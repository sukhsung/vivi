import math, time, struct, sys
from PySide6.QtCore import (Signal, QObject, QThread)

if '-dev' in sys.argv:
    print( 'DEV MODE: Dummy Devices' )
    from dummy_serial import list_ports
    import dummy_serial as serial
else:
    from serial.tools.list_ports import comports as list_ports
    import serial

"""Program to store continuous data readings from an ADC-8 board."""
"""Based off of adc8-transfer.py and noise-density.py"""
def get_port_list():
    """
    Return a list of USB serial port devices.

    Entries in the list are ListPortInfo objects from the
    serial.tools.list_ports module.  Fields of interest include:

        device:  The device's full path name.
        vid:     The device's USB vendor ID value.
        pid:     The device's USB product ID value.
    """
    port_list = [p.device for p in list_ports() if p.vid]
    port_list.append("RFC 2217")
    return port_list

class Board(QObject):
    status = str
    status_signal = Signal(str)
    status_possible = ["NOT-READY", "LISTENING", "LIVE", "ACQUIRE", "STOPPING", "DISCONNECT"]

    request = None
    request_possible = ["LISTEN", "LIVE", "ACQUIRE","STOP","DISCONNECT"]

    msg_out = Signal( str )
    live_data = Signal( list )
    acquire_data = Signal( list )
    elapsed_time = Signal( int )
    setting_changed = Signal()

    connected = False
    connected_signal = Signal( bool )

    gains = []
    sampling = 0
    labels = []

    portname = None

    vivi_thread = None

    """Represent a single ADC-8 board."""
    def __init__(self):
        """
        Initialize an ADC-8 Board object.
        """
        super().__init__() #Inherit QObject

        self.set_board_type()

        self.dev = None
        self.msg_input = []
        self.status = "NOT-READY"
        self.connected = False

    def connect_board( self, portname ):
        """  
        portname is the name of the board's USB serial port device, 
        which will be opened in exclusive mode.
        """
        self.msg_out.emit("Connecting...")
        try:
            if portname.startswith("rfc2217://"):
                # Serial over Ethernet (RFC2217)
                self.default_timeout = 0.5
                self.dev = serial.serial_for_url(portname, exclusive=True)
            else:
                # True Serial (pyserial)
                self.default_timeout = 0.01
                self.dev = serial.Serial(portname, exclusive=True)
            time.sleep( 0.8 )

            # Run Device Check
            dev_check_result = self.dev_check()
            if not dev_check_result:
                self.dev = None
                self.msg_out.emit("Device is not an ADC-8 board")
                self.set_status( "NOT-READY" ) 
                self.set_connected( False )
                return False
            else:
                self.portname = portname
                self.set_board_type(dev_check_result)
                self.set_connected( True )
        except:
            self.portname = None
            self.dev = None
            self.set_status( "NOT-READY" ) 
            self.set_connected( False )
            return False
            
    def dev_check(self):
        msg = self.get_board_id()

        if msg.startswith("ADC-8x"):
            return "ADC-8x"
        elif msg.startswith("ADC-8"):
            return "ADC-8"
        else:
            return False
            
    def set_board_type( self, board_type=None ):
        self.board_type = board_type
        if board_type == "ADC-8x":
            
            self.NUM_CHANNELS = self.get_available_NUM_CHANNELS()
            self.HDR_LEN = 10 + self.NUM_CHANNELS * 2
            self.BIPOLAR = 2
            self.SCALE_24 = 1.0 / (1 << 24)
            self.VREF = 2.5 * 1.02		# Include 2% correction factor
        elif board_type == "ADC-8":
            self.NUM_CHANNELS = self.get_available_NUM_CHANNELS()
            self.HDR_LEN = 16
            self.BIPOLAR = 2
            self.SCALE_24 = 1.0 / (1 << 24)
            self.VREF = 2.5 * 1.02		# Include 2% correction factor
        elif board_type is None:
            self.NUM_CHANNELS = 0
            self.HDR_LEN = 0
            self.BIPOLAR = 2
            self.SCALE_24 = 0
            self.VREF = 0

    def returnThreadToMain( self, main_thread ):
        self.moveToThread( main_thread )

    def close_board( self ):
        if self.status == "LIVE" or self.status == "ACQUIRE":
            self.set_request( "STOP" )
            while self.status == "STOPPING":
                time.sleep(0.01)

        time.sleep(0.01)
        self.set_status( "DISCONNECT")
        self.send_command( "q" )

        self.dev.close()
        self.dev = None
        self.set_status( "NOT-READY")
        self.set_connected(False)
        self.msg_input = []
        self.board_type = None
        self.portname = None

    def initialize( self ):
        self.dev.write(b'\n')

        boardmsg = "Connected to "+self.board_type+" board: "+self.portname +"\n"
        self.msg_out.emit( boardmsg )
        self.gains = [1 for x in range( self.NUM_CHANNELS) ]
        self.labels = [f"Ch {x+1}" for x in range( self.NUM_CHANNELS)]
        self.polarity = [2 for x in range( self.NUM_CHANNELS) ]
        self.buffer = [0 for x in range( self.NUM_CHANNELS) ]
        self.sampling = 0#sampling#self.init_sampling
        
        self.set_status( "LISTENING" ) 


    def get_available_NUM_CHANNELS( self ): 
        # Get number of channels
        self.dev.write(b'c\n')
        msg = self.dev.read(1000).decode()
        msg = msg.split('\n')
        msg = [x for x in msg if x.startswith('ADC ')]
        return len( msg )

    def set_connected( self,connected ):
        self.connected = connected
        self.connected_signal.emit(connected)

    def set_status( self, new_status ):
        if new_status not in self.status_possible:
            print( "INVALID STATUS SIGNAL")
        else:
            self.status = new_status
            self.status_signal.emit( new_status )

    def set_request( self, new_request ):
        if new_request in self.request_possible or new_request is None:
            self.request = new_request
        else:
            print( "INVALID REQUEST")

    def __repr__(self):
        """String representation of adc8 Board."""

        return "<Board id=0x{:X}, port={!r}>".format(id(self), self.dev.port)

    def get_board_id(self):
        """Return the board's identification string and store its serial_number."""
        self.dev.timeout = self.default_timeout#0.01
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
        while self.connected:
            counter += 1
            try:
                if self.status == "LISTENING":
                    # Check for request
                    if self.request is None:
                        # See if there's any message to pass
                        if len(self.msg_input)>0:
                            cur_msg = self.msg_input.pop(0)
                            self.msg_out.emit( cur_msg )
                            write_msg = cur_msg + "\n"

                            self.dev.write( write_msg.encode() )
                            ans_msg = self.dev.read(1500).decode()
                            self.parse_answer( ans_msg )
                            self.msg_out.emit( ans_msg )
                        else:
                        # Might as well check for connectivity
                            time.sleep(0.01) #Prevent talking too often
                            self.dev.write( '*'.encode())
                            ans_msg = self.dev.read(1500).decode()
                            if not ans_msg.startswith('ADC'):
                                self.run_emergency()
                                return
                    elif self.request == "LIVE":
                        self.start_live_view()
                        self.set_status( "LISTENING" )
                        self.set_request(None)
                    elif self.request == "ACQUIRE":
                        self.start_acquire()
                        self.set_status( "LISTENING" )
                        self.set_request(None)
                    elif self.request == "DISCONNECT":
                        self.set_request(None)
                        break
            except Exception as e:
                print(e)
                self.run_emergency()
                return
                        
        
        self.msg_out.emit( "Disconnecting..." )
        self.close_board()
        self.moveToThread( self.thread_main )
        QThread.currentThread().quit()

    def run_emergency(self):
        print("Something Wrong, closing board")
        self.close_board()
        self.set_connected( False)
        self.set_status("NOT-READY")
        self.moveToThread( self.thread_main )
        QThread.currentThread().quit()

    def parse_answer(self, msg):
        if msg.startswith("Sampling rate set to "):
            parts = msg.split(' ')
            self.sampling = float(parts[4])
            self.setting_changed.emit()
        elif msg.startswith("ADC "):
            parts = msg.split(',')
            parts_gain = parts[0]
            parts_polarity = parts[1]
            parts_buffer = parts[2]

            parts_gain = parts_gain.split(' ')
            ch = int(parts_gain[1])-1
            gain = int(parts_gain[5])
            self.gains[ch] = gain

            parts_polarity = parts_polarity.split(' ')[-1]
            if parts_polarity=="(unipolar)":
                self.polarity[ch] = 1
            elif parts_polarity=="(bipolar)":
                self.polarity[ch] = 2
            
            parts_buffer = parts_buffer.split(' ')[-1]
            if parts_buffer.startswith( "buffered" ):
                self.buffer[ch] = 1
            elif parts_buffer.startswith( "unbuffered"):
                self.buffer[ch] = 0

        elif msg.startswith("All ADCs "):
            parts = msg.split(',')
            parts_gain = parts[0]
            parts_polarity = parts[1]
            parts_buffer = parts[2]

            parts_gain = parts_gain.split(' ')

            gain = int(parts_gain[5])
            self.gains = [gain for i in range(self.NUM_CHANNELS)]

            parts_polarity = parts_polarity.split(' ')[-1]
            if parts_polarity=="(unipolar)":
                self.polarity = [1 for i in range(self.NUM_CHANNELS)]
            elif parts_polarity=="(bipolar)":
                self.polarity = [2 for i in range(self.NUM_CHANNELS)]
            
            parts_buffer = parts_buffer.split(' ')[-1]
            if parts_buffer.startswith( "buffered" ):
                self.buffer = [1 for i in range(self.NUM_CHANNELS)]
            elif parts_buffer.startswith( "unbuffered"):
                self.buffer = [0 for i in range(self.NUM_CHANNELS)]


            self.setting_changed.emit()


            
    def set_num_live_sample(self, value):
        self.num_live_sample = value

    def send_command(self, msg):
        # Send Serial Command and Listen

        if self.status == "LISTENING":
            self.msg_input.append(msg)
        else:
            self.msg_out.emit( "Connect an ADC-8 Board to Start" )
    
    def get_board_status(self):
        self.send_command("c")
            
    def set_ADC_settings(self, ch, gain, polarity, buffer):
        self.send_command(f"g {ch} {gain} {polarity} {buffer}")
    
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
        self.set_status("LIVE")

        self.dev.write("b0\n".encode())
        self.dev.timeout = 6
        a=self.dev.read_until(b"+")		# Skip initial text
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
        if self.board_type == 'ADC-8x' and self.NUM_CHANNELS==4:
            self.dev.read(8)
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

            if self.request == "STOP":
                self.msg_out.emit("Termination requested")
                self.set_status( "STOPPING")
                break

        self.dev.write(b"\n")
        self.msg_out.emit("Transfer ended")
        self.msg_out.emit(f"{total_blocks} blocks received")

        self.dev.timeout = self.default_timeout#0.01
        

        self.dev.read(1000)		# Flush any extra output
        
        return output_data
    
    def start_acquire(self):
        self.msg_out.emit("Acquiring")
        self.set_status("ACQUIRE")

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
            self.set_request( "LISTEN" )
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
            self.set_status( "LISTEN" )
            return -1
        

        blocksize = num * 3

        total_blocks = 0
        warned = False

        output_data = []
        # Receive and store the data


        time_start = time.time()
        time_counter = 0
        cont = True
        if self.board_type == 'ADC-8x' and self.NUM_CHANNELS==4:
            self.dev.read(8)
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

            if self.request == "STOP":
                self.msg_out.emit("Termination requested")
                self.set_status( "STOPPING")
                break

        if self.status == "STOPPING":     
            self.dev.write(b"\n")
            self.acquire_data.emit( [-1] )
        else:
            self.dev.write(b"\n")
            self.msg_out.emit("Transfer ended")
            self.msg_out.emit(f"{total_blocks} blocks received")

            self.acquire_data.emit( output_data )

        self.dev.timeout = self.default_timeout#0.01
        self.dev.read(1000)		# Flush any extra output
        return output_data
