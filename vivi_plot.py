# vivi-plot.py
# Manage Plotting Aspects
import time
from PyQt6.QtCore import (Qt, pyqtSignal, QTimer, QObject)
from PyQt6.QtWidgets import QWidget
import pyqtgraph as pg
import numpy as np

class Plotter(QObject):

    """Represent a single Plot Board"""
    def __init__(self, plot_widget, PW_spectrum, spectrum_widget):
        super().__init__() #Inherit QObject

        self.NUM_CHANNELS = 4
        self.Plot_Widget = plot_widget
        self.PW_spectrum = PW_spectrum
        self.Spectrum_Widget = spectrum_widget
        self.Spectrum_image = []

        self.Plot_Widget.setBackground((57, 57, 57))
        self.Plot_Objs = []
        self.Plot_Ave_Objs = []
        self.legend = self.Plot_Widget.addLegend()

        self.pen = []
        self.pen.append( pg.mkPen((239,48,89), width=2))
        self.pen.append( pg.mkPen((255,248,238), width=2))
        self.pen.append( pg.mkPen((242,132,68),  width=2))
        self.pen.append( pg.mkPen((29,188,82), width=2))

        self.pen_ave = []
        self.pen_ave.append( pg.mkPen((239,48,89), width=4))
        self.pen_ave.append( pg.mkPen((255,248,238), width=4))
        self.pen_ave.append( pg.mkPen((242,132,68),  width=4))
        self.pen_ave.append( pg.mkPen((29,188,82), width=4))


        self.sampling = None
        self.num_sample = None
        self.plot_average = True


    def init_plot_board(self, xs ):
        self.xs = xs
        ys = np.zeros_like( xs )
        for p in self.Plot_Objs:
            p.clear()
        for p in self.Plot_Ave_Objs:
            p.clear()
        self.legend.clear()# = self.Plot_Widget.addLegend()
        self.Plot_Objs = []
        self.Plot_Ave_Objs = []

        self.y_sum = []
        self.y_counter = 0
        for i in range(4):
            self.y_sum.append( ys+1 )
            self.Plot_Objs.append(self.Plot_Widget.plot( xs, ys+1, pen=self.pen[i], name="Ch. {}".format(i+1)) )
            
            if self.plot_average:
                self.Plot_Ave_Objs.append(self.Plot_Widget.plot( xs, ys+1, pen=self.pen_ave[i] ))
        
        self.Plot_Widget.setLogMode(False, True)
        self.Plot_Widget.setLimits( yMin=0, yMax=12, xMin=0, xMax=self.sampling/2)
        self.Plot_Widget.setRange( yRange=(0, 7), disableAutoRange=True)

        self.Plot_Widget.getAxis('bottom').setLabel(text="Frequency", units="Hz",unitPrefix=None)

    def update_plot_board(self, xs, data):
        self.y_counter += 1
        for i in range(4):
            self.y_sum[i] += data[1:,i]
            self.Plot_Objs[i].setData( xs[1:], data[1:,i])

            if self.plot_average:
                if self.y_counter < 2*self.num_pts:
                    y_mean = np.mean( self.Spectrum_image[i][:self.y_counter],0 )
                else:
                    y_mean = np.mean( self.Spectrum_image[i],0 )

                self.Plot_Ave_Objs[i].setData( xs[1:], y_mean)
            
            

    def init_spectrum( self, num_pts):
        # for p in self.spectrum_widget:
        #     p.clear()
        # self.counter = np.random.rand( 64,64 )
        self.num_pts= num_pts
        xticks_pos = np.linspace(0, num_pts, 5)
        fs = np.linspace(0, self.sampling/2, 5)
        major_ticks = []
        for i in range(5):
            major_ticks.append( (xticks_pos[i], f"{fs[i]:.2f}") )
        xticks = [ major_ticks, [] ]

        t_step = self.num_sample/self.sampling
        yticks_pos = np.linspace(0, 2*num_pts, 11)
        ts= np.linspace(0, t_step*2*num_pts, 11)
        major_ticks = []
        for i in range(11):
            major_ticks.append( (yticks_pos[i], f"{ts[i]:.1f}") )
        yticks = [ major_ticks, [] ]


        self.Spectrum_image = []
        self.Spectrum_image_log = []
        for i in range(4):
            self.Spectrum_image.append( np.zeros( (2*num_pts, num_pts)) )
            self.Spectrum_image_log.append( np.zeros( (2*num_pts, num_pts)) )
            # self.Spectrum_Widget[i].addColorBar( colormap='viridis')
            self.PW_spectrum[i].setYRange( 0, num_pts, padding=0 )
            self.PW_spectrum[i].setXRange( 0, 2*num_pts, padding=0 )
            self.PW_spectrum[i].setLimits( xMin=0, xMax=2*num_pts, yMin=0, yMax= (num_pts*1.05) )
            axX = self.PW_spectrum[i].getAxis('left')
            axX.setLabel(text="Frequency", units="Hz",unitPrefix=None)
            axX.setTicks( xticks )
            axY = self.PW_spectrum[i].getAxis('bottom')
            axY.setLabel(text="Time", units="s",unitPrefix=None)
            axY.setTicks( yticks )

    def update_spectrum( self, data ):
        for i in range(4):
            self.Spectrum_image[i] = np.roll( self.Spectrum_image[i], 1, axis=(0))
            self.Spectrum_image_log[i] = np.roll( self.Spectrum_image_log[i], 1, axis=(0))
            self.Spectrum_image[i][0,:] = data[1:,i]
            self.Spectrum_image_log[i][0,:] = np.log10(1+data[1:,i])
            self.Spectrum_Widget[i].setImage(self.Spectrum_image_log[i],autoLevels=False )

    def set_plot_average( self, value ):
        self.plot_average = value