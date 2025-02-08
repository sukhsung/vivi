import time,sys,struct
from datetime import datetime
from PySide6.QtCore import (Signal, QObject, QThread, QElapsedTimer)
import numpy as np
from math import floor

if '-verbose' in sys.argv:
    verbose = True
else:
    verbose = False

if '-request' in sys.argv:
    print_request = True
else:
    print_request = False

if '-dev' in sys.argv:
    print( 'DEV MODE: Dummy Devices' )
    from dummy_device import list_ports
    from dummy_device import Serial
else:
    from serial.tools.list_ports import comports as list_ports
    from serial import Serial
import socket
    
def get_port_list():
    port_list = [p.device for p in list_ports() if p.vid]
    port_list.append("RFC 2217")
    port_list.append("UDP")
    return port_list

class UDP_Device():
    def __init__( self, IP, PORT):
        print(IP)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
        self.IP = IP
        self.PORT = PORT

        self.write( '*IDN?\r\n'.encode('utf-8') )
        msg = self.read_until('\r\n') 

    def write( self, msg):
        self.sock.sendto( msg, ( self.IP, self.PORT))

    def read_until( self, msg):
        return self.sock.recvfrom(1024)[0]

    def close( self ):
        self.write( 'System.IP.Close\r\n'.encode('utf-8'))
        self.sock.close()

class Device(QObject):
    ## Common Signals
    signal_connected = Signal( bool )
    signal_update = Signal( object )
    signal_status = Signal( str)
    signal_received_msg = Signal (str)

    elapsed_time = Signal( int )

    def __init__( self ):
        # Inherit QObject
        super().__init__()
        self.encoding = 'utf-8'

        self.m_thread = None
        self.address = None
        self.connected = False
        self.device_type = None
        self.status = 'NOT-READY'
        self.time_interval = 0
        self.requests = []
        self.timer = Timer()

        self.lineending = '\r\n'
        
    ## Abstract Methods
    def dev_check( self ):
        print('ERROR: dev_check NOT IMPLEMENTED')
        pass

    def while_listening( self ):
        print('ERROR: while_listening NOT IMPLEMENTED')
        pass

    def initialize( self ):
        print('ERROR: initialize NOT IMPLEMENTED')

    def reset( self ):
        print('ERROR: reset NOT IMPLEMENTED')

    ## Common Concrete Method
    def start_comm( self ):
        self.timer.stop
        loop_timer = Timer()
        loop_timer.start()
        while True:
            loop_timer.restart()
            try:
                if self.status == "LISTENING":
                    if len( self.requests )==0:

                        self.while_listening()
                        dt = loop_timer.elapsed()
                        t_remain = self.time_interval-dt
                        if t_remain>0:
                            time.sleep(t_remain)

                    elif len( self.requests) >0:
                        self.process_request()

                elif self.status == "DISCONNECT":
                    print( "DISCONNECTING")
                    self.disconnect_device()
                    break
            except Exception as e:
                print(e)
                self.run_emergency()
                return
        
        self.set_status( "NOT-READY" )
        # Return Board to main thread before finishing
        self.moveToThread( self.thread_main )
        QThread.currentThread().quit()

    def connect_device( self, addr, baudrate=9600 ):
        if addr.startswith("UDP"):
            addr = addr.split(':')
            IP = addr[1]
            if len(addr)==2:
                port = 23
            elif len(addr) ==3:
                port = int(addr[2])
            self.device = UDP_Device( IP, port)
        else:
            self.device = Serial( addr, baudrate=baudrate, exclusive=True )
            self.device.timeout = 1

        
        if not self.dev_check():
            print( 'Invalid Device, closing')
            self.device.close()
        else:
            self.addr = addr
            self.initialize()
            self.set_connected( True )
            self.reset()

            self.set_status( 'LISTENING' )

    def disconnect_device( self ):
        self.reset()
        self.device.close()
        self.set_connected(False)
        self.address = None
        self.device_type = None
        self.status = 'NOT-READY'
        self.device = None

    def returnThreadToMain( self, main_thread ):
        self.moveToThread( main_thread )

    def set_connected( self, val ):
        self.connected = val
        self.signal_connected.emit( val )

    def run_emergency( self ):
        self.disconnect_device()
        self.set_status( "NOT-READY" )
        self.moveToThread( self.thread_main )
        QThread.currentThread().quit()
        
    def set_status( self, value ):
        self.status = value
        self.signal_status.emit( value )

    def set_request( self, request ):
        self.requests.append( request )

    def write( self, val ):
        if verbose:
            print("SENDING: "+ val)
        val = val+self.lineending
        self.device.write( val.encode( self.encoding) )

    def read( self ):
        # val = self.device.read_until( self.lineending.encode(self.encoding) ).decode(self.encoding).rstrip()
        val = self.device.read_all().decode(self.encoding)
        if verbose:
            print(val)
        return val
    
    def query( self,val, repeat=False, announce=False ):

        if repeat:
            self.signal_received_msg.emit(val)

        self.write(val)
        time.sleep( self.time_interval)
        msg = self.read()

        if announce:
            self.signal_received_msg.emit( msg )
        return msg

    def close( self ):
        self.set_status( "DISCONNECT")
        while self.status == "DISCONNECT":
            time.sleep( self.time_interval)
        self.device.close()

class ADC8( Device ):
    signal_setting = Signal( )
    live_data = Signal(list)
    acquire_data = Signal(list)
    def __init__(self):
        super().__init__()
        self.encoding = 'utf-8'
        self.lineending = '\n'
        self.time_interval = 0.1
        self.board_type = 'ADC-8x'
        self.NUM_CHANNELS = 0
        self.default_timeout = 0.01

    def dev_check(self):
        try:
            msg = self.get_board_id()
            if msg.startswith("ADC-8"):
                return True
        except:
            return False
        
    def get_board_id(self):
        """Return the board's identification string and store its serial_number."""
        self.device.write(b'\n')
        self.device.reset_input_buffer()
        self.device.read(1000)		# Wait for timeout

        self.device.write(b'*\n')
        id = self.device.read_until(size=80)
        n = id.rfind(b"   ")
        if n < 0:
            self.serial_number = ""
        else:
            # Remove the final '\n' and convert to an ASCII string
            self.serial_number = id[n + 3:-1].decode()
            
        return id[:n].decode()
    
    def while_listening(self):
        pass

    def reset(self):
        pass

    def initialize(self):

        self.NUM_CHANNELS = self.get_available_NUM_CHANNELS()
        self.set_board_type()

        self.adcs = []
        for i in range(self.NUM_CHANNELS):
            self.adcs.append( {'label': f"Ch {i+1}",
                               'gain':None,
                               'polarity':None,
                               'buffer':None,
                               'impedance':None})

        self.sampling = 0
        
        self.device.write(b'\n')

        self.get_board_status(emit=False)
        # self.set_status( "LISTENING" ) 

    def set_board_type( self):

        if self.board_type == "ADC-8x":
            self.HDR_LEN = 10 + self.NUM_CHANNELS * 2
            self.BIPOLAR = 2
            self.SCALE_24 = 1.0 / (1 << 24)
            self.VREF = 2.5 * 1.02		# Include 2% correction factor
            self.check_i_function()
        elif self.board_type == "ADC-8":
            self.HDR_LEN = 16
            self.BIPOLAR = 2
            self.SCALE_24 = 1.0 / (1 << 24)
            self.VREF = 2.5 * 1.02		# Include 2% correction factor
        elif self.board_type is None:
            self.NUM_CHANNELS = 0
            self.HDR_LEN = 0
            self.BIPOLAR = 2
            self.SCALE_24 = 0
            self.VREF = 0

    def check_m_function( self ):
        # Check whether m function exist
        self.device.read(1000)
        self.device.write(b'm\n')
        msg = self.device.read(10).decode(self.encoding).strip()
        if msg.startswith('Measuring'):
            self.m_function = True
            print( 'M exists')
            for i in range(10):
                time.sleep(1)
                print(i)
        else:
            self.m_function = False
            print( 'M does not exist')
        print( self.device.read(1000))

    def check_i_function( self ):
        # Check whether m function exist
        self.device.read(1000)
        self.device.write(b'i\n')
        msg = self.device.read(1000).decode()
        if msg.startswith('Impedance'):
            self.i_function = True
            print( 'I function exists')
        else:
            self.i_function = False
            print( 'I function does not exist')
        _ = self.device.read(1000)


    def get_available_NUM_CHANNELS( self ): 
        # Get number of channels
        self.device.write(b'c\n')
        msg = self.device.read(1000).decode()
        msg = msg.split('\n')
        msg = [x for x in msg if x.startswith('ADC ')]
        return len( msg )


    def process_request(self):
        req = self.requests.pop(0)
        if verbose or print_request:
            print( req )
        match req['func']:
            case 'send_command':
                self.send_command( req['value'])
                # print( req['value'])
                # print(val)

            case 'set_sampling':
                self.set_sampling( req['value'])

            case 'get_board_status':
                self.get_board_status()

            case 'set_ADC_settings':
                ch = req['ch']
                gain = req['gain']
                polarity = req['polarity']
                buffer = req['buffer']

                self.set_ADC_settings( ch,gain,polarity,buffer )

            case 'set_impedance':
                ch = req['ch']
                impedance = req['impedance']
                self.set_impedance(ch,impedance)

            case 'live':
                self.start_live_view()

            case 'acquire':
                self.start_acquire()
                
    def send_command( self, val,emit=True ):
        msg = self.query( val, announce=True)
        self.parse_answer(msg,emit)

    def set_sampling(self, sampling,emit=True):
        msg = self.query(f"s {sampling}", repeat=True, announce=True )
        self.parse_answer(msg,emit)
    
    def get_board_status(self,emit=True):
        msg = self.query("c", repeat=True,announce=True)
        self.parse_answer(msg,emit)

    def set_ADC_settings(self, ch, gain, polarity, buffer,emit=True):
        msg = self.query(f"g {ch} {gain} {polarity} {buffer}", repeat=True,announce=True)
        self.parse_answer(msg,emit)

    def set_impedance( self,ch,impedance,emit=True):
        msg = self.query( f"i {ch}{impedance}",repeat=True,announce=True)
        self.parse_answer(msg,emit)


    def start_live_view(self):
        self.stop = False

        self.device.write("b0\n".encode())
        self.device.timeout = 6
        self.device.read_until(b"+")		# Skip initial text
        sig = b""
        h = self.device.read(self.HDR_LEN)

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
            print("Invalid header received, transfer aborted")
            self.device.write(b"\n")
            self.set_status( "LISTENING" )
            return -1 
        
        num = 0
        gains = [chans[2 * i] for i in range(self.NUM_CHANNELS)]
        bipolar = [chans[2 * i + 1] & self.BIPOLAR for i in range(self.NUM_CHANNELS)]
        for g in gains:
            if g > 0:
                num += 1
        if num == 0:
            print("Header shows no active ADCs, transfer aborted")
            self.device.write(b"\n")
            self.set_status( "LISTENING" )
            return -1


        blocksize = num * 3

        total_blocks = 0
        warned = False

        output_data = []
        # Receive and store the data
        cont = True
        if self.board_type == 'ADC-8x' and self.NUM_CHANNELS==4:
            self.device.read(8)
        while cont:
            n = self.device.read(1)		# Read the buffer's length byte
            if len(n) == 0:
                print("Timeout")
                break
            n = n[0]
            if n == 0:
                print("End of data")
                break
            
            d = self.device.read(n)		# Read the buffer contents
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

            if self.stop:
                print( "Live View Termination Requested")
                self.live_data.emit( ["STOP"] )
                break

        self.device.write(b"\n")
        # print("Transfer ended")
        # print(f"{total_blocks} blocks received")

        self.device.timeout = self.default_timeout#0.01
        

        self.device.read(1000)		# Flush any extra output
        
        return output_data
    
    def start_acquire(self):
        self.stop = False

        self.device.write(f"b{self.acquire_time}\n".encode())
        self.device.timeout = 6
        self.device.read_until(b"+")		# Skip initial text
        sig = b""
        h = self.device.read(self.HDR_LEN)
        
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
            print("Invalid header received, transfer aborted")
            self.device.write(b"\n")
            self.set_request( "LISTEN" )
            return -1
        
        num = 0
        gains = [chans[2 * i] for i in range(self.NUM_CHANNELS)]
        bipolar = [chans[2 * i + 1] & self.BIPOLAR for i in range(self.NUM_CHANNELS)]
        for g in gains:
            if g > 0:
                num += 1
        if num == 0:
            print("Header shows no active ADCs, transfer aborted")
            self.device.write(b"\n")
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
            self.device.read(8)
        while cont:
            time_cur = time.time()
            time_elapsed = floor(time_cur - time_start)
            if time_elapsed == time_counter:
                self.elapsed_time.emit(time_elapsed)
                time_counter += 1
            n = self.device.read(1)		# Read the buffer's length byte
            
            if len(n) == 0:
                print("Timeout")
                break
            n = n[0]
            if n == 0:
                print("End of data")
                break

            d = self.device.read(n)		# Read the buffer contents
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

            if self.stop:
                print( "Acquisition Termination Requested")
                # self.acquire_data.emit( ["STOP"] )
                break

        if self.stop: 
            self.device.write(b"\n")
            self.acquire_data.emit( [-1] )
        else:
            self.device.write(b"\n")
            self.acquire_data.emit( output_data )

        self.device.timeout = self.default_timeout#0.01
        self.device.read(1000)		# Flush any extra output
        return output_data


    def set_stop(self):
        self.stop = True

    def parse_answer(self, msg, emit):
        setting_changed = False
        if msg.startswith("Sampling rate set to "):
            parts = msg.split(' ')
            self.sampling = float(parts[4])
            setting_changed = True

        elif msg.startswith("ADC "):
            ch = int(msg[4])
            i = ch -1
            if msg.endswith("disabled\n"):
                self.adcs[i]['gain'] = 0
            else:
                parts = msg.split(',')
                parts_gain = parts[0]
                parts_polarity = parts[1]
                parts_buffer = parts[2]

                parts_gain = parts_gain.split(' ')
                # ch = int(parts_gain[1])
                gain = int(parts_gain[5])


                self.adcs[i]['gain'] = gain

                parts_polarity = parts_polarity.split(' ')[-1]
                if parts_polarity=="(unipolar)":
                    self.adcs[i]['polarity'] = 1
                elif parts_polarity=="(bipolar)":
                    self.adcs[i]['polarity'] = 2

                parts_buffer = parts_buffer.split(' ')[-1]
                if parts_buffer.startswith( "buffered" ):
                    self.adcs[i]['buffer'] = 'b'
                elif parts_buffer.startswith( "unbuffered"):
                    self.adcs[i]['buffer'] = 'u'


            setting_changed = True
                
        elif msg.startswith("All ADCs "):
            if msg.endswith("disabled\n"):
                for i in range(self.NUM_CHANNELS):
                    self.adcs[i]['gain'] = 0
            else:


                parts = msg.split(',')
                parts_gain = parts[0]
                parts_polarity = parts[1]
                parts_buffer = parts[2]

                parts_gain = parts_gain.split(' ')

                gain = int(parts_gain[5])
                parts_polarity = parts_polarity.split(' ')[-1]

                parts_buffer = parts_buffer.split(' ')[-1]

                for i in range(self.NUM_CHANNELS):
                    self.adcs[i]['gain'] = gain

                    if parts_polarity=="(unipolar)":
                        self.adcs[i]['polarity'] = 1
                    elif parts_polarity=="(bipolar)":
                        self.adcs[i]['polarity'] = 2

                    if parts_buffer.startswith( "buffered" ):
                        self.adcs[i]['buffer'] = 'b'
                    elif parts_buffer.startswith( "unbuffered"):
                        self.adcs[i]['buffer'] = 'u'
            

            setting_changed = True

        elif msg.startswith("Impedance settings"):
            settings = msg.strip().split()[3:]

            for i in range(self.NUM_CHANNELS):
                self.adcs[i]['impedance'] = settings[i][1]

            setting_changed = True
            
        elif msg.startswith("\nCurrent settings"):
            lines = msg.split('\n')
            for line in lines:
                if line.startswith('Current settings:'):
                    self.sampling = float(line.split(' ')[-1])
                elif line.startswith('ADC '):
                    parts = line.split(': ')
                    ch = int(parts[0][-1])

                    if parts[1].startswith('disabled'):
                        self.adcs[ch-1]['gain'] = 0
                    else:
                        parts = parts[1].split(', ')

                        gain = int(parts[0].split(' ')[1])
                        polarity = parts[1]
                        if polarity == 'bipolar':
                            polarity = 2
                        else:
                            polarity = 1

                        buffer = parts[2]
                        if buffer == 'unbuffered':
                            buffer = 'u'
                        else:
                            buffer = 'b'

                        if len(parts)==4:
                            impedance = parts[3][-1]
                        else:
                            impedance = ''
                        
                        self.adcs[ch-1]['gain'] = gain
                        self.adcs[ch-1]['polarity'] = polarity
                        self.adcs[ch-1]['buffer'] = buffer
                        self.adcs[ch-1]['impedance'] = impedance

            setting_changed = True

        else:
            print("CAN'T PARSE")
            print(msg)

        if setting_changed and emit:
            self.signal_setting.emit()


    def set_num_live_sample(self, value):
        self.num_live_sample = value
    
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

class Timer():
    def __init__(self):
        self.t0 = False
        self.started = False
    
    def start(self):
        self.t0 = datetime.now()
        self.started = True

    def elapsed(self):
        return (datetime.now() - self.t0).total_seconds()
    
    def elapsed_n_now(self):
        now = datetime.now() 
        return (now - self.t0).total_seconds(), now
    
    def stop(self):
        self.t0 = False
        self.started = False

    def restart(self):
        self.t0 = datetime.now()
    
