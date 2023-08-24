from PyQt6.QtCore import QSize, Qt, QThread
from PyQt6.QtWidgets import (
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
    QCheckBox
)
from PyQt6.QtGui import QPalette, QColor, QFont, QFontDatabase

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

import sys
import os
import vivi, vivi_plot
import numpy as np
from functools import partial 
import math, time
from datetime import datetime

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Vivi")
        self.setFixedSize(QSize(1280, 700))
        self.board = None

        self.make_panel_device()
        self.make_panel_viewer()

        layout = QHBoxLayout()
        layout.addWidget( self.group_vivi )
        layout.addWidget( self.group_viviewer )

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget( widget )

    def make_panel_device( self ):
        # Vivi Device Manager Panel
        self.group_vivi = QGroupBox("Vivi")
        self.group_vivi.setFixedSize(QSize(450, 680))
        layout_vivi = QVBoxLayout()
        self.group_vivi.setLayout( layout_vivi )

        # Serial Port Manager
        layout_device = QHBoxLayout()
        layout_device.setContentsMargins( 0,0,0,0 )
        self.dev_list = QComboBox(  )
        self.port_list = vivi.get_port_list()
        self.dev_list.addItems( [p.device for p in self.port_list] )
        # self.dev_list.addItems( ["1","2"] )
        self.PB_connect = QPushButton( "Connect" )
        self.PB_connect.clicked.connect( self.on_click_connect )
        layout_device.addWidget( self.dev_list )
        layout_device.addWidget( self.PB_connect )

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
        self.sampling = 400
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
        self.CB_gains = []
        for i in range(4):
            self.CB_gains.append( QComboBox() )
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
        # Acquisition Viewer Panel
        self.group_viviewer = QGroupBox("Viviewer")
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
        self.PB_live_start.setEnabled( False )
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
        self.CheckBox_average.stateChanged.connect( self.on_checked_average )
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
        self.group_acquire_control.setFixedSize( QSize(150, 100))
        self.group_acquire_control.setLayout( layout_acquire_control )
        self.PB_acquire_start = QPushButton( "Acquire: Start" )
        self.PB_acquire_start.setEnabled( False )
        self.PB_acquire_start.clicked.connect( self.on_click_start_acquire )
        layout_num_dft_acquire = QHBoxLayout()
        label_num_dft_acquire = QLabel("# DFT")
        self.LE_num_dft_acquire = QLineEdit("1024")
        layout_num_dft_acquire.addWidget( label_num_dft_acquire )
        layout_num_dft_acquire.addWidget( self.LE_num_dft_acquire )
        layout_acquire_time = QHBoxLayout()
        label_acquire_time = QLabel("time (s)")
        self.LE_acquire_time = QLineEdit("3")
        # self.LE_acquire_time.width = 10
        self.label_elapsed_time = QLabel("0 s")
        layout_acquire_time.addWidget( label_acquire_time )
        layout_acquire_time.addWidget( self.LE_acquire_time )
        layout_acquire_time.addWidget( self.label_elapsed_time )
        layout_acquire_control.addWidget( self.PB_acquire_start)
        layout_acquire_control.addLayout( layout_num_dft_acquire)
        layout_acquire_control.addLayout( layout_acquire_time)

        layout_acquisition_control.addWidget( self.group_live_control )
        layout_acquisition_control.addWidget( self.group_acquire_control )

        group_live_view = QGroupBox("")
        layout_live_view = QVBoxLayout()
        group_live_view.setLayout( layout_live_view )
        group_live_view.setContentsMargins(0,0,0,0)
        layout_live_view.setContentsMargins(0,0,0,0)
        group_live_view.setFixedHeight( 250)
        self.PW_live_view = pg.plot(title="Live View")
        layout_live_view.addWidget( self.PW_live_view )

        layout_upper.addLayout( layout_acquisition_control )
        layout_upper.addWidget( group_live_view )

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
        self.LE_save_browse = QPushButton( "Browse" )
        self.LE_save_browse.clicked.connect( self.on_click_browse )
        self.save_status = QLabel("")
        layout_save_control.addWidget( label_save_control )
        layout_save_control.addWidget( self.LE_save_path )
        layout_save_control.addWidget( self.LE_save_browse )
        layout_save_control.addWidget( self.save_status )
        layout_middle.addWidget( self.group_save_control )
        self.on_save_path_change()

        tabs_spectrum = QTabWidget()
        tab_item = [];
        self.PW_spectrum = []
        self.II_spectrum = []
        self.PW_spectrum_colorbar = []
        for i in range(4):
            self.PW_spectrum.append( pg.plot() )
            self.II_spectrum.append( pg.ImageItem(img= np.zeros((128,64))) )
            self.PW_spectrum[i].getPlotItem().addItem(self.II_spectrum[i])
            self.PW_spectrum_colorbar.append( pg.ColorBarItem( values=(1,10), colorMap=pg.colormap.get('inferno') ))
            self.PW_spectrum_colorbar[i].setImageItem( self.II_spectrum[i], insert_in=self.PW_spectrum[i].getPlotItem())
            
            self.PW_spectrum[i].setBackground( (62,62,62))
            tabs_spectrum.addTab( self.PW_spectrum[i], f"Ch {i+1}" )
        layout_lower.addWidget( tabs_spectrum ) 

        self.live_plotter = vivi_plot.Plotter( self.PW_live_view, self.PW_spectrum, self.II_spectrum )
        self.group_viviewer.setEnabled( False )

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

    def on_checked_average( self ):
        self.live_plotter.set_plot_average( self.CheckBox_average.isChecked() )

    def on_click_browse( self ):
        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.LE_save_path.setText( folderpath )
        self.save_status.setText( "Folder Path Set")


    def on_quit( self ):
        print("Exiting Vivi")
        if not self.board == None:
            self.board.set_stop( True )
            time.sleep(0.5)
            self.disconnect_device()

    def on_status_change( self,value ):
        if value == -1: # Board not Ready
            self.PB_live_start.setEnabled( False )
            self.PB_acquire_start.setEnabled( False )
        elif value == 0:# Board Ready
            self.PB_live_start.setEnabled( True )
            self.PB_acquire_start.setEnabled( True )
            self.PB_acquire_start.setText( "Acquire: Start")
            self.group_device_setting.setEnabled( True )
            self.group_live_control.setEnabled( True )

    def on_click_start_acquire(self):
        if self.board.connected:
            if self.PB_acquire_start.text() == "Acquire: Start":
                # Acq Param
                acquire_time = int( self.LE_acquire_time.text() )
                sampling = self.sampling
                gains = []
                for i in range(4):
                    gains.append( int(self.CB_gains[i].currentText()) )

                if gains[0] == gains[1] and gains[0] == gains[2] and gains[0] == gains[3]:
                    gains = gains[0]

                self.timestamp = time.strftime( "%H%M", time.localtime())
                fname = f"{self.timestamp}_Acquire_{acquire_time}s_Sampling_{sampling}Hz_Gain_{gains}"
                self.fpath = os.path.join(self.LE_save_path.text(), fname)

                self.board.set_acquire_time( acquire_time )

                NUM_DFT = int( self.LE_num_dft_live.text() )
                num_pts = math.ceil(NUM_DFT/2)
                xscale = sampling / NUM_DFT
                xs = xscale* np.arange( num_pts )
                ys = np.zeros_like( xs )

                self.live_plotter.init_plot_board( xs )

                self.board.set_acquire_mode( "capture" )
                self.board.set_listening( False )

                self.PB_acquire_start.setText( "Acquire: Stop")
                self.group_device_setting.setEnabled( False )
                self.group_live_control.setEnabled( False )
                self.LE_num_dft_acquire.setEnabled( False )
                self.LE_acquire_time.setEnabled( False )

            elif self.PB_acquire_start.text() == "Acquire: Stop":
                self.board.set_stop( True )
                self.PB_acquire_start.setText( "Acquire: Start")
                self.group_device_setting.setEnabled( True )
                self.group_live_control.setEnabled( True )
                self.LE_num_dft_acquire.setEnabled( True )
                self.LE_acquire_time.setEnabled( True )

    def on_click_start_view(self):
        if self.board.connected:
            if self.PB_live_start.text() == "Live: Start":
                
                # Acq Param
                sampling = self.sampling
                self.live_plotter.sampling = sampling

                gains = []
                for i in range(4):
                    gains.append( int(self.CB_gains[i].currentText()) )

                if gains[0] == gains[1] and gains[0] == gains[2] and gains[0] == gains[3]:
                    gains = gains[0]

                self.timestamp = time.strftime( "%H%M", time.localtime())
                fname = f"{self.timestamp}_Live_Sampling_{sampling}Hz_Gain_{gains}"
                self.fpath = os.path.join(self.LE_save_path.text(), fname)
                self.live_file = open( self.fpath, 'w')


                # Pre-set dft
                NUM_DFT = int( self.LE_num_dft_live.text() )
                if NUM_DFT % 2 == 0: #If is Even
                    num_pts = int( (NUM_DFT/2)+1 ) -1
                else:
                    num_pts = int( (NUM_DFT+1)/2 ) -1
                xscale = self.sampling / NUM_DFT
                xs = xscale* np.arange( num_pts )

                self.board.set_num_live_sample( int( self.LE_num_live_sample.text() ) )
                self.live_plotter.num_sample = int( self.LE_num_live_sample.text() )
                self.live_plotter.init_plot_board( xs )
                self.live_plotter.init_spectrum( num_pts )

                self.board.set_acquire_mode( "live" )
                self.board.set_listening( False )
                self.PB_live_start.setText( "Live: Stop")
                self.group_device_setting.setEnabled( False )
                self.group_acquire_control.setEnabled( False )
                self.LE_num_dft_live.setEnabled( False )
                self.LE_num_live_sample.setEnabled( False )
                self.CheckBox_average.setEnabled( False )
            elif self.PB_live_start.text() == "Live: Stop":
                self.board.set_stop( True )
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

    def received_acquire_data( self, value):
        if not value==[-1]:
            volts = np.array(value)
            NUM_DFT = int( self.LE_num_dft_acquire.text())
            xs, spectra = self.calc_noise_density( volts, rate=self.sampling, NUM_DFT=NUM_DFT )

            self.live_plotter.update_plot_board( xs, spectra )

            acquire_file = open(self.fpath, 'w')
            for line in value:
                acquire_file.write(f"{line[0]}, {line[1]}, {line[2]}, {line[3]}\n") # works with any number of elements in a line
            acquire_file.close()

            self.save_status.setText( f"File Saved time stamp: {self.timestamp}")

        
        self.LE_num_dft_acquire.setEnabled( True )
        self.LE_acquire_time.setEnabled( True )


    def received_live_data( self, value ):
        volts = np.array(value)
        NUM_DFT = int( self.LE_num_dft_live.text())
        xs, spectra = self.calc_noise_density( volts, rate=self.sampling, NUM_DFT=NUM_DFT )

        self.live_plotter.update_plot_board( xs, spectra )
        self.live_plotter.update_spectrum( spectra )
        
        for line in value:
            self.live_file.write(f"{line[0]}, {line[1]}, {line[2]}, {line[3]}\n") 

    def received_msg( self, value ):
        self.TE_deviceStatus.append( value )
        if value.startswith("Sampling rate "):
            parts = value.split(' ')
            self.sampling = float(parts[4])
            self.TB_sampling.setText( f"{self.sampling:.2f}" )
    def send_command( self, msg ):      
        # Send Serial Command and Listen
        # Post result to Text Board
        if self.board.connected:
            self.board.send_command( msg )
        else:
            self.TE_deviceStatus.append( "\nConnect to send a command" )

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
        self.sampling = float( self.TB_sampling.text() )

    def on_click_send(self):
        self.send_command( self.LE_command.text() )

    def on_click_clear(self):
        self.TE_deviceStatus.setText("")

    def on_click_connect(self):
        # Connect Push Button
        if self.PB_connect.text() == "Connect":
            self.connect_device()
        elif self.PB_connect.text() == "Disconnect":
            self.disconnect_device()

    def connect_device(self):
        
        if self.board == None:
            self.board = vivi.Board( None )
            self.board.msg_out.connect( self.received_msg )
            self.board.status_signal.connect( self.on_status_change )
            self.board.live_data.connect( self.received_live_data )
            self.board.acquire_data.connect( self.received_acquire_data )
            self.board.elapsed_time.connect( self.received_elapsed_time)

        if self.board.connected:
            self.board.close_board()

        if len(self.port_list) > 0:
            portname = self.port_list[self.dev_list.currentIndex()].device
            self.board.connect_board( portname )

            self.thread = QThread()
            self.board.moveToThread(self.thread)
            self.thread.started.connect( self.board.start_comm )
            self.thread.start()

            self.PB_send.setEnabled( True )
            self.PB_connect.setText( "Disconnect" )
            self.group_device_setting.setEnabled( True )
            self.group_viviewer.setEnabled( True )

            self.board.init_settings()


    def disconnect_device( self ):
        if self.board.connected:
            self.board.set_stop( True )
            time.sleep(0.5)
            self.board.set_connected( False )
            self.thread.quit()
            self.board.close_board()
            self.PB_send.setEnabled( False )
            self.PB_connect.setText( "Connect" )
            self.group_device_setting.setEnabled( False )
            self.group_viviewer.setEnabled( False )

    def dev_changed(self):
        print( "Selected: "+self.dev_list.currentText())
        self.connect_device(  )
    
    """Program to compute noise spectral density in nV / sqrt(Hz) for ADC-8 data."""
    def calc_noise_density( self, data, rate, NUM_DFT ):
        rate = float(rate)
        nchans = 4
        
        nsamples = data.shape[0]
        
        total_power = np.zeros((NUM_DFT // 2 + 1, nchans))
        navg = 0

        for i in range(0, nsamples - NUM_DFT, NUM_DFT):
            f = np.fft.rfft(data[i:, :], NUM_DFT, axis=0)		# Noise spectrum
            f = np.square(np.real(f)) + np.square(np.imag(f))	# Power spectrum
            total_power += f
            navg += 1


        f = np.sqrt(total_power / navg)

        # Normalize and convert to nV / sqrt(Hz)
        f *= 1.0e9 / math.sqrt(NUM_DFT * 0.5 * rate)

        # Round off to a reasonable number of decimals
        f = f.round(6)


        xscale = rate / NUM_DFT
        xs = xscale* np.arange( f.shape[0] )

        return xs, f
        


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.aboutToQuit.connect( window.on_quit )


app.exec()