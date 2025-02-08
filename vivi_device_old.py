import math, time, struct, sys
from PySide6.QtCore import (Signal, QObject, QThread)

if '-dev' in sys.argv:
    print( 'DEV MODE: Dummy Devices' )
    from dummy_device import list_ports
    import dummy_device as serial
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




    
    
    
  