
def list_ports():
    return [dummy_device()]
    
class dummy_device():
    device = "DUMMY DEVICE"
    vid    = 'VENDOR ID'
    pid    = 'PRODUCT ID'


class Serial():
    def __init__(self, portname, exclusive=True):
        super().__init__()
        self.portname = portname
        self.sampling = 400
        self.NUM_CHANNEL = 8
        self.gains = [1 for x in range(self.NUM_CHANNEL)]
        self.identifier = "ADC-8x FAUX DEVICE\nNO SERIAL NUMBER"
        
    def reset_input_buffer(self):
        self.buffer = ""
    def write(self,msg):
        msg = msg.decode()
        if msg.startswith('c'):
            self.buffer = self.show_current_settings()
        elif msg.startswith('*'):
            self.buffer = self.print_id()
        elif msg.startswith('s'):
            msg = msg.split(' ')
            self.sampling = int(msg[1])
        elif msg.startswith('g'):
            msg = msg.split(' ')
            channels = int(msg[1])
            gain = int(msg[2])
            if channels == 0:
                self.gains = [gain for x in range(self.NUM_CHANNEL)]
            else:
                self.gains[channels-1] = gain
                print( self.gains)
        elif msg.startswith('b'):
            self.begin_data_collection()
    
    def show_current_settings(self):
        msg_out =  "\nCurrent settings:  Sampling rate %.2f\n" % self.sampling
        msg_out += "\nExtra on-board channel-4 input enabled\n"
        for i in range(self.NUM_CHANNEL):
            msg_out += "ADC %d " % (i+1)
            if self.gains[i] == 0:
                msg_out += "disabled\n"
            else:
                msg_out += "gain %d, bipolar, unbuffered\n" % self.gains[i]
        return msg_out

    def print_id(self):
        msg_id = "ADC-8x driver version FAUX\n"
        msg_id += "SAMD21 ID: XXXX-XXXX-XXXX-XXXX\n"
        msg_id += "Flash ID:  XXXXXXXX-XXXX\n"
        return msg_id

    def close(self):
        print('CLOSED')
    def read(self, n):
        if n < len(self.buffer):
            msg_out = self.buffer[:n]
            self.buffer = self.buffer[n:]
        else:
            msg_out = self.buffer
            self.buffer = ""

        
        return msg_out.encode()
    
    def read_until(self, size):
        if size < len(self.buffer):
            msg_out = self.buffer[:size]
        else:
            msg_out = self.buffer
        
        return msg_out.encode()


        