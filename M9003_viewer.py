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

        # self.menu_quit.addAction('&Quit', self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)

        # set time
        self.ui.m_time.setReadOnly(True)
        self.ui.gate_time.textChanged.connect(self.calc_time)
        self.ui.read_data.textChanged.connect(self.calc_time)

        # insert logo
        pixmap = QtGui.QPixmap("./bitmap.png")
        self.ui.logo.setPixmap(pixmap)
        self.ui.logo.setScaledContents(True)

        # set fig
        self.graph01 = pg.PlotWidget(self.ui.centralwidget)
        self.graph01.setObjectName("graph01")
        self.ui.countCh1.addWidget(self.graph01)
        self.plot()

        self.graph02 = pg.PlotWidget(self.ui.centralwidget)
        self.graph02.setObjectName("graph02")
        self.ui.sumCh1.addWidget(self.graph02)
        self.plot2()

        self.graph03 = pg.PlotWidget(self.ui.centralwidget)
        self.graph03.setObjectName("graph03")
        self.ui.countCh2.addWidget(self.graph03)
        self.plot3()

        self.graph04 = pg.PlotWidget(self.ui.centralwidget)
        self.graph04.setObjectName("graph04")
        self.ui.sumCh2.addWidget(self.graph04)
        self.plot4()

        #self.ui.loop_start.clicked.connect(self.plot())
        #self.verticalLayout.addWidget(self.graph01)

    def plot(self):
        photon = np.random.randint(0, 30, 100)
        self.graph01.plot(photon)
        self.graph01.setLabel('left', "Photon Count", units='photon')
        self.graph01.setLabel('bottom', "Time",)
        self.graph01.setLabel('top', "Temporal Photon Count (Ch01)")
        #self.graph01.setLable('left', "Photon Count", units='photon')


    def plot2(self):
        x = np.random.normal(size=1000) * 1e-5
        y = x * 1000 + 0.005 * np.random.normal(size=1000)
        y -= y.min() - 1.0
        mask = x > 1e-15
        x = x[mask]
        y = y[mask]
        self.graph02.plot(x, y, pen=None, symbol='t', symbolPen=None, symbolSize=10, symbolBrush=(100, 100, 255, 50))
        self.graph02.setLabel('left', "Y Axis", units='A')
        self.graph02.setLabel('bottom', "Y Axis", units='s')
        self.graph02.setLabel('top', "Summation of Photon Count (Ch01)")
        self.graph02.setLogMode(x=True, y=False)

    def plot3(self):
        photon = np.random.randint(0, 30, 100)
        self.graph03.plot(photon)
        self.graph03.setLabel('left', "Photon Count (Ch02)", units='photon')
        self.graph03.setLabel('bottom', "Time",)
        self.graph03.setLabel('top', "Temporal Photon Count")

    def plot4(self):
        x = np.random.normal(size=1000) * 1e-5
        y = x * 1000 + 0.005 * np.random.normal(size=1000)
        y -= y.min() - 1.0
        mask = x > 1e-15
        x = x[mask]
        y = y[mask]
        self.graph04.plot(x, y, pen=None, symbol='t', symbolPen=None, symbolSize=10, symbolBrush=(100, 100, 255, 50))
        self.graph04.setLabel('left', "Y Axis", units='A')
        self.graph04.setLabel('bottom', "Y Axis", units='s')
        self.graph04.setLabel('top', "Summation of Photon Count (Ch02)")
        self.graph04.setLogMode(x=True, y=False)


    def calc_time(self):
        g = int(self.ui.gate_time.text()) * 50
        r = int(self.ui.read_data.text())
        self.ui.m_time.setText(str((r * g) / pow(10, 9)))

    def doSomething(self):
        print("I'm doing something")


    def fileQuit(self):
        self.close()

pg.setConfigOption('foreground', 'k')
pg.setConfigOption('background', 'w')

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
