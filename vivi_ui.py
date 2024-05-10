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

import sys, os, time, json, glob
import vivi, vivi_plot
import numpy as np
from functools import partial
from datetime import datetime
import serial.tools.list_ports

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vivi_path=os.path.dirname(os.path.abspath(__file__))
        self.asset_path = os.path.join( self.vivi_path, 'assets')

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
        self.dev_list.activated.connect( self.on_dev_selected )
        self.dev_list.setFixedWidth( 100)
        self.LE_URL = QLineEdit( "<hostname>:<port>")
        self.PB_connect = QPushButton( "Connect" )
        self.PB_connect.clicked.connect( self.on_click_connect )
        self.PB_refresh = QPushButton( "Refresh" )
        self.PB_refresh.clicked.connect( self.update_port_list )
        layout_device.addWidget( self.dev_list )
        layout_device.addWidget( self.LE_URL )
        layout_device.addWidget( self.PB_connect )
        layout_device.addWidget( self.PB_refresh )
        # g_tmp.setLayout( layout_device)

        self.update_port_list()

        # Settings Panel
        self.group_device_setting = QGroupBox("")
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
        self.TB_sampling.editingFinished.connect( self.set_sampling ) 
        self.PB_getDevStatus = QPushButton( "Status" )
        self.PB_getDevStatus.clicked.connect( self.get_board_status )
        self.listening_for_sampling = True
        layout_all_gain = QHBoxLayout()
        layout_all_gain.addWidget( QLabel("All Gains:"))
        layout_all_gain.addWidget( self.CB_allGains)
        layout_all_gain.setSpacing(0)

        layout_sampling = QHBoxLayout()
        layout_sampling.addWidget( QLabel("Sampling (Hz):"))
        layout_sampling.addWidget( self.TB_sampling)
        layout_sampling.setSpacing(0)

        layout_device_input.addLayout( layout_all_gain )
        layout_device_input.addStretch()
        layout_device_input.addLayout( layout_sampling )
        layout_device_input.addStretch()
        layout_device_input.addWidget( self.PB_getDevStatus)
        layout_device_input.setSpacing(0)
        layout_device_input.setContentsMargins(0,0,0,0)


        # Individual Gain Channels
        layout_gains = QVBoxLayout()
        layout_gains_1 = QHBoxLayout()
        layout_gains_2 = QHBoxLayout()
        self.CB_gains = [QComboBox() for i in range(8)]
        # self.CB_gains_labels = []

        self.TB_gains_labels = [QLineEdit(f"Ch {i+1}") for i in range(8)]

        self.group_channels = [QGroupBox(f"Ch {i+1}") for i in range(8)]


        for i in range(8):
            self.CB_gains[i].addItems( ["128", "64", "32", "16", "8","1"])
            self.CB_gains[i].activated.connect( partial(self.set_individual_gain,i) )
            
            # self.TB_gains_labels[i].setMaxLength(7)
            # self.TB_gains_labels[i].setFixedWidth( 80 )
            self.TB_gains_labels[i].editingFinished.connect( self.set_label )
            # self.TB_gains_labels[i].setHidden( True )
            cur_ver = QVBoxLayout()
            cur_ver.addWidget( self.CB_gains[i] )
            cur_ver.addWidget( self.TB_gains_labels[i])
            cur_ver.setSpacing(0)
            cur_ver.setContentsMargins(8,22,8,8)
            self.group_channels[i].setLayout( cur_ver )
            if i < 4:
                layout_gains_1.addWidget( self.group_channels[i] )
            else:
                layout_gains_2.addWidget( self.group_channels[i] )

            self.group_channels[i].setHidden(True)


        layout_gains.addLayout( layout_gains_1 )
        layout_gains.addLayout( layout_gains_2 )
        layout_gains.setSpacing(10)
        # Device Console
        layout_device_status = QHBoxLayout()
        self.TE_deviceStatus = QTextEdit( "Connect to an ADC-8 Board to start" )
        self.TE_deviceStatus.setReadOnly(True)
        layout_device_status.addWidget( self.TE_deviceStatus )
        layout_device_status.setContentsMargins(0,10,0,0)

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
        layout_vivi_setting.addLayout( layout_gains )
        layout_vivi_setting.addLayout( layout_device_status )
        layout_vivi_setting.addLayout( layout_command )
        layout_vivi_setting.setSpacing( 0 )

        layout_vivi.addLayout( layout_device )
        layout_vivi.addWidget( self.group_device_setting)
        layout_vivi.setSpacing( 0 )
    
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
        self.CheckBox_average.setChecked( False )

        layout_CB_plot = QHBoxLayout()
        self.CB_plot = [QCheckBox() for i in range(8)]
        for i in range(8):
            layout_CB_plot.addWidget( self.CB_plot[i])
            self.CB_plot[i].setChecked( True )
            self.CB_plot[i].setHidden( True )
            self.CB_plot[i].stateChanged.connect( self.set_plot_enable )

        layout_num_dft_live.addWidget( label_num_dft_live )
        layout_num_dft_live.addWidget( self.LE_num_dft_live )
        layout_live_control.addWidget( self.PB_live_start)
        layout_live_control.addLayout( layout_num_live_sample)
        layout_live_control.addLayout( layout_num_dft_live)
        layout_live_control.addWidget( self.CheckBox_average )
        layout_live_control.addLayout( layout_CB_plot )

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
        savepath = os.path.join( self.vivi_path, 'results', today)
        self.LE_save_path = QLineEdit(savepath)
        self.LE_save_path.editingFinished.connect( self.on_save_path_change )
        self.PB_browse = QPushButton( "Browse" )
        self.PB_browse.clicked.connect( self.on_click_browse )
        layout_save_control.addWidget( label_save_control )
        layout_save_control.addWidget( self.LE_save_path )
        layout_save_control.addWidget( self.PB_browse )

        folder_control = QGroupBox("")
        folder_control.setFlat( True )
        layout_folder_control = QHBoxLayout()
        self.PB_open = QPushButton( "Open" )
        self.PB_open.clicked.connect( self.on_click_open )
        self.save_status = QLabel("")
        layout_folder_control.addWidget( self.PB_open )
        layout_folder_control.addWidget( self.save_status )
        folder_control.setLayout( layout_folder_control)
        layout_middle.addWidget( self.group_save_control )
        layout_middle.addWidget( folder_control )
        self.on_save_path_change()

        self.tabs_spectrogram = QTabWidget()
        for i in range( 8 ):
            self.tabs_spectrogram.addTab( self.plotter.PW_spectrogram[i], f"Ch {i+1}" )
            self.tabs_spectrogram.setTabVisible(i,True)
        self.tabs_spectrogram.addTab( self.plotter.PW_integrated, "Integrated Power")

        layout_lower.addWidget( self.tabs_spectrogram ) 

        # self.plotter.initialize()
        self.group_viviewer.setEnabled( False )

    def make_panel_banner( self ):
        self.group_logo = QGroupBox("")
        self.group_logo.setFlat( True )
        self.group_logo.setFixedHeight(70)

        # Loading SVG
        self.svg_logo_left = QSvgWidget( os.path.join(self.asset_path,'vivi-logo-left.svg'), parent=self.group_logo)
        self.svg_logo_left.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.svg_logo_left.setContentsMargins( 0,0,0,0 )
        self.svg_logo_left.move(5, -75)
        self.svg_logo_left.resize(220,220)

        self.svg_logo_right = QSvgWidget( os.path.join( self.asset_path,'vivi-logo-right.svg'), parent=self.group_logo)
        self.svg_logo_right.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        # svg_logo_right.renderer().viewBox().setWidth( 5000)
        self.svg_logo_right.setContentsMargins( 0,0,0,0 )
        self.svg_logo_right.move(825, -175)
        self.svg_logo_right.resize(420,420)

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

    def on_dev_selected( self ):
        if self.dev_list.currentText() == "RFC 2217":
            self.LE_URL.setHidden(False)
        else:
            self.LE_URL.setHidden(True)
            # self.dev_list.setFixedWidth( 100)
            # self.LE_URL.setFixedWidth( 100 )

    def prepare_metadata( self, fname, acquistion ):
        # Make Python dictionary then dump to JSON
        
        if acquistion == -1:
            acquistion = "live"

        channels = []
        for i in range( self.board.NUM_CHANNELS):
            channels.append( {"Channel": (i+1),
                              "Gain": self.board.gains[i],
                              "Label": self.board.labels[i]})


        meta = {"filename": fname+".csv",
                "Sampling": self.board.sampling,
                "Acquisition": acquistion,
                "Channels": channels}
        
        jsonpath = os.path.join(self.LE_save_path.text(), fname+".json")
        with open(jsonpath, 'w') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    def prepare_fname( self ):
        self.timestamp = time.strftime( "%H%M", time.localtime())
        file_path = self.LE_save_path.text()
        fname = f"{self.timestamp}"

        # Check to see if there is duplicate
        print( file_path )
        files = glob.glob( os.path.join( file_path, f"{fname}*.csv") )
        
        if len(files) == 0:
            return fname
        else:
            return f"{fname}_{len(files)}"




    def prepare_acquisition(self, mode ):
        self.plotter.sampling = self.board.sampling

        if mode == "live":
            self.board.set_num_live_sample( int( self.LE_num_live_sample.text() ) )
            
            self.plotter.num_dft = int( self.LE_num_dft_live.text() )
            self.plotter.num_sample = int( self.LE_num_live_sample.text() )
            self.plotter.set_plot_average( self.CheckBox_average.isChecked() )
            self.plotter.set_plot_enable( self.CB_plot )
            self.plotter.init_all()
            self.plotter.labels = self.board.labels
            self.plotter.init_spectrum()
            self.plotter.init_spectrogram()
            self.plotter.init_integrated()

            fname = self.prepare_fname()
            self.fpath = os.path.join(self.LE_save_path.text(), fname+".csv")



            self.prepare_metadata( fname, -1 ) #-1 for live acqusition


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

            fname = self.prepare_fname()
            self.fpath = os.path.join(self.LE_save_path.text(), fname+".csv")
            self.prepare_metadata( fname, acquire_time )
        
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
                str_out = ""
                for i in range(self.board.NUM_CHANNELS):
                    str_out += f"{line[i]}, "
                str_out = str_out[:-2]
                str_out += "\n"
                acquire_file.write(str_out) # works with any number of elements in a line
            
            acquire_file.close()
            self.save_status.setText( f"File Saved time stamp: {self.timestamp}")

        
        self.LE_num_dft_acquire.setEnabled( True )
        self.LE_acquire_time.setEnabled( True )


    def received_live_data( self, value ):
        volts = np.array(value)

        self.plotter.update_all( volts, spectrogram=True)
        
        for line in value:
            str_out = ""
            for i in range(self.board.NUM_CHANNELS):
                str_out += f"{line[i]}, "
            str_out = str_out[:-2]
            str_out += "\n"
            self.live_file.write(str_out) 

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

    def set_label( self ):
        for i in range(self.board.NUM_CHANNELS):
            self.board.labels[i] = self.TB_gains_labels[i].text()
            self.tabs_spectrogram.setTabText(i, self.TB_gains_labels[i].text())
    def set_plot_enable( self ):
        for i in range(self.board.NUM_CHANNELS):
            self.plotter.plot_enable[i] = self.CB_plot[i].isChecked()

        self.plotter.set_plot_enable( self.CB_plot )
    ###

    ### Terminal Related    
    def received_msg( self, value ):
        self.TE_deviceStatus.append( value )

    def received_setting_changed( self ):
        # Update Sampling UIs
        self.TB_sampling.setText( f"{self.board.sampling:.2f}" )
        # Update Gain UIs
        bool_all_gain = True
        for i in range(self.board.NUM_CHANNELS):
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
        port_list = [p.device for p in serial.tools.list_ports.comports() if p.vid]
        port_list.append("RFC 2217")
        return port_list

    def update_port_list(self):
        # Remove Current List
        for i in range(self.dev_list.count()):
            self.dev_list.removeItem(0)

        # Update Port List
        self.port_list = self.get_port_list()
        self.dev_list.addItems( self.port_list )
        if len(self.port_list) > 0:
            self.PB_connect.setEnabled( True )
        elif len(self.port_list) == 0:
            self.PB_connect.setEnabled( False )
            self.LE_URL.setHidden(True)

        if self.dev_list.currentText() == "RFC 2217":
            self.LE_URL.setHidden(False)
        else:
            self.LE_URL.setHidden(True)



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
            portname = self.dev_list.currentText()
            if portname == "RFC 2217":
                portname = "rfc2217://"+self.LE_URL.text()#192.168.1.115:2217"
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

                for i in range(8):
                    self.group_channels[i].setHidden(True)
                    self.tabs_spectrogram.setTabVisible(i, False)
                    self.CB_plot[i].setHidden( True )

                for i in range(self.board.NUM_CHANNELS):

                    self.group_channels[i].setHidden(False)
                    self.tabs_spectrogram.setTabVisible(i, True)
                    self.CB_plot[i].setHidden( False )
                self.plotter.nchans = self.board.NUM_CHANNELS
                

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

vivi_path = os.path.dirname(os.path.abspath(__file__))
asset_path = os.path.join( vivi_path, 'assets')

with open( os.path.join( asset_path,"style.css"),"r") as fh:
    app.setStyleSheet(fh.read())


app.setWindowIcon(QIcon(os.path.join(asset_path,"vivi-icon.png")))
window = MainWindow()
window.show()

app.aboutToQuit.connect( window.on_quit )


app.exec()