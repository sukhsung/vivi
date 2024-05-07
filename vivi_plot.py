# vivi_plot.py
# Manage Plotting Aspects
from PyQt5.QtCore import (QObject)
# from PyQt6.QtWidgets import QWidget
import pyqtgraph as pg
import numpy as np
from math import sqrt

class Plotter(QObject):
    def __init__(self):
        super().__init__() #Inherit QObject
        pg.setConfigOption('background', "#393939")
        pg.setConfigOption('foreground', "#FFFFFF")
        
        self.nchans = 8
        self.labels = [f"Ch {i+1}" for i in range(self.nchans)]
        self.plot_enable = [True for i in range(self.nchans)]

        # Spectrum
        self.PW_spectrum = pg.plot()
        self.legend = self.PW_spectrum.addLegend()
        self.legend.setOffset( -1 )
        
        # Spectrograph
        self.PW_spectrogram = [pg.plot() for i in range(8)]
        self.II_spectrogram = [pg.ImageItem(img= np.zeros((128,64))) for i in range(8)]
        for i in range(8):
            self.PW_spectrogram[i].getPlotItem().addItem(self.II_spectrogram[i])
            colorbar = ( pg.ColorBarItem( values=(1,10), colorMap=pg.colormap.get('inferno') ))
            colorbar.setImageItem( self.II_spectrogram[i], insert_in=self.PW_spectrogram[i].getPlotItem())
            # self.PW_spectrogram[i].setBackground( (62,62,62))

        # Integrated Intensity
        self.PW_integrated = pg.plot()
        self.PW_integrated.setBackground((57, 57, 57))

        colors = [(239,48,90), (255, 248, 238), (242,132,68), (29,188,82),
                  (29,188,82), (29,188,82), (29,188,82), (29,188,82)]
        self.pen = [ pg.mkPen( colors[i], width=2) for i in range(8)]
        self.pen_ave = [ pg.mkPen( colors[i], width=4) for i in range(8)]

        self.Image_spectrogram = []
        self.plot_spectrum = []
        self.plot_spectrum_ave = []
        self.plot_integrated = []


        self.sampling = 0
        self.num_sample = 0
        self.num_dft = 0
        self.plot_average = True

        self.fs = []

    def init_all(self):
        # Set Axes
        if self.num_dft % 2 == 0: #If is Even
            self.num_fs = int( (self.num_dft/2)+1 ) -1
        else:
            self.num_fs = int( (self.num_dft+1)/2 ) -1
        self.fscale = self.sampling / self.num_dft
        self.fs = self.fscale* np.arange( self.num_fs )
        self.fmax = self.fs[-1]

        self.num_ts = 2*self.num_fs
        self.tscale = self.num_sample/self.sampling
        self.ts= self.tscale*np.arange(self.num_ts)
        self.tmax = self.ts[-1]

    def init_spectrum(self):
        for p in self.plot_spectrum:
            p.clear()
        for p in self.plot_spectrum_ave:
            p.clear()
        self.legend.clear()

        ys = np.zeros_like( self.fs )
        self.plot_spectrum = [self.PW_spectrum.plot( self.fs, ys+1, pen=self.pen[i], name=self.labels[i]) for i in range(self.nchans)]
        if self.plot_average:
            self.plot_spectrum_ave = [self.PW_spectrum.plot( self.fs, ys+1, pen=self.pen_ave[i] ) for i in range(self.nchans)]

            # if self.plot_enable[i]:
            #     self.plot_spectrum[i].show()
            # else:
            #     self.plot_spectrum[i].show()

        self.y_counter = 0
        self.PW_spectrum.setLogMode(False, True)
        self.PW_spectrum.setLimits( yMin=0, yMax=12, xMin=0, xMax=self.fmax)
        self.PW_spectrum.setRange( yRange=(0, 7), disableAutoRange=True)
        self.PW_spectrum.getAxis('bottom').setLabel(text="Frequency", units="Hz",unitPrefix=None)
           

    def init_spectrogram( self ):
        fticks_pos = np.linspace(0, self.num_fs, 5)
        fs = np.linspace(0, self.sampling/2, 5)
        major_ticks = []
        for i in range(5):
            major_ticks.append( (fticks_pos[i], f"{fs[i]:.2f}") )
        fticks = [ major_ticks, [] ]

        t_step = self.num_sample/self.sampling
        yticks_pos = np.linspace(0, self.num_ts, 11)
        ts= np.linspace(0, t_step*self.num_ts, 11)
        major_ticks = []
        for i in range(11):
            major_ticks.append( (yticks_pos[i], f"{ts[i]:.1f}") )
        tticks = [ major_ticks, [] ]

        self.Image_spectrogram = [np.zeros( (self.num_ts, self.num_fs)) for i in range(8)]
        self.Image_spectrogram_log = [np.zeros( (self.num_ts, self.num_fs)) for i in range(8)]
        for i in range(8):
            self.PW_spectrogram[i].setYRange( 0, self.num_fs, padding=0 )
            self.PW_spectrogram[i].setXRange( 0, self.num_ts, padding=0 )
            self.PW_spectrogram[i].setLimits( xMin=0, xMax=self.num_ts, yMin=0, yMax= (self.num_fs*1.00) )
            axX = self.PW_spectrogram[i].getAxis('left')
            axX.setLabel(text="Frequency", units="Hz", unitPrefix=None)
            axX.setTicks( fticks )
            axY = self.PW_spectrogram[i].getAxis('bottom')
            axY.setLabel(text="Time", units="s", unitPrefix=None)
            axY.setTicks( tticks )

    def init_integrated( self ):
        for p in self.plot_integrated:
            p.clear()

        ys = np.zeros_like( self.ts )
        self.plot_integrated = [self.PW_integrated.plot( self.ts, ys+1, pen=self.pen[i], name="Ch. {}".format(i+1)) for i in range(8)]
        
        # self.y_counter = 0
        self.PW_integrated.setLogMode(False, True)
        self.PW_integrated.setLimits( yMin=0, yMax=12, xMin=0, xMax=self.tmax)
        self.PW_integrated.setRange( yRange=(0, 7), disableAutoRange=True)
        self.PW_integrated.getAxis('bottom').setLabel(text="Time", units="s", unitPrefix=None)

    def update_all(self, volts, spectrogram):
        spectra = self.calc_noise_density( volts, rate=self.sampling, NUM_DFT=self.num_dft, nchans=self.nchans )

        self.update_spectrum( spectra )
        if spectrogram:
            self.update_spectrogram( spectra )
            self.update_integrated()

    def update_spectrum(self, data):
        self.y_counter += 1
        for i in range(self.nchans):
            self.plot_spectrum[i].setData( self.fs, data[1:,i])

            self.plot_spectrum[i].setVisible( self.plot_enable[i])

            if self.plot_average:
                if self.y_counter < self.num_ts:
                    y_mean = np.mean( self.Image_spectrogram[i][:self.y_counter],0 )
                else:
                    y_mean = np.mean( self.Image_spectrogram[i],0 )

                self.plot_spectrum_ave[i].setData( self.fs, y_mean)
                self.plot_spectrum_ave[i].setVisible( self.plot_enable[i])

    def update_spectrogram( self, data ):
        for i in range(self.nchans):
            self.Image_spectrogram[i] = np.roll( self.Image_spectrogram[i], 1, axis=(0))
            self.Image_spectrogram_log[i] = np.roll( self.Image_spectrogram_log[i], 1, axis=(0))
            self.Image_spectrogram[i][0,:] = data[1:,i]
            self.Image_spectrogram_log[i][0,:] = np.log10(1+data[1:,i])
            self.II_spectrogram[i].setImage(self.Image_spectrogram_log[i],autoLevels=False )

    def update_integrated( self ):
        for i in range(self.nchans):
            self.plot_integrated[i].setData( self.ts, np.mean(self.Image_spectrogram[i], axis=1 ))

    def set_plot_average( self, value ):
        self.plot_average = value

    def set_plot_enable( self, CB_plot):
        for i in range( self.nchans ):
            self.plot_enable[i] = CB_plot[i].isChecked()

    """Program to compute noise spectral density in nV / sqrt(Hz) for ADC-8 data."""
    def calc_noise_density( self, data, rate, NUM_DFT, nchans ):
        rate = float(rate)
        
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
        f *= 1.0e9 / sqrt(NUM_DFT * 0.5 * rate)

        # Round off to a reasonable number of decimals
        f = f.round(6)

        return f