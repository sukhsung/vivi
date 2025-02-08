from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QFileDialog, QMenu,
    QDialog, QGroupBox, QVBoxLayout, QHBoxLayout
)
from PySide6.QtGui import QIcon, QAction
from PySide6.QtSvgWidgets import QSvgWidget

import sys, os, time, json, glob
import numpy as np
from functools import partial
from datetime import datetime

import vivi_device, vivi_plot
# from vivi_makeUI import Ui_MainWindow

from UI_makers.vivi_makeUI_main import Ui_MainWindow
from UI_makers.vivi_makeUI_deviceDialog import Ui_device_dialog
from vivi_device_manager import device_manager

from vivi_console import device_console
 

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.vivi_path=os.path.dirname(os.path.abspath(__file__))
        self.asset_path = os.path.join( self.vivi_path, 'assets')

        with open( os.path.join( self.asset_path,"style.css"),"r") as fh:
            self.css = fh.read()
        self.icon = QIcon(os.path.join(self.asset_path,"vivi-icon.png"))

        self.setupUi(self)
        self.setWindowTitle("Vivi")


        self.dev_vivi = vivi_device.ADC8()
        self.thread_main = QThread.currentThread()

        self.console_vivi = device_console('Geophone Recorder')

        # self.thread_main = QThread.currentThread() 
        # self.dev_vivi = vivi_device.Board()
        # self.dev_vivi.msg_out.connect( self.received_msg )
        self.dev_vivi.signal_status.connect( self.on_status_change )
        self.dev_vivi.live_data.connect( self.received_live_data )
        self.dev_vivi.acquire_data.connect( self.received_acquire_data )
        self.dev_vivi.elapsed_time.connect( self.received_elapsed_time)
        # self.dev_vivi.setting_changed.connect( self.received_setting_changed )
        self.dev_vivi.signal_connected.connect( self.received_connected )

        self.make_panel_viewer()
        self.make_about_dialog()
        self.make_panel_banner()
        self.make_device_dialog()

        self.add_actions()

        # # self.widget_about = AboutWindow()

    def contextMenuEvent(self, event):
        # Show the context menu at the event position
        self.main_contextMenu.exec(event.globalPos())

    def add_actions(self):
        ## Right Click
        self.main_contextMenu = QMenu(self)

        self.action_logo = QAction('About Vivi')
        self.action_device_dialog = QAction('Open Device Manager')
        self.action_adc_dlg = QAction('Open ADC Settings')
        self.action_vivi_cmd = QAction('Open Console')

        self.action_logo.triggered.connect( self.dlg_about.show )
        self.action_device_dialog.triggered.connect( self.open_device_dialog )
        self.action_adc_dlg.triggered.connect( self.dev_manager_vivi.open_adc_setting )
        self.action_vivi_cmd.triggered.connect( self.dev_manager_vivi.console_open )

        self.main_contextMenu.addAction(self.action_logo)
        self.main_contextMenu.addAction(self.action_device_dialog)
        self.main_contextMenu.addAction(self.action_adc_dlg)
        self.main_contextMenu.addAction(self.action_vivi_cmd)

    ### DEVICE DIALOG
    def make_device_dialog(self):
        # Create a Modal Dialog
        self.Ui_device_dialog = Ui_device_dialog()
        self.Ui_device_dialog.widget = QDialog()
        self.Ui_device_dialog.setupUi( self.Ui_device_dialog.widget )
        self.Ui_device_dialog.widget.setModal(True)
        self.Ui_device_dialog.widget.show()
        self.Ui_device_dialog.widget.setWindowTitle("Vivi")

        # Logo on Left
        self.svg_logo_device = QSvgWidget( os.path.join(self.asset_path,'vivi-main.svg'))#, parent=self.group_logo)
        self.Ui_device_dialog.layout_logo = QHBoxLayout( self.Ui_device_dialog.group_logo)
        self.Ui_device_dialog.layout_logo.setContentsMargins( 50,50,50,50 )
        self.Ui_device_dialog.layout_logo.addWidget( self.svg_logo_device )
        self.svg_logo_device.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)

        self.Ui_device_dialog.PB_start_main.clicked.connect( self.start_main)

        self.dev_manager_vivi = device_manager( parent = self,
                                                name = "Geophone Recorder",
                                                device = self.dev_vivi,
                                                ui_stack = self.group_vivi_control,
                                                layout_adc = self.layout_adc,
                                                console = self.console_vivi,
                                                baudrate=9600)

    def start_main( self ):
        self.Ui_device_dialog.widget.close()
        self.Ui_device_dialog.PB_start_main.setVisible( False )
        self.Ui_device_dialog.widget.setWindowTitle("Milí - Device Manager")
        self.show()

    def open_device_dialog(self):
        self.Ui_device_dialog.widget.show()

    def make_panel_banner( self ):
        # Page 0: Logo
        self.svg_logo_enabled = QSvgWidget( os.path.join(self.asset_path,'vivi-main.svg'))#, parent=self.group_logo)
        self.layout_logo_enable = QVBoxLayout( self.group_logo_enable)
        self.layout_logo_enable.addWidget( self.svg_logo_enabled )
        self.svg_logo_enabled.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)

        # self.console_temp.setFont( self.font_mono_XS )

    def make_panel_viewer( self ):
        # Load Plot Manager
        self.plotter = vivi_plot.Plotter(  )

        # Acquisition Viewer Panel
        self.PB_live_start.clicked.connect( self.on_click_start_view )
        self.LE_num_dft.setText("128")
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
            self.CB_plot[i].setVisible( False )
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

    def make_about_dialog( self ):
        self.dlg_about = QDialog(self)
        self.dlg_about.setWindowTitle("About Vivi")
        self.dlg_about.resize(300,450)
        self.dlg_about.setMinimumSize(300,450)
        layout_about = QVBoxLayout()
        self.dlg_about.setLayout( layout_about )
        layout_about.setContentsMargins(15,15,15,15)
        self.dlg_about.setStyleSheet('background-color: black;')
        
        self.group_dlg = QGroupBox()
        layout_about.addWidget(self.group_dlg)
        layout_dlg = QVBoxLayout()
        self.group_dlg.setLayout( layout_dlg )
        layout_dlg.setContentsMargins(0,0,0,0)

        self.group_dlg.setStyleSheet('background-color: #158081;border-radius:15%')


        group_svg = QGroupBox()
        layout_dlg.addWidget( group_svg)
        layout_svg = QVBoxLayout()
        group_svg.setLayout( layout_svg )
        layout_svg.setContentsMargins(0,0,0,0)

        self.svg_about = QSvgWidget( os.path.join(self.asset_path,'vivi-about.svg'))#, parent=group_svg)
        layout_svg.addWidget( self.svg_about )
        self.svg_about.renderer().setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        self.svg_about.resize( 500,900 )

        self.dlg_about.resizeEvent = self.on_resize_dlg_about

    def on_resize_dlg_about( self,event ):
        new_w= int(self.dlg_about.width())
        new_h= int(self.dlg_about.width()*1.5)
        self.dlg_about.resize(new_w, new_h)

    def open_about( self ):
        self.dlg_about.exec_()

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
    def on_click_browse( self ):
        folderpath = QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.LE_save_path.setText( folderpath )
        self.save_status.setText( "Folder Path Set")

    def prepare_metadata( self, fname, acquistion ):
        # Make Python dictionary then dump to JSON
        
        if acquistion == -1:
            acquistion = "live"

        channels = []
        for i in range( self.dev_vivi.NUM_CHANNELS):
            channels.append( {"Channel": (i+1),
                              "Gain": self.dev_vivi.adcs[i]['gain'],
                              "Label": self.dev_vivi.adcs[i]['label']})


        meta = {"filename": fname+".csv",
                "Sampling": self.dev_vivi.sampling,
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


    def on_status_change( self,status ):
        if status == "NOT-READY": # Board not Ready
            self.group_vivi_on.setEnabled(False)
            self.group_viviewer.setEnabled( False )
        elif status == "LISTENING":# Board Ready
            self.PB_acquire_start.setText( "Acquire: Start")
            self.PB_live_start.setText( "Live: Start")
            self.group_live_control.setEnabled( True )
            self.group_acquire_control.setEnabled( True )

            self.PB_acquire_start.setEnabled(True)
            self.PB_live_start.setEnabled(True)
            self.LE_acquire_time.setEnabled( True )
            self.group_vivi_on.setEnabled(True)

        elif status == "LIVE":
            self.PB_live_start.setText( "Live: Stop")
            self.group_live_control.setEnabled( False )
            self.PB_acquire_start.setEnabled(False)
            self.LE_acquire_time.setEnabled( False )
            self.group_vivi_on.setEnabled(False)
        elif status == "ACQUIRE":
            self.PB_acquire_start.setText( "Acquire: Stop")
            self.group_live_control.setEnabled( False )
            self.PB_live_start.setEnabled(False)
            self.LE_acquire_time.setEnabled( False )
            self.group_vivi_on.setEnabled(False)

    def prepare_acquisition(self, mode ):
        self.plotter.sampling = self.dev_vivi.sampling
        
        if mode == "live":
            self.dev_vivi.set_num_live_sample( int( self.LE_num_dft.text() ) )
            
            self.plotter.num_dft = self.dev_vivi.num_live_sample
            self.plotter.num_sample = int( self.LE_num_dft.text() )
            self.plotter.set_plot_average( self.CheckBox_average.isChecked() )
            self.plotter.set_plot_enable( self.CB_plot )
            self.plotter.init_all()
            self.plotter.labels = [adc['label'] for adc in self.dev_vivi.adcs]
            self.plotter.init_spectrum()
            self.plotter.init_spectrogram()
            self.plotter.init_integrated()

            fname = self.prepare_fname()
            self.fpath = os.path.join(self.LE_save_path.text(), fname+".csv")

            self.prepare_metadata( fname, -1 ) #-1 for live acqusition


        elif mode == "acquire":
            acquire_time = int( self.LE_acquire_time.text() )
            self.dev_vivi.set_acquire_time( acquire_time )
            self.plotter.set_plot_average( False )

            self.plotter.num_dft = int( self.LE_num_dft.text() )
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
            self.dev_vivi.set_request( {"func":"acquire"})

            # self.PB_acquire_start.setText( "Acquire: Stop")
        elif self.PB_acquire_start.text() == "Acquire: Stop":
            self.dev_vivi.set_stop()
            print( f"File Saved time stamp: {self.timestamp}")
            # self.PB_acquire_start.setText( "Acquire: Start")

    def on_click_start_view(self):
        if self.PB_live_start.text() == "Live: Start":
            self.prepare_acquisition("live")
            self.live_file = open( self.fpath, 'w')
            self.dev_vivi.set_request( {"func":"live"} )
            # self.PB_live_start.setText( "Live: Stop")
        elif self.PB_live_start.text() == "Live: Stop":
            self.dev_vivi.set_stop()
            print( f"File Saved time stamp: {self.timestamp}")
            # self.PB_live_start.setText( "Live: Start")

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
                for i in range(self.dev_vivi.NUM_CHANNELS):
                    str_out += f"{line[i]}, "
                str_out = str_out[:-2]
                str_out += "\n"
                acquire_file.write(str_out) # works with any number of elements in a line
            
            acquire_file.close()
            print( f"File Saved time stamp: {self.timestamp}")
            self.PB_acquire_start.setText( "Acquire: Start")

    def received_live_data( self, value ):
        if value == ["STOP"]:
            self.live_file.close()
        else:
            volts = np.array(value)
            self.plotter.update_all( volts, spectrogram=True)
            for line in value:
                str_out = ""
                for i in range(self.dev_vivi.NUM_CHANNELS):
                    str_out += f"{line[i]}, "
                str_out = str_out[:-2]
                str_out += "\n"
                self.live_file.write(str_out) 

    def set_plot_enable( self ):
        for i in range(self.dev_vivi.NUM_CHANNELS):
            self.plotter.plot_enable[i] = self.CB_plot[i].isChecked()

        self.plotter.set_plot_enable( self.CB_plot )

    def received_connected( self, val ): 
        if val: # CONNECTED
            for i in range(8):
                if i<self.dev_vivi.NUM_CHANNELS:
                    # Enabled Channels
                    self.tabs_spectrogram.setTabVisible(i, True)
                    self.CB_plot[i].setVisible( True )
                else:
                    # Disabled channels
                    self.tabs_spectrogram.setTabVisible(i, False)
                    self.CB_plot[i].setVisible( False )

            self.plotter.nchans = self.dev_vivi.NUM_CHANNELS
            
            self.group_viviewer.setEnabled( True )
            self.group_live_control.setEnabled( True )
            self.group_acquire_control.setEnabled( True )
            self.group_save_control.setEnabled( True )

            # Init settings
            # self.dev_vivi.

        else: # Disconnected

            self.group_viviewer.setEnabled( False )
            self.group_live_control.setEnabled( False )
            self.group_acquire_control.setEnabled( False )
            self.group_save_control.setEnabled( False )
            print("disconnected")


    def on_quit( self ):
        print("Exiting Vivi")
        self.dev_manager_vivi.disconnect_device()
    
        
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