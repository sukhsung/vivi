from PyQt5.QtCore import QSize, QThread, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTabWidget,
    QLineEdit,
    QWidget,
    QGroupBox,
    QComboBox,
    QTextEdit,
    QFileDialog,
    QCheckBox,
    QProgressBar
)
from PyQt5.QtGui import QFont, QFontDatabase,QIcon
from PyQt5.QtSvg import QSvgWidget

import sys, os, time
import vivi, vivi_plot
import numpy as np
from functools import partial
from datetime import datetime
import serial.tools.list_ports

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vivi")
        self.setFixedSize(QSize(1280, 780))
        self.main_widget = QWidget()
        self.main_widget.setObjectName( "main_widget")
        layout_main = QVBoxLayout()
        self.main_widget.setLayout(layout_main)
        self.board = None

        self.make_panel_device()
        self.make_panel_viewer()
        self.make_panel_banner()

        layout_UI = QHBoxLayout()
        layout_UI.addWidget( self.group_vivi )
        layout_UI.addWidget( self.group_viviewer )

        layout_main.addLayout( layout_UI )
        layout_main.addWidget( self.group_logo )
        # self.main_widget.setStyleSheet( "background-color:393939")

        self.setCentralWidget( self.main_widget )

    def make_panel_device( self ):
        # Vivi Device Manager Panel
        self.group_vivi = QGroupBox("")
        self.group_vivi.setFixedSize(QSize(450, 680))
        layout_vivi = QVBoxLayout()
        self.group_vivi.setLayout( layout_vivi )

        # Serial Port Manager
        layout_device = QHBoxLayout()
        layout_device.setContentsMargins( 0,0,0,0 )
        self.dev_list = QComboBox(  )
        self.PB_connect = QPushButton( "Connect" )
        self.PB_connect.clicked.connect( self.on_click_connect )
        self.PB_refresh = QPushButton( "Refresh" )
        self.PB_refresh.clicked.connect( self.update_port_list )
        layout_device.addWidget( self.dev_list )
        layout_device.addWidget( self.PB_connect )
        layout_device.addWidget( self.PB_refresh )

        self.update_port_list()

        # Settings Panel
        self.group_device_setting = QGroupBox()
        layout_vivi_setting = QVBoxLayout()
        # self.group_device_setting.setContentsMargins( 0,0,0,0 )
        layout_vivi_setting.setContentsMargins( 0,0,0,0 )
        self.group_device_setting.setLayout( layout_vivi_setting )
        self.group_device_setting.setFlat( True )
        self.group_device_setting.setEnabled( False )

        # All Channel Settings
        layout_device_input = QHBoxLayout()
        self.CB_allGains = QComboBox()
        self.CB_allGains.addItems( ["128", "64", "32", "16", "8","1"])
        self.CB_allGains.activated.connect( self.set_all_gains )
        self.TB_sampling = QLineEdit("400.00")
        self.TB_sampling.setMaxLength(7)
        self.TB_sampling.setFixedWidth( 55 )
        self.TB_sampling.returnPressed.connect( self.set_sampling ) 
        self.PB_getDevStatus = QPushButton( "Status" )
        self.PB_getDevStatus.clicked.connect( self.get_board_status )
        self.listening_for_sampling = True
        layout_device_input.addWidget( QLabel("All Gains:"))
        layout_device_input.addWidget( self.CB_allGains)
        layout_device_input.addWidget( QLabel("Sampling (Hz):"))
        layout_device_input.addWidget( self.TB_sampling)
        layout_device_input.addWidget( self.PB_getDevStatus)

        # Individual Gain Channels
        layout_gains = QHBoxLayout()
        self.CB_gains = [QComboBox() for i in range(4)]
        for i in range(4):
            self.CB_gains[i].addItems( ["128", "64", "32", "16", "8","1"])
            self.CB_gains[i].activated.connect( partial(self.set_individual_gain,i) )
            layout_gains.addWidget( QLabel( "Ch {}".format(i+1)) )
            layout_gains.addWidget( self.CB_gains[i] )

        # Device Console
        layout_device_status = QHBoxLayout()
        self.TE_deviceStatus = QTextEdit( "Connect to an ADC-8 Board to start" )
        self.TE_deviceStatus.setReadOnly(True)
        layout_device_status.addWidget( self.TE_deviceStatus )

        layout_command = QHBoxLayout()
        self.LE_command = QLineEdit()
        self.LE_command.returnPressed.connect( self.on_click_send )
        self.PB_send = QPushButton( "Send" )
        self.PB_send.clicked.connect( self.on_click_send )
        self.PB_clear = QPushButton( "Clear" )
        self.PB_clear.clicked.connect( self.on_click_clear )

        layout_command.addWidget( self.LE_command )
        layout_command.addWidget( self.PB_send )
        layout_command.addWidget( self.PB_clear )

        layout_vivi_setting.addLayout( layout_device_input )
        layout_vivi_setting.addLayout(layout_gains)
        layout_vivi_setting.addLayout( layout_device_status )
        layout_vivi_setting.addLayout( layout_command )

        layout_vivi.addLayout( layout_device )
        layout_vivi.addWidget( self.group_device_setting)
    
    def make_panel_viewer( self ):
        # Load Plot Manager
        self.plotter = vivi_plot.Plotter(  )

        # Acquisition Viewer Panel
        self.group_viviewer = QGroupBox("")
        layout_viviewer = QVBoxLayout()
        self.group_viviewer.setLayout( layout_viviewer )
        self.group_viviewer.setFixedSize(QSize(790, 680))
        layout_upper = QHBoxLayout()
        layout_middle = QHBoxLayout()
        layout_lower = QVBoxLayout()
        layout_viviewer.addLayout( layout_upper )
        layout_viviewer.addLayout( layout_middle )
        layout_viviewer.addLayout( layout_lower )

        layout_acquisition_control = QVBoxLayout() 
        self.group_live_control = QGroupBox()
        self.group_live_control.setFlat( True )
        layout_live_control = QVBoxLayout()
        self.group_live_control.setContentsMargins(0,0,0,0)
        layout_live_control.setContentsMargins(0,0,0,0)
        self.group_live_control.setFixedSize( QSize(150, 130))
        self.group_live_control.setLayout( layout_live_control )
        self.PB_live_start = QPushButton( "Live: Start" )
        self.PB_live_start.clicked.connect( self.on_click_start_view )
        layout_num_live_sample = QHBoxLayout()
        label_num_live_sample = QLabel("# Live Sample")
        self.LE_num_live_sample = QLineEdit("512")
        layout_num_live_sample.addWidget( label_num_live_sample )
        layout_num_live_sample.addWidget( self.LE_num_live_sample )
        layout_num_dft_live = QHBoxLayout()
        label_num_dft_live = QLabel("# DFT")
        self.LE_num_dft_live = QLineEdit("128")
        self.CheckBox_average =QCheckBox("Show Average")
        self.CheckBox_average.setChecked( True )
        layout_num_dft_live.addWidget( label_num_dft_live )
        layout_num_dft_live.addWidget( self.LE_num_dft_live )
        layout_live_control.addWidget( self.PB_live_start)
        layout_live_control.addLayout( layout_num_live_sample)
        layout_live_control.addLayout( layout_num_dft_live)
        layout_live_control.addWidget( self.CheckBox_average )

        self.group_acquire_control = QGroupBox()
        self.group_acquire_control.setFlat( True )
        layout_acquire_control = QVBoxLayout()
        self.group_acquire_control.setContentsMargins(0,0,0,0)
        layout_acquire_control.setContentsMargins(0,0,0,0)
        self.group_acquire_control.setFixedSize( QSize(150, 130))
        self.group_acquire_control.setLayout( layout_acquire_control )
        self.PB_acquire_start = QPushButton( "Acquire: Start" )
        self.PB_acquire_start.clicked.connect( self.on_click_start_acquire )
        layout_num_dft_acquire = QHBoxLayout()
        label_num_dft_acquire = QLabel("# DFT")
        self.LE_num_dft_acquire = QLineEdit("1024")
        layout_num_dft_acquire.addWidget( label_num_dft_acquire )
        layout_num_dft_acquire.addWidget( self.LE_num_dft_acquire )
        layout_acquire_time = QHBoxLayout()
        label_acquire_time = QLabel("time (s)")
        self.LE_acquire_time = QLineEdit("3")
        self.label_elapsed_time = QLabel("0 s")
        self.Progress_Acquistion = QProgressBar()
        self.Progress_Acquistion.setValue(0)
        layout_acquire_time.addWidget( label_acquire_time )
        layout_acquire_time.addWidget( self.LE_acquire_time )
        layout_acquire_time.addWidget( self.label_elapsed_time )
        layout_acquire_control.addWidget( self.PB_acquire_start)
        layout_acquire_control.addLayout( layout_num_dft_acquire)
        layout_acquire_control.addLayout( layout_acquire_time)
        layout_acquire_control.addWidget( self.Progress_Acquistion)

        layout_acquisition_control.addWidget( self.group_live_control )
        layout_acquisition_control.addWidget( self.group_acquire_control )

        group_spectrum = QGroupBox("")
        group_spectrum.setFlat( True )
        layout_spectrum = QVBoxLayout()
        group_spectrum.setLayout( layout_spectrum )
        group_spectrum.setContentsMargins(0,0,0,0)
        layout_spectrum.setContentsMargins(0,0,0,0)
        group_spectrum.setFixedHeight( 250)
        layout_spectrum.addWidget( self.plotter.PW_spectrum )

        layout_upper.addLayout( layout_acquisition_control )
        layout_upper.addWidget( group_spectrum )

        # Save Control
        self.group_save_control = QGroupBox("")
        self.group_save_control.setFlat( True )
        layout_save_control = QHBoxLayout()
        self.group_save_control.setLayout( layout_save_control )
        self.group_save_control.setContentsMargins(0,0,0,0)
        layout_save_control.setContentsMargins(0,0,0,0)
        label_save_control = QLabel("Save Path:")
        today = datetime.today().strftime('%Y-%m-%d')# Get Today
        self.LE_save_path = QLineEdit(f"{os.getcwd()}/results/{today}")
        self.LE_save_path.returnPressed.connect( self.on_save_path_change )
        self.PB_browse = QPushButton( "Browse" )
        self.PB_browse.clicked.connect( self.on_click_browse )
        self.PB_open = QPushButton( "Open" )
        self.PB_open.clicked.connect( self.on_click_open )
        self.save_status = QLabel("")
        layout_save_control.addWidget( label_save_control )
        layout_save_control.addWidget( self.LE_save_path )
        layout_save_control.addWidget( self.PB_browse )
        layout_save_control.addWidget( self.PB_open )
        layout_save_control.addWidget( self.save_status )
        layout_middle.addWidget( self.group_save_control )
        self.on_save_path_change()

        tabs_spectrogram = QTabWidget()
        test_widget = QWidget()
        # test_widget.setObjectName( "Test")
        # tabs_spectrogram.addTab( test_widget, "Test")
        # tabs_spectrogram.setAutoFillBackground( True )
        for i in range(4):
            tabs_spectrogram.addTab( self.plotter.PW_spectrogram[i], f"Ch {i+1}" )
            # self.plotter.PW_spectrogram[i].setBackground( (60, 60, 60))
        tabs_spectrogram.addTab( self.plotter.PW_integrated, "Integrated Power")
        # self.plotter.PW_integrated.setBackground( (60, 60, 60))

        layout_lower.addWidget( tabs_spectrogram ) 

        # self.plotter.initialize()
        self.group_viviewer.setEnabled( False )

    def make_panel_banner( self ):
        self.group_logo = QGroupBox("")
        self.group_logo.setFlat( True )
        self.group_logo.setFixedHeight(70)

        # Loading SVG
        #svg_logo_left = QtSvgWidgets.QSvgWidget('assets/vivi-logo-left.svg', parent=self.group_logo)
        svg_logo_left = QSvgWidget('assets/vivi-logo-left.svg', parent=self.group_logo)
        svg_logo_left.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        svg_logo_left.setContentsMargins( 0,0,0,0 )
        svg_logo_left.move(5, -75)
        svg_logo_left.resize(220,220)

        # svg_logo_right = QtSvgWidgets.QSvgWidget('assets/vivi-logo-right.svg', parent=self.group_logo)
        svg_logo_right = QSvgWidget('assets/vivi-logo-right.svg', parent=self.group_logo)
        svg_logo_right.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        # svg_logo_right.renderer().viewBox().setWidth( 5000)
        svg_logo_right.setContentsMargins( 0,0,0,0 )
        svg_logo_right.move(825, -175)
        svg_logo_right.resize(420,420)

        # layout_logo.addSpacing(50)
        # layout_logo.addWidget(svg_logo_left)
        # layout_logo.addSpacing(500)
        # layout_logo.addWidget(svg_logo_right)
        # layout_logo.addSpacing(50)


    ### Save Related
    def on_save_path_change( self ):
        folderpath= self.LE_save_path.text(  )
        if not os.path.isdir( folderpath ):
            try:
                os.makedirs( folderpath )
                self.save_status.setText( "Folder Path Created")
            except:
                self.save_status.setText( "Folder Path Not Set")
        else :
            self.save_status.setText( "Folder Path Set")

    def on_click_open( self ):
        try:
            os.system("open "+self.LE_save_path.text() )
        except:
            self.PB_open.setEnabled( False )
        #     os.startfile(self.LE_save_path.text())
    def on_click_browse( self ):
        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.LE_save_path.setText( folderpath )
        self.save_status.setText( "Folder Path Set")
    ### #Save Realted

    def on_status_change( self,status ):
        if status == "NOT-READY": # Board not Ready
            self.group_device_setting.setEnabled( False )
            self.group_viviewer.setEnabled( False )
        elif status == "LISTENING":# Board Ready
            self.group_device_setting.setEnabled( True )
            self.group_viviewer.setEnabled( True )
            self.group_acquire_control.setEnabled( True )
            self.group_live_control.setEnabled( True )
            self.group_save_control.setEnabled( True )
            self.PB_acquire_start.setText( "Acquire: Start")
            self.PB_live_start.setText( "Live: Start")
        elif status == "LIVE":
            self.group_acquire_control.setEnabled( False )
            self.group_save_control.setEnabled( False )
        elif status == "ACQUIRE":
            self.group_live_control.setEnabled( False )
            self.group_save_control.setEnabled( False )
        elif status == "DISCONNECT":
            print("Disconnecting")
            self.disconnect_device()
            self.thread_board.quit()

            self.PB_refresh.setEnabled( True )
            self.PB_send.setEnabled( False )
            self.PB_connect.setText( "Connect" )
            self.group_device_setting.setEnabled( False )
            self.group_viviewer.setEnabled( False )
            self.update_port_list()


    def prepare_acquisition(self, mode ):
        self.plotter.sampling = self.board.sampling
        self.timestamp = time.strftime( "%H%M", time.localtime())

        if mode == "live":
            self.board.set_num_live_sample( int( self.LE_num_live_sample.text() ) )
            
            self.plotter.num_dft = int( self.LE_num_dft_live.text() )
            self.plotter.num_sample = int( self.LE_num_live_sample.text() )
            self.plotter.set_plot_average( self.CheckBox_average.isChecked() )

            self.plotter.init_all()
            self.plotter.init_spectrum()
            self.plotter.init_spectrogram()
            self.plotter.init_integrated()

            fname = f"{self.timestamp}_Live_Sampling_{self.board.sampling}Hz_Gain_{self.board.gains}"
            self.fpath = os.path.join(self.LE_save_path.text(), fname)

        elif mode == "acquire":
            acquire_time = int( self.LE_acquire_time.text() )
            self.board.set_acquire_time( acquire_time )
            self.plotter.set_plot_average( False )

            self.plotter.num_dft = int( self.LE_num_dft_acquire.text() )
            self.plotter.num_sample = self.plotter.num_dft
            self.plotter.set_plot_average( False )

            self.plotter.init_all()
            self.plotter.init_spectrum()

            self.timestamp = time.strftime( "%H%M", time.localtime())
            fname = f"{self.timestamp}_Acquire_{acquire_time}s_Sampling_{self.board.sampling}Hz_Gain_{self.board.gains}"
            self.fpath = os.path.join(self.LE_save_path.text(), fname)
        
    def on_click_start_acquire(self):
        if self.PB_acquire_start.text() == "Acquire: Start":
            self.prepare_acquisition("acquire")
            self.board.set_status("ACQUIRE")


            self.group_device_setting.setEnabled( False )
            self.group_live_control.setEnabled( False )

            self.PB_acquire_start.setText( "Acquire: Stop")
            self.LE_num_dft_acquire.setEnabled( False )
            self.LE_acquire_time.setEnabled( False )
            self.Progress_Acquistion.setValue(0)

        elif self.PB_acquire_start.text() == "Acquire: Stop":
            self.board.set_status( "STOPPING" )
            self.PB_acquire_start.setText( "Acquire: Start")
            self.group_device_setting.setEnabled( True )
            self.group_live_control.setEnabled( True )
            self.LE_num_dft_acquire.setEnabled( True )
            self.LE_acquire_time.setEnabled( True )

    def on_click_start_view(self):
        if self.PB_live_start.text() == "Live: Start":
            self.prepare_acquisition("live")
            self.live_file = open( self.fpath, 'w')
            self.board.set_status( "LIVE" )

            self.PB_live_start.setText( "Live: Stop")
            self.group_device_setting.setEnabled( False )
            self.group_acquire_control.setEnabled( False )
            self.LE_num_dft_live.setEnabled( False )
            self.LE_num_live_sample.setEnabled( False )
            self.CheckBox_average.setEnabled( False )
        elif self.PB_live_start.text() == "Live: Stop":
            self.board.set_status( "STOPPING" )

            self.PB_live_start.setText( "Live: Start")
            self.group_device_setting.setEnabled( True )
            self.group_acquire_control.setEnabled( True )
            self.LE_num_dft_live.setEnabled( True )
            self.LE_num_live_sample.setEnabled( True )
            self.CheckBox_average.setEnabled( True )
            self.live_file.close()

            self.save_status.setText( f"File Saved time stamp: {self.timestamp}")

    def received_elapsed_time( self, value):
        self.label_elapsed_time.setText( f"{value} s")
        self.Progress_Acquistion.setValue( int( 100*float(value)/float(self.LE_acquire_time.text())))

    def received_acquire_data( self, value):
        if not value==[-1]:
            self.Progress_Acquistion.setValue(100)
            self.label_elapsed_time.setText( f"{self.LE_acquire_time.text()} s" )
            volts = np.array(value)
            self.plotter.update_all( volts, spectrogram=False )

            ## Save Data
            acquire_file = open(self.fpath, 'w')
            for line in value:
                acquire_file.write(f"{line[0]}, {line[1]}, {line[2]}, {line[3]}\n") # works with any number of elements in a line
            acquire_file.close()
            self.save_status.setText( f"File Saved time stamp: {self.timestamp}")

        
        self.LE_num_dft_acquire.setEnabled( True )
        self.LE_acquire_time.setEnabled( True )


    def received_live_data( self, value ):
        volts = np.array(value)

        self.plotter.update_all( volts, spectrogram=True)
        
        for line in value:
            self.live_file.write(f"{line[0]}, {line[1]}, {line[2]}, {line[3]}\n") 

    ### ADC Setting Related
    def get_board_status(self):
        self.board.get_board_status()
                                                                                                                                                                                                                                                                                          
    def set_all_gains( self ):
        self.board.set_all_gains( self.CB_allGains.currentText() )
        for i in range( len(self.CB_gains) ):
            self.CB_gains[i].setCurrentIndex( self.CB_allGains.currentIndex() )

    def set_individual_gain( self, ch):
        self.board.set_individual_gain(ch+1, self.CB_gains[ch].currentText())

    def set_sampling( self ):
        self.board.set_sampling(self.TB_sampling.text())
        self.board.sampling = float( self.TB_sampling.text() )
    ###

    ### Terminal Related    
    def received_msg( self, value ):
        self.TE_deviceStatus.append( value )

    def received_setting_changed( self ):
        # Update Sampling UIs
        self.TB_sampling.setText( f"{self.board.sampling:.2f}" )
        # Update Gain UIs
        bool_all_gain = True
        for i in range(4):
            ind = ["128", "64", "32", "16", "8","1"].index(str(self.board.gains[i]))
            self.CB_gains[i].setCurrentIndex(ind)
            bool_all_gain = bool_all_gain and self.board.gains[i] == self.board.gains[0]

        if bool_all_gain:
            self.CB_allGains.setCurrentIndex(ind)


    def send_command( self, msg ):      
        # Send Serial Command and Listen
        self.board.send_command( msg )

    def on_click_send(self):
        self.send_command( self.LE_command.text() )
        self.LE_command.setText("")

    def on_click_clear(self):
        self.TE_deviceStatus.setText("")
    ###

    ### Device management Related
    def on_click_connect(self):
        # Connect Push Button
        if self.PB_connect.text() == "Connect":
            # Check if port list needs update:
            cur_port_list = self.port_list
            new_port_list = self.get_port_list()
            if not cur_port_list == new_port_list:
                self.update_port_list()
            else:
                self.connect_device()
        elif self.PB_connect.text() == "Disconnect":
            self.disconnect_device()

    def get_port_list(self):
        """\
        Return a list of USB serial port devices.

        Entries in the list are ListPortInfo objects from the
        serial.tools.list_ports module.  Fields of interest include:

            device:  The device's full path name.
            vid:     The device's USB vendor ID value.
            pid:     The device's USB product ID value.
        """
        return [p for p in serial.tools.list_ports.comports() if p.vid]

    def update_port_list(self):
        # Remove Current List
        for i in range(self.dev_list.count()):
            self.dev_list.removeItem(0)

        # Update Port List
        self.port_list = self.get_port_list()
        if len(self.port_list) > 0:
            self.dev_list.addItems( [p.device for p in self.port_list] )
            self.PB_connect.setEnabled( True )
        elif len(self.port_list) == 0:
            self.PB_connect.setEnabled( False )

    def connect_device(self):
        if self.board == None: # Initialize board object if it doesn't exisit
            self.board = vivi.Board( )
            self.board.msg_out.connect( self.received_msg )
            self.board.status_signal.connect( self.on_status_change )
            self.board.live_data.connect( self.received_live_data )
            self.board.acquire_data.connect( self.received_acquire_data )
            self.board.elapsed_time.connect( self.received_elapsed_time)
            self.board.setting_changed.connect( self.received_setting_changed )

        if len(self.port_list) > 0:
            portname = self.port_list[self.dev_list.currentIndex()].device
            connected = self.board.connect_board( portname )
            if connected:
                self.thread_board = QThread()
                self.thread_main = QThread.currentThread() 
                self.board.thread_main = self.thread_main
                self.board.moveToThread(self.thread_board)
                self.thread_board.started.connect( self.board.start_comm )
                self.thread_board.finished.connect( self.thread_board.deleteLater )
                self.thread_board.start()

                self.PB_send.setEnabled( True )
                self.PB_connect.setText( "Disconnect" )
                self.PB_refresh.setEnabled( False )

                self.group_acquire_control.setEnabled( True )
                self.group_live_control.setEnabled( True )
                # self.group_save_control.setEnabled( True )

                self.board.init_settings()
        

    def disconnect_device( self ):
        if self.board == None:
            return
        elif self.board.status == "DISCONNECT":
            return
        elif self.board.status == "NOT-READY":
            return
        else:
            self.board.close_board()
            self.thread_board.quit()
            self.PB_refresh.setEnabled( True )
            self.PB_send.setEnabled( False )
            self.PB_connect.setText( "Connect" )
            self.group_device_setting.setEnabled( False )
            self.group_viviewer.setEnabled( False )

    def on_quit( self ):
        print("Exiting Vivi")
        self.disconnect_device()
    ###
    
        


app = QApplication(sys.argv)

with open("assets/style.css","r") as fh:
    app.setStyleSheet(fh.read())
# app.setStyleSheet( "assets/style.css")
 
# font = QFontDatabase.addApplicationFont("Arial")
# font =QFont("Arial")
# print(font)
# app.setFont(font)

app.setWindowIcon(QIcon("assets/vivi-icon.png"))
window = MainWindow()
window.show()

app.aboutToQuit.connect( window.on_quit )


app.exec()
