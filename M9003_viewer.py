# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 16:18:12 2018

@author: Gembu MARYU
"""
import sys
from PyQt5.QtWidgets import (QGraphicsScene, QApplication, QMainWindow, QGridLayout, QVBoxLayout,
                             QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QSizePolicy, QGraphicsPixmapItem)
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

from ui import qt_ui
from math import pow

import random
import numpy as np
import pyqtgraph as pg

import ctypes

"""Load M9003 API from dll
dll = ctypes.windll.LoadLibrary('./M9003api.dll')
hM9003 = dll.M9003Open()
dll.M9003Reset(hM9003)
"""


# Ensure using PyQt5 backend
# matplotlib.use('QT5Agg')

# Matplotlib widget

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
        pixmap = QtGui.QPixmap("./bitmap.png")
        self.ui.logo.setPixmap(pixmap)
        self.ui.logo.setScaledContents(True)

        # set fig

        photon_hist_ch1 = []
        photon_hist_ch2 = []
        ## measure photon before button cle
        photon_ch1, photon_hist_ch1 = self.measurePhoton(photon_hist_ch1)
        photon_ch2, photon_hist_ch2 = self.measurePhoton(photon_hist_ch2)

        # Graph01 : photon count of Ch1
        self.graph01 = pg.PlotWidget(self.ui.centralwidget)
        self.graph01.setObjectName("graph01")
        self.ui.countCh1.addWidget(self.graph01)
        self.graph01.setLabel('left', "Photon Count", units='photon')
        self.graph01.setLabel('bottom', "Time", )
        self.graph01.setLabel('top', "Temporal Photon Count (Ch01)")
        self.graph01.setLabel('left', "Photon Count", units='photon')
        #self.plotCount_Ch1(photon_ch1) # Is this needed for t=0

        # Graph02 : photon sum history of Ch1
        self.graph02 = pg.PlotWidget(self.ui.centralwidget)
        self.graph02.setObjectName("graph02")
        self.ui.sumCh1.addWidget(self.graph02)
        self.graph02.setLabel('left', "Photon Count", units='photon')
        self.graph02.setLabel('bottom', "Time", )
        self.graph02.setLabel('top', "Temporal Photon Count (Ch01)")
        #self.plotHist_Ch1(photon_hist_ch1)

        # Graph03 : photon count of Ch2
        self.graph03 = pg.PlotWidget(self.ui.centralwidget)
        self.graph03.setObjectName("graph03")
        self.ui.countCh2.addWidget(self.graph03)
        self.graph03.setLabel('left', "Photon Count", units='photon')
        self.graph03.setLabel('bottom', "Time",)
        self.graph03.setLabel('top', "Temporal Photon Count (Ch02)")
        self.graph03.setLabel('left', "Photon Count", units='photon')
        #self.plotCount_Ch2(photon_ch2)

        # Graph02 : photon sum history of Ch2
        self.graph04 = pg.PlotWidget(self.ui.centralwidget)
        self.graph04.setObjectName("graph04")
        self.ui.sumCh2.addWidget(self.graph04)
        self.graph04.setLabel('left', "Photon Count", units='photon')
        self.graph04.setLabel('bottom', "Time", )
        self.graph04.setLabel('top', "Temporal Photon Count (Ch02)")
        #self.plotHist_Ch2(photon_hist_ch2)

        self.ui.btn_measure.clicked.connect(lambda: self.measurebtnClicked(photon_hist_ch1, photon_hist_ch2))

        #self.ui.loop_start.clicked.connect(self.plot())
        #self.verticalLayout.addWidget(self.graph01)

    def measurePhoton(self, photon_hist):
        """run M9003api_ReadData
            assign temporal random value """
        photon = np.random.randint(0, 30, 100)
        photon_sum = sum(photon)
        photon_hist.append(photon_sum)
        return photon, photon_hist


    def plotCount_Ch1(self, photon):
        self.graph01.plot(photon)

    def plotCount_Ch2(self, photon):
        self.graph03.plot(photon)

    def plotHist_Ch1(self, photon_hist):
        if len(photon_hist) > 10:
            photon_hist.pop(0)
        self.graph02.plot(photon_hist)

    def plotHist_Ch2(self, photon_hist):
        if len(photon_hist) > 10:
            photon_hist.pop(0)
        self.graph04.plot(photon_hist)

    def calc_time(self):
        g = int(self.ui.gate_time.text()) * 50
        r = int(self.ui.read_data.text())
        self.ui.m_time.setText(str((r * g) / pow(10, 9)))

    def doSomething(self):
        print("I'm doing something")


    def fileQuit(self):
        self.close()

    def measurebtnClicked(self, photon_hist_ch1, photon_hist_ch2):
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' was pressed')

        photon_ch1, photon_hist_ch1 = self.measurePhoton(photon_hist_ch1)
        photon_ch2, photon_hist_ch2 = self.measurePhoton(photon_hist_ch2)

        self.graph01.clear()
        self.plotCount_Ch1(photon_ch1)
        self.graph02.clear()
        self.plotHist_Ch1(photon_hist_ch1)

        self.graph03.clear()
        self.plotCount_Ch2(photon_ch2)
        self.graph04.clear()
        self.plotHist_Ch2(photon_hist_ch2)


pg.setConfigOption('foreground', 'k')
pg.setConfigOption('background', 'w')

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
