# vivi-plot.py
# Manage Plotting Aspects
import time
from PyQt6.QtCore import (Qt, pyqtSignal, QTimer, QObject)
from PyQt6.QtWidgets import QWidget
import pyqtgraph as pg
import struct
import numpy as np

class Plotter(QObject):

    """Represent a single Plot Board"""
    def __init__(self, plot_widget,spectrum_widget):
        super().__init__() #Inherit QObject

        self.NUM_CHANNELS = 4
        self.Plot_Widget = plot_widget
        self.Spectrum_Widget = spectrum_widget
        self.Spectrum_image = []

        self.Plot_Widget.setBackground((57, 57, 57))
        self.Plot_Objs = []
        self.legend = self.Plot_Widget.addLegend()

        self.pen = []
        self.pen.append( pg.mkPen((239,48,89), width=3))
        self.pen.append( pg.mkPen((255,248,238), width=3))
        self.pen.append( pg.mkPen((242,132,68),  width=3))
        self.pen.append( pg.mkPen((29,188,82), width=3))


    def init_plot_board(self, xs ):
        self.xs = xs
        ys = np.zeros_like( xs )
        for p in self.Plot_Objs:
            p.clear()
        self.legend.clear()# = self.Plot_Widget.addLegend()
        self.Plot_Objs = []
        for i in range(4):
            self.Plot_Objs.append(self.Plot_Widget.plot( xs, ys, pen=self.pen[i], name="Ch. {}".format(i+1)) )
    def update_plot_board(self, xs, data):
        for i in range(4):
            self.Plot_Objs[i].setData( xs, data[:,i])
        self.Plot_Widget.setLogMode(False, True)

    def init_spectrum( self, num_pts):
        # for p in self.spectrum_widget:
        #     p.clear()
        self.Spectrum_image = []
        for i in range(4):
            self.Spectrum_image.append( np.zeros( (num_pts, num_pts)) )


    def update_spectrum( self, data ):

        for i in range(4):
            self.Spectrum_image[i] = np.roll( self.Spectrum_image[i], (0,1))
            self.Spectrum_image[i][:,0] = np.log10(1+data[1:,i])
            self.Spectrum_Widget[i].setImage(self.Spectrum_image[i])

