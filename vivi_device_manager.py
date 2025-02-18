import time
import vivi_device
from PySide6.QtCore import QThread,Qt
from PySide6.QtWidgets import QGroupBox, QWidget, QVBoxLayout,QGridLayout,QLabel,QSpacerItem,QPushButton,QSizePolicy
from UI_makers.vivi_makeUI_deviceManager import Ui_device_manager
from functools import partial
from vivi_adc_setting import adc_setting, adc_full_setting
# from vivi_adc

class device_manager():
    def __init__(self, 
                 parent,
                 name,
                 device, 
                 ui_stack,
                 layout_adc,
                 console,
                 default_ip):
        
        self.name = name
        self.device = device
        self.thread_main = parent.thread_main
        self.parent = parent
        self.layout_adc = layout_adc
        self.UI_device_manager = Ui_device_manager()
        widget = QGroupBox()
        self.device_index = parent.Ui_device_dialog.layout_dev.count()-1
        parent.Ui_device_dialog.layout_dev.insertWidget( self.device_index, widget )
        self.UI_device_manager.setupUi( widget )
        self.UI_device_manager.label_deviceName.setText( name )
        
        self.ui_stack = ui_stack
        self.console = console

        self.protocol = 'TCP'
        self.serial_port = None
        self.baudrate = 9600


        self.UI_device_manager.CB_protocol.activated.connect( self.on_select_protocol )
        self.UI_device_manager.CB_deviceList.activated.connect(self.on_device_selected)
        self.UI_device_manager.PB_connect.clicked.connect( self.on_click_connect )
        self.UI_device_manager.PB_refresh.clicked.connect( self.update_port_list )

        self.UI_device_manager.CB_protocol.setCurrentIndex(0)

        self.UI_device_manager.CB_Baud.setCurrentIndex(6)
        self.baudrate = int( self.UI_device_manager.CB_Baud.currentText())
        self.UI_device_manager.CB_Baud.currentIndexChanged.connect( self.on_select_baud )

        self.UI_device_manager.CB_deviceList.setVisible(False)
        self.UI_device_manager.LE_addr.setText( f"{default_ip}:48105")
        self.UI_device_manager.LE_addr.setVisible( True )
        self.UI_device_manager.PB_refresh.setVisible( False )

        # Console Related
        self.console.signal_send_command.connect( self.console_send )
        self.device.signal_received_msg.connect( self.console.msg_received )

        #
        self.make_dlg_adc()

        self.update_port_list()
        self.on_device_selected()
        self.make_disabled_panel()
        self.ui_stack.setCurrentIndex(0)
        self.device.signal_connected.connect( self.received_device_connected )
        self.device.signal_setting.connect( self.received_setting_changed )

        self.LE_sampling = self.parent.LE_sampling
        self.LE_sampling.returnPressed.connect( self.set_sampling )

        self.CB_allGains = self.parent.CB_allGains
        self.CB_allGains.activated.connect( self.set_all_gains )

    def allow_connect( self ):
        if self.baudrate is None:
            return False
        
        if self.protocol == "Serial":
            if self.serial_port == None:
                return False
        return True

    def on_select_protocol( self ):
        self.protocol = self.UI_device_manager.CB_protocol.currentText()
        if self.protocol == "Serial":
            self.UI_device_manager.LE_addr.setVisible( False )
            self.UI_device_manager.CB_deviceList.setVisible( True )
            self.UI_device_manager.PB_refresh.setVisible( True )
        else:
            self.UI_device_manager.LE_addr.setVisible( True )
            self.UI_device_manager.CB_deviceList.setVisible( False )
            self.UI_device_manager.PB_refresh.setVisible( False )
        
        self.UI_device_manager.PB_connect.setEnabled( self.allow_connect() )


    def on_select_baud( self ):
        if self.UI_device_manager.CB_Baud.currentIndex() == 0:
            self.baudrate = None
        else:
            self.baudrate = int(self.UI_device_manager.CB_Baud.currentText())

        self.UI_device_manager.PB_connect.setEnabled( self.allow_connect() )


    def on_boardType_selected( self ):
        self.device.board_type = self.UI_device_manager.CB_boardType.currentText()

    def make_disabled_panel(self):
        self.layout_off = QVBoxLayout(self.ui_stack.widget(0))

        spacer_1 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        spacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layout_off.addItem(spacer_1)
        off_label = QLabel()
        off_label.setText( "Connect to a "+self.name)
        off_label.setAlignment(Qt.AlignCenter)
        self.layout_off.addWidget(off_label)

        self.PB_open_deviceManager = QPushButton("Open Device Manager")
        self.PB_open_deviceManager.setObjectName("PB_open_deviceManager")
        self.layout_off.addWidget(self.PB_open_deviceManager, 0, Qt.AlignHCenter)

        self.layout_off.addItem(spacer_2)
        self.PB_open_deviceManager.clicked.connect( self.parent.open_device_dialog )

    def on_device_selected(self):
        self.serial_port = self.UI_device_manager.CB_deviceList.currentText()
        if self.serial_port == 'No Serial Ports':
            self.serial_port = None

        self.UI_device_manager.PB_connect.setEnabled( self.allow_connect() )
            

    def on_click_connect(self):
        if self.UI_device_manager.PB_connect.text() == "Connect":
            self.connect_device()
        elif self.UI_device_manager.PB_connect.text() == "Disconnect":
            self.disconnect_device()

    def update_port_list(self):
        # Remove Current List
        for i in range(self.UI_device_manager.CB_deviceList.count()):
            self.UI_device_manager.CB_deviceList.removeItem(0)
        # Update Port List
        self.port_list = vivi_device.get_port_list()
        self.UI_device_manager.CB_deviceList.addItems( self.port_list )
        # Enable Address field as necesary
        self.on_device_selected()

    def connect_device(self):
        if self.protocol == 'Serial':
            portname = self.serial_port
        else:
            portname = self.UI_device_manager.LE_addr.text()

        self.device.connect_device( self.protocol, portname,baudrate=self.baudrate )


    def disconnect_device(self):
        self.device.set_status("DISCONNECT")
        t = time.time()
        while self.device.connected and (time.time()-t<1):
            time.sleep(0.01)

    def received_device_connected( self, val ):
        if val: # CONNECTED
            self.UI_device_manager.PB_connect.setText( "Disconnect" )
            self.UI_device_manager.label_deviceName.setText( self.name+": Connected")
            self.UI_device_manager.PB_refresh.setEnabled( False )
            self.console.setEnabled( True )
            self.UI_device_manager.CB_deviceList.setEnabled( False )
            self.UI_device_manager.CB_boardType.setEnabled( False )
            self.ui_stack.setCurrentIndex(1)

            self.start_device()
            # self.device.initialize()
            self.make_panel_adc()
            self.get_board_status()
            self.set_ADC_settings(0,128,2,'u')
            self.set_sampling()


            
                        
        else: # Disconnected
            self.UI_device_manager.PB_connect.setText( "Connect" )
            self.UI_device_manager.label_deviceName.setText( self.name+": Disconnected")
            self.UI_device_manager.PB_refresh.setEnabled( True )
            self.console.setEnabled( False )
            self.update_port_list()
            self.UI_device_manager.CB_deviceList.setEnabled( True )
            self.UI_device_manager.CB_boardType.setEnabled( True )
            self.ui_stack.setCurrentIndex(0)
    
    def received_setting_changed( self ):
        # Update Sampling UIs
        self.LE_sampling.setText( f"{self.device.sampling:.2f}" )
        # Update Gain UIs
        bool_all_gain = True
        for i in range(self.device.NUM_CHANNELS):
            # print('XX', self.device.adcs[i]['gain'] )
            ind = [128, 64, 32, 16, 8, 1, 0].index(self.device.adcs[i]['gain'] )
            self.adc[i].CB_gain.setCurrentIndex(ind)
            bool_all_gain = bool_all_gain and self.device.adcs[i]['gain'] == self.device.adcs[0]['gain']

            self.adc_full[i].CB_gain.setCurrentIndex(ind)


            if self.device.adcs[i]['polarity']==1 :
                self.adc_full[i].CB_polarity.setCurrentIndex(0)
            elif self.device.adcs[i]['polarity']==2 :
                self.adc_full[i].CB_polarity.setCurrentIndex(1)

            if self.device.adcs[i]['buffer']=='u' :
                self.adc_full[i].CB_buffer.setCurrentIndex(1)
            elif self.device.adcs[i]['buffer']=='b' :
                self.adc_full[i].CB_buffer.setCurrentIndex(0)

            if self.device.i_function:
                if self.device.adcs[i]['impedance']=='+':
                    self.adc_full[i].CB_impedance.setCurrentIndex(0)
                if self.device.adcs[i]['impedance']=='-':
                    self.adc_full[i].CB_impedance.setCurrentIndex(1)



        if bool_all_gain:
            self.CB_allGains.setCurrentIndex(ind)


    def make_dlg_adc(self):
        self.dlg_adc = QWidget()
        layout = QGridLayout()
        self.dlg_adc.setLayout(layout)
        # self.dlg_adc.layout = QGridLayout(self.dlg_adc)
        # self.dlg_adc.show()
        # # Clear current dialog
        # self.adc_full = []
        # while self.layout_adc_full.count():  # While there are items in the layout
        #     item = self.layout_adc_full.takeAt(0)  # Take the first item
        #     widget = item.widget()  # Get the widget
        #     if widget is not None:
        #         widget.deleteLater()  # Mark the widget for deletion

    def get_board_status(self):
        req = {'func':'get_board_status'}
        self.device.set_request( req )
        
    def open_adc_setting(self):
        self.dlg_adc.show()

    def make_panel_adc(self):
        # Clear current adc panel
        self.adc = []
        self.adc_full = []
        while self.layout_adc.count():  # While there are items in the layout
            item = self.layout_adc.takeAt(0)  # Take the first item
            widget = item.widget()  # Get the widget
            if widget is not None:
                widget.deleteLater()  # Mark the widget for deletion
        
        ind_row = int( (self.device.NUM_CHANNELS-1)/4)#0
        ind_col = 0
        for i in range(self.device.NUM_CHANNELS):
            # Quick Setting
            self.adc.append( adc_setting() )
            self.layout_adc.addWidget( self.adc[i].widget, ind_row, ind_col)
            self.adc[i].group_adc.setTitle( f"Ch {i+1}")
            self.adc[i].LE_label.setText( f"Ch {i+1}")

            self.adc[i].CB_gain.activated.connect( partial(self.set_individual_gain,i,True) )
            self.adc[i].LE_label.editingFinished.connect( partial(self.set_label,i) )

            # Full Setting
            self.adc_full.append( adc_full_setting())
            self.adc_full[i].label.setText( f"Ch {i+1}")
            self.dlg_adc.layout().addWidget( self.adc_full[i].widget, ind_row,ind_col)

            self.adc_full[i].CB_gain.activated.connect( partial(self.set_individual_gain,i,False))
            self.adc_full[i].CB_polarity.activated.connect( partial(self.set_individual_polarity,i))
            self.adc_full[i].CB_buffer.activated.connect( partial(self.set_individual_buffer,i))
            self.adc_full[i].CB_impedance.activated.connect( partial(self.set_individual_impedance,i) )
            self.adc_full[i].widget_impedance.setVisible( self.device.i_function)
            
            ind_col += 1
            if ind_col == 4:
                ind_col = 0
                ind_row -= 1
                # ind_row +=1


    def set_individual_gain( self, i, quick, dummy ):
        if quick:
            gain = self.adc[i].CB_gain.currentText()
        else:
            gain = self.adc_full[i].CB_gain.currentText()

        if gain == "Off": 
            gain = 0
        else:
            gain = int(gain)

        req = {'func':'set_ADC_settings',
               'ch': i+1,
               'gain': gain,
               'polarity': 0,
               'buffer':''}
        self.device.set_request( req )

    def set_individual_polarity( self, i, dummy):
        gain = self.adc[i].CB_gain.currentText()
        if gain == "Off": 
            gain = 0
        else:
            gain = int(gain)


        if self.adc_full[i].CB_polarity.currentText() == "Unipolar":
            polarity = 1
        elif self.adc_full[i].CB_polarity.currentText() == "Bipolar":
            polarity = 2
            
        req = {'func':'set_ADC_settings',
               'ch': i+1,
               'gain': gain,
               'polarity': polarity,
               'buffer':''}
        self.device.set_request( req )

    def set_individual_buffer( self, i, dummy):
        gain = self.adc[i].CB_gain.currentText()
        if gain == "Off": 
            gain = 0
        else:
            gain = int(gain)

        if self.adc_full[i].CB_buffer.currentText() == "Unbuffered":
            buffer = 'u'
        elif self.adc_full[i].CB_buffer.currentText() == "Buffered":
            buffer = 'b'
        req = {'func':'set_ADC_settings',
               'ch': i+1,
               'gain': gain,
               'polarity': 0,
               'buffer':buffer}
        self.device.set_request( req )

    def set_individual_impedance( self, i, dummy):
        impedance = self.adc_full[i].CB_impedance.currentText()
        req = {'func': 'set_impedance',
               'ch': i+1,
               'impedance': impedance}
        self.device.set_request( req)

    def set_ADC_settings( self, ch, gain, polarity, buffer ):
        req = {'func':'set_ADC_settings',
               'ch': ch,
               'gain': gain,
               'polarity': polarity,
               'buffer':buffer}
        self.device.set_request( req )
                                                                                                                                                                                                      
    def set_all_gains( self ):
        gain = self.CB_allGains.currentText()
        if gain == "Off": 
            gain = 0
        else:
            gain = int(gain)
        self.set_ADC_settings( 0, gain, polarity=0,buffer='' )

    def set_sampling( self ):
        sampling = float( self.LE_sampling.text() )
        if self.device.sampling !=  sampling :
            self.device.set_request( {'func':'set_sampling',
                                        'value':sampling})
            

    def set_label( self,i ):
        label = self.adc[i].LE_label.text()
        self.device.adcs[i]['label'] = label
        # self.tabs_spectrogram.setTabText(i, label)

    def start_device(self):
        self.data_index = 0
        self.device.thread_main = self.thread_main
        self.device.m_thread = QThread()
        self.device.moveToThread(self.device.m_thread)
        self.device.m_thread.started.connect( self.device.start_comm )
        self.device.m_thread.start()    

    ### Terminal Related    
    def console_close(self):
        self.console.hide()

    def console_open(self):
        self.console.appear()

    def console_send(self, msg):
        req = {'func':'send_command', 
               'value':msg }
        self.device.set_request( req )
    
        

