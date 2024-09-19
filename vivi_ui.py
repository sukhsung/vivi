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
    QProgressBar,
    QStyleFactory
)
from PyQt5.QtGui import QFont, QFontDatabase,QIcon
from PyQt5.QtSvg import QSvgWidget

import sys, os, time, json, glob
import vivi, vivi_plot
import numpy as np
from functools import partial
from datetime import datetime
import serial.tools.list_ports

from vivi_makeUI import Ui_MainWindow

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.vivi_path=os.path.dirname(os.path.abspath(__file__))
        self.asset_path = os.path.join( self.vivi_path, 'assets')

        self.setupUi(self)

        # print("HI")
        # print(self.group_left.

        self.setWindowTitle("Vivi")
        self.board = None

        self.make_panel_device()
        self.make_panel_viewer()
        self.make_panel_banner()

        self.group_left.resizeEvent = self.group_left_resize_event

    def group_left_resize_event(self,event):
        self.svg_logo_main.resize(self.group_logo.width(), self.group_logo.width())
        self.svg_logo_disabled.resize(self.group_logo.width(), self.group_logo.width())


    def make_panel_device( self ):
        self.dev_list.activated.connect( self.on_dev_selected )
        self.LE_URL.setText( "<hostname>:<port>")
        self.PB_connect.clicked.connect( self.on_click_connect )
        self.PB_refresh.clicked.connect( self.update_port_list )

        self.update_port_list()

        # Settings Panel
        self.group_device_setting.setVisible( False )

        # All Channel Settings
        self.CB_allGains.addItems( ["128", "64", "32", "16", "8","1"])
        self.CB_allGains.activated.connect( self.set_all_gains )

        # Sampling Setting
        self.TB_sampling.setText("400.00")
        self.TB_sampling.editingFinished.connect( self.set_sampling ) 

        # Individual Gain Channels
        self.TB_gains_labels = [self.TB_gains_label_1,
                                self.TB_gains_label_2,
                                self.TB_gains_label_3,
                                self.TB_gains_label_4,
                                self.TB_gains_label_5,
                                self.TB_gains_label_6,
                                self.TB_gains_label_7,
                                self.TB_gains_label_8]
        
        self.group_channels =  [self.group_channel_1,
                                self.group_channel_2,
                                self.group_channel_3,
                                self.group_channel_4,
                                self.group_channel_5,
                                self.group_channel_6,
                                self.group_channel_7,
                                self.group_channel_8]
        
        self.CB_gains = [self.CB_gain_1,
                         self.CB_gain_2,
                         self.CB_gain_3,
                         self.CB_gain_4,
                         self.CB_gain_5,
                         self.CB_gain_6,
                         self.CB_gain_7,
                         self.CB_gain_8]
# 
        for i in range(8):
            self.CB_gains[i].addItems( ["128", "64", "32", "16", "8","1"])
            self.CB_gains[i].activated.connect( partial(self.set_individual_gain,i) )
            self.TB_gains_labels[i].editingFinished.connect( self.set_label )
            self.group_channels[i].setHidden(True)

        self.PB_closeCMD.clicked.connect( self.on_click_closeCMD )

        # # Device Console
        self.TE_deviceStatus.setText( "Connect to an ADC-8 Board to start" )
        self.TE_deviceStatus.setReadOnly(True)
        self.LE_command.returnPressed.connect( self.on_click_send )
        self.PB_send.clicked.connect( self.on_click_send )
        self.PB_clear.clicked.connect( self.on_click_clear )
        self.group_cmd.setVisible(False)
    
    def make_panel_viewer( self ):
        # Load Plot Manager
        self.plotter = vivi_plot.Plotter(  )

        # Acquisition Viewer Panel
        self.PB_live_start.clicked.connect( self.on_click_start_view )
        self.LE_num_live_sample.setText("512")
        self.LE_num_dft_live = QLineEdit("128")
        self.LE_num_dft_live.setText("128")
        self.CheckBox_average.setChecked( False )

        self.CB_plot =[self.CB_plot_1,
                       self.CB_plot_2,
                       self.CB_plot_3,
                       self.CB_plot_4,
                       self.CB_plot_5,
                       self.CB_plot_6,
                       self.CB_plot_7,
                       self.CB_plot_8]
        for i in range(8):
            self.CB_plot[i].setChecked( True )
            self.CB_plot[i].setHidden( True )
            self.CB_plot[i].stateChanged.connect( self.set_plot_enable )

 
        self.PB_acquire_start.clicked.connect( self.on_click_start_acquire )
        self.LE_acquire_time.setText("3")

        self.layout_spectrum.addWidget( self.plotter.PW_spectrum )

        # Save Control
        today = datetime.today().strftime('%Y-%m-%d')# Get Today
        savepath = os.path.join( self.vivi_path, 'results', today)
        self.LE_save_path.setText(savepath)
        self.LE_save_path.editingFinished.connect( self.on_save_path_change )
        self.PB_browse.clicked.connect( self.on_click_browse )
        self.PB_open.clicked.connect( self.on_click_open )
        self.on_save_path_change()

        for i in range( 8 ):
            self.tabs_spectrogram.addTab( self.plotter.PW_spectrogram[i], f"Ch {i+1}" )
            self.tabs_spectrogram.setTabVisible(i,True)
        self.tabs_spectrogram.addTab( self.plotter.PW_integrated, "Integrated Power")

        # self.plotter.initialize()
        self.group_viviewer.setEnabled( False )

    def make_panel_banner( self ):

        # Loading SVG
        self.svg_logo_main = QSvgWidget( os.path.join(self.asset_path,'vivi-main.svg'), parent=self.group_logo)
        self.svg_logo_main.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.svg_logo_main.setContentsMargins( 0,0,0,0 )
        self.svg_logo_main.setVisible(False)


        self.svg_logo_disabled = QSvgWidget( os.path.join(self.asset_path,'vivi-disabled.svg'), parent=self.group_logo)
        self.svg_logo_disabled.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.svg_logo_disabled.setContentsMargins( 0,0,0,0 )

        self.group_logo.mouseDoubleClickEvent = self.enable_logo
        self.on_click_closeCMD()

    def enable_logo(self,a):
        self.group_logo.setVisible(False)
        self.group_cmd.setVisible(True)
        self.layout_left.setStretch(0,1)
        self.layout_left.setStretch(1,0)
        self.layout_left.setStretch(2,3)
        self.layout_left.setStretch(3,0)
        self.layout_left.setStretch(4,0)

    def on_click_closeCMD(self):
        self.group_logo.setVisible(True)
        self.group_cmd.setVisible(False)
        self.layout_left.setStretch(0,1)
        self.layout_left.setStretch(1,1)
        self.layout_left.setStretch(2,3)
        self.layout_left.setStretch(3,3)
        self.layout_left.setStretch(4,1)

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
            self.group_device_setting.setVisible( False )
            self.group_viviewer.setEnabled( False )
            self.svg_logo_disabled.setVisible( True )
            self.svg_logo_main.setVisible( False )
        elif status == "LISTENING":# Board Ready
            self.group_device_setting.setVisible( True )
            self.group_viviewer.setEnabled( True )
            self.group_acquire_control.setEnabled( True )
            self.group_live_control.setEnabled( True )
            self.group_save_control.setEnabled( True )
            self.PB_acquire_start.setText( "Acquire: Start")
            self.PB_live_start.setText( "Live: Start")
            self.svg_logo_disabled.setVisible( False )
            self.svg_logo_main.setVisible( True )
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
            self.group_device_setting.setVisible( False )
            self.group_viviewer.setEnabled( False )
            self.svg_logo_disabled.setVisible( True )
            self.svg_logo_main.setVisible( False )
            self.update_port_list()

    def on_dev_selected( self ):
        if self.dev_list.currentText() == "RFC 2217":
            self.LE_URL.setVisible(True)
            self.dev_list.setMaximumWidth(100)
            self.LE_URL.setMinimumWidth(130)
        else:
            self.LE_URL.setVisible(False)
            self.dev_list.setMaximumWidth(300)

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


            self.group_device_setting.setVisible( False )
            self.group_live_control.setEnabled( False )

            self.PB_acquire_start.setText( "Acquire: Stop")
            self.LE_num_dft_acquire.setEnabled( False )
            self.LE_acquire_time.setEnabled( False )
            self.Progress_Acquistion.setValue(0)

        elif self.PB_acquire_start.text() == "Acquire: Stop":
            self.board.set_status( "STOPPING" )
            self.PB_acquire_start.setText( "Acquire: Start")
            self.group_device_setting.setVisible( True )
            self.group_live_control.setEnabled( True )
            self.LE_num_dft_acquire.setEnabled( True )
            self.LE_acquire_time.setEnabled( True )

    def on_click_start_view(self):
        if self.PB_live_start.text() == "Live: Start":
            self.prepare_acquisition("live")
            self.live_file = open( self.fpath, 'w')
            self.board.set_status( "LIVE" )

            self.PB_live_start.setText( "Live: Stop")
            self.group_device_setting.setVisible( False )
            self.group_acquire_control.setEnabled( False )
            self.LE_num_dft_live.setEnabled( False )
            self.LE_num_live_sample.setEnabled( False )
            self.CheckBox_average.setEnabled( False )
        elif self.PB_live_start.text() == "Live: Stop":
            self.board.set_status( "STOPPING" )

            self.PB_live_start.setText( "Live: Start")
            self.group_device_setting.setVisible( True )
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
            new_port_list = vivi.get_port_list()
            if not cur_port_list == new_port_list:
                self.update_port_list()
            else:
                self.connect_device()
        elif self.PB_connect.text() == "Disconnect":
            self.disconnect_device()


    def update_port_list(self):
        # Remove Current List
        for i in range(self.dev_list.count()):
            self.dev_list.removeItem(0)

        # Update Port List
        self.port_list = vivi.get_port_list()
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
            self.group_device_setting.setVisible( False )
            self.group_viviewer.setEnabled( False )

    def on_quit( self ):
        print("Exiting Vivi")
        self.disconnect_device()
    ###
    
        
if __name__ == "__main__":
    app = QApplication(sys.argv)

    vivi_path = os.path.dirname(os.path.abspath(__file__))
    asset_path = os.path.join( vivi_path, 'assets')

    with open( os.path.join( asset_path,"style.css"),"r") as fh:
        app.setStyleSheet(fh.read())


    app.setWindowIcon(QIcon(os.path.join(asset_path,"vivi-icon.png")))
    app.setApplicationName("Vivi")


    window = MainWindow()
    window.setWindowIcon(QIcon(os.path.join(asset_path,"vivi-icon.png")))
    window.show()
    window.resize(1280,719)
    window.resize(1280,720)

    app.aboutToQuit.connect( window.on_quit )


    app.exec()