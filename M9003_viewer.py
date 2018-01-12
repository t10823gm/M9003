# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 16:18:12 2018

@author: maryu
"""
import sys
from PyQt5.QtWidgets import (QGraphicsScene, QApplication, QMainWindow, QGridLayout, QVBoxLayout, 
                             QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QSizePolicy)
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

from ui import qt_ui
from math import pow

import random
import numpy as np

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as Canvas
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib
from numpy import arange, sin, pi
# Ensure using PyQt5 backend
#matplotlib.use('QT5Agg')

# Matplotlib widget

class MatplotlibWidget(Canvas):
    """
    MatplotlibWidget inherits PyQt4.QtGui.QWidget or PyQt5.QtWidgets.QWidget
    and matplotlib.backend_bases.FigureCanvasBase
    Options: option_name (default_value)
    -------
    parent (None): parent widget
    title (''): figure title
    xlabel (''): X-axis label
    ylabel (''): Y-axis label
    xlim (None): X-axis limits ([min, max])
    ylim (None): Y-axis limits ([min, max])
    xscale ('linear'): X-axis scale
    yscale ('linear'): Y-axis scale
    width (4): width in inches
    height (3): height in inches
    dpi (100): resolution in dpi
    hold (False): if False, figure will be cleared each time plot is called
    Widget attributes:
    -----------------
    figure: instance of matplotlib.figure.Figure
    axes: figure axes
    Example:
    -------
    self.widget = MatplotlibWidget(self, yscale='log', hold=True)
    from numpy import linspace
    x = linspace(-10, 10)
    self.widget.axes.plot(x, x**2)
    self.wdiget.axes.plot(x, x**3)
    """
    def __init__(self, parent=None, title='', xlabel='', ylabel='',
                 xlim=None, ylim=None, xscale='linear', yscale='linear',
                 width=4, height=3, dpi=100, hold=False):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_title(title)
        self.axes.set_xlabel(xlabel)
        self.axes.set_ylabel(ylabel)
        if xscale is not None:
            self.axes.set_xscale(xscale)
        if yscale is not None:
            self.axes.set_yscale(yscale)
        if xlim is not None:
            self.axes.set_xlim(*xlim)
        if ylim is not None:
            self.axes.set_ylim(*ylim)
        self.axes.hold(hold)

        Canvas.__init__(self, self.figure)
        self.setParent(parent)

        Canvas.setSizePolicy(self, QSizePolicy.Expanding,
                             QSizePolicy.Expanding)
        Canvas.updateGeometry(self)

    def sizeHint(self):
        w, h = self.get_width_height()
        return QSize(w, h)

    def minimumSizeHint(self):
        return QSize(10, 10)


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    def __init__(self, parent=None, width=5, height=4, dpi=100, ylim=2000):
        fig = Figure(figsize=(width, height), dpi=dpi)
        fig.subplots_adjust(left=0.15)
        self.axes = fig.add_subplot(111)
        self.ylimval = ylim
        # We want the axes cleared every time plot() is called
        self.axes.hold(False)

        self.compute_initial_figure()

        #
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def compute_initial_figure(self):
        pass

class MyStaticMplCanvas(MyMplCanvas):
    """Simple canvas with a sine plot."""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        #self.ylimval = args[4]
    def compute_initial_figure(self):
        t = arange(0.0, 3.0, 0.01)
        s = 4*sin(2*pi*t)
        self.axes.plot(t, s)
        self.axes.set_ylabel("Photon Count")
        self.axes.set_ylim([0,self.ylimval])
        

class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        l = [random.randint(0, 1000) for i in range(4)]

        self.axes.plot([0, 100, 500, 800], l, 'r')
        self.axes.set_ylabel("Total Photon Number")
        self.axes.set_ylim([0,self.ylimval])
        self.draw()

class MainWindow(QMainWindow, qt_ui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent=parent)
        self.ui = qt_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        
        #self.menu_quit.addAction('&Quit', self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        
        # set time
        self.ui.m_time.setReadOnly(True)
        self.ui.gate_time.textChanged.connect(self.calc_time)
        self.ui.read_data.textChanged.connect(self.calc_time)

        # insert logo
        pixmap = QtGui.QPixmap("./logo.png")
        self.ui.logo.setPixmap(pixmap)
        self.ui.logo.setScaledContents(True)
            
        # set fig
        val_sumCh1 = int(self.ui.sumCh1_y.text())
        dc1 = MyDynamicMplCanvas(self, width=5, height=4, dpi=100, ylim=val_sumCh1)
        self.ui.sumCh1.addWidget(dc1)
        self.ui.sumCh1_y.textChanged.connect(self.plot_sumCount_Ch1)
        
        val_pCh1 = int(self.ui.pCh1_y.text())
        sc1 = MyStaticMplCanvas(self, width=5, height=4, dpi=100, ylim=val_pCh1)
        self.ui.countCh1.addWidget(sc1)
        self.ui.pCh1_y.textChanged.connect(self.plot_photonCount_Ch1)

        val_sumCh2 = int(self.ui.sumCh2_y.text())
        dc2 = MyDynamicMplCanvas(self, width=5, height=4, dpi=100, ylim=val_sumCh2)
        self.ui.sumCh2.addWidget(dc2)
        self.ui.sumCh2_y.textChanged.connect(self.plot_sumCount_Ch2)
        
        val_pCh2 = int(self.ui.pCh2_y.text())
        sc2 = MyStaticMplCanvas(self, width=5, height=4, dpi=100, ylim=val_pCh2)
        self.ui.countCh2.addWidget(sc2)
        self.ui.pCh2_y.textChanged.connect(self.plot_photonCount_Ch2)
        
    def calc_time(self):
       g = int(self.ui.gate_time.text()) * 50
       r = int(self.ui.read_data.text())
       self.ui.m_time.setText(str((r * g)/pow(10,9)))
    
    def doSomething(self):
        print( "I'm doing something")
       
    def plot_photonCount_Ch1(self):
        val_pcCh = int(self.ui.pCh1_y.text())
        sc = MyStaticMplCanvas(self, width=5, height=4, dpi=100, ylim=val_pcCh)
        self.ui.countCh1.addWidget(sc)
        
    def plot_photonCount_Ch2(self):
        val_pcCh = int(self.ui.pCh2_y.text())
        sc = MyStaticMplCanvas(self, width=5, height=4, dpi=100, ylim=val_pcCh)
        self.ui.countCh2.addWidget(sc)
    
    def plot_sumCount_Ch1(self):
        val_sumCh1 = int(self.ui.sumCh1_y.text())
        dc = MyDynamicMplCanvas(self, width=5, height=4, dpi=100, ylim=val_sumCh1)
        self.ui.sumCh1.addWidget(dc)
        
    def plot_sumCount_Ch2(self):
        val_sumCh = int(self.ui.sumCh2_y.text())
        dc = MyDynamicMplCanvas(self, width=5, height=4, dpi=100, ylim=val_sumCh)
        self.ui.sumCh2.addWidget(dc)
    
    def fileQuit(self):
        self.close()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())