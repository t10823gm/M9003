# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 16:18:12 2018

@author: Gembu MARYU
"""
import sys
from PyQt5.QtWidgets import (QGraphicsScene, QApplication, QMainWindow, QGridLayout, QVBoxLayout,
                             QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QSizePolicy, QGraphicsPixmapItem)
from PyQt5 import QtCore
from PyQt5 import QtGui

from ui import qt_ui
from math import pow

import random
import numpy as np
import pyqtgraph as pg

from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QMessageBox
from PyQt5.QtGui import QIcon

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


import ctypes

"""Load M9003 API from dll
dll = ctypes.windll.LoadLibrary('./M9003api.dll')
hM9003 = dll.M9003Open()
dll.M9003Reset(hM9003)
"""


# Ensure using PyQt5 backend

class MainWindow(QMainWindow, qt_ui.Ui_MainWindow):
    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent=parent)
        self.ui = qt_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.timer = QtCore.QTimer()

        # set time
        self.ui.m_time.setReadOnly(True)
        self.ui.gate_time.textChanged.connect(self.check_blank)
        self.ui.read_data.textChanged.connect(self.check_blank)


        # insert logo
        #pixmap = QtGui.QPixmap("./bitmap.png")
        #self.ui.logo.setPixmap(pixmap)
        self.ui.logo.setScaledContents(True)

        # watch combobox index
        self.ui.channelBox.setCurrentIndex(0)
        self.ui.channelBox.currentIndexChanged.connect(self.on_combobox_changed)

        # set initial tab
        self.ui.tabWidget.setCurrentIndex(0)

        ''' FCS '''
        # Initiation of figure for FCS
        self.init_FCS_PC_Figure()
        self.init_FCS_SUM_Figure()
        self.init_FCS_COLL_Figure()

        ''' FCCS '''
        self.init_FCCS_ch1_PC_Figure()
        self.init_FCCS_ch2_PC_Figure()
        self.init_FCCS_ch1_COLL_Figure()
        self.init_FCCS_ch2_COLL_Figure()

        # set photon_hist list
        photon_hist_ch1 = []
        photon_hist_ch2 = []


        # FCS single measurement
        self.ui.measureBtn.clicked.connect(lambda: self.measurebtnClicked(photon_hist_ch1, photon_hist_ch2))

        # loop measurement
        # self.ui.btn_loopStart.clicked.connect(lambda: self.loop_measurment(photon_hist_ch1, photon_hist_ch2))
        # self.ui.btn_loopStop.clicked.connect(self.loop_stop)

        '''

        
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


    def doSomething(self):
        print("I'm doing something")

    def loop_measurment(self, photon_hist_ch1, photon_hist_ch2):
        self.timer.timeout.connect(lambda: self.measurebtnClicked(photon_hist_ch1, photon_hist_ch2))
        interval = (int(self.ui.gate_time.text()) * 50) * int(self.ui.read_data.text()) / pow(10, 6)
        print(interval)
        self.timer.start(interval + 100)

    def loop_stop(self):
        print('loop stop!')
        self.timer.stop()

    def playScansPressed(self):
        if self.playScansAction.isChecked():
            self.playTimer.start()
        else:
            self.playTimer.stop()

    def fileQuit(self):
        self.close()


    '''

    # テキストボックスに数字が入力されているかを確認
    def check_blank(self):
        gt = self.ui.gate_time.text()
        rd = self.ui.read_data.text()
        if gt.isnumeric() == True and rd.isnumeric() == True:
            print(gt, rd)
            self.calc_time()
        else:
            print('fuck')

    # 測定にかかる時間を計算
    def calc_time(self):
        g = int(self.ui.gate_time.text()) * 50
        r = int(self.ui.read_data.text())
        self.ui.m_time.setText(str((r * g) / pow(10, 9)))

    # チャンネルの情報の変更に伴うタブの切替え
    def on_combobox_changed(self, value):
        if value != 2:
            self.ui.tabWidget.setCurrentIndex(0)
        else:
            self.ui.tabWidget.setCurrentIndex(1)

    # Figureを作成
    pg.setConfigOption('background', None)
    pg.setConfigOption('foreground', 'k')
    def init_FCS_PC_Figure(self):
        self.fig = pg.PlotWidget()
        self.ui.FCS_PC_Layout.addWidget(self.fig)
        self.fig.setLabel('left', "Photon Count", units='photon')
        self.fig.setLabel('bottom', "Time", )
        self.fig.setLabel('top', "Temporal Photon Count")
        self.fig.setLabel('left', "Photon Count", units='photon')

    def init_FCS_SUM_Figure(self):
        self.fig = pg.PlotWidget()
        self.ui.FCS_PS_Layout.addWidget(self.fig)
        self.fig.setLabel('left', "Photon Count", units='photon')
        self.fig.setLabel('bottom', "Time", )
        self.fig.setLabel('top', "Temporal Photon Count")
        self.fig.setLabel('left', "Photon Count", units='photon')

    def init_FCS_COLL_Figure(self):
        self.Figure = plt.figure()
        # FigureをFigureCanvasに追加
        self.FigureCanvas = FigureCanvas(self.Figure)
        # LayoutにFigureCanvasを追加
        self.ui.FCS_CF_Layout.addWidget(self.FigureCanvas)
        self.axis = self.Figure.add_subplot(111, position=[0.05, 0.05, 0.05, 0.05])
        plt.xlabel('Time lag')
        plt.ylabel('Coll function')
        plt.tight_layout()

    def init_FCCS_ch1_PC_Figure(self):
        self.fig = pg.PlotWidget()
        self.ui.FCCS_Ch1_photonCount.addWidget(self.fig)
        self.fig.setLabel('left', "Photon Count", units='photon')
        self.fig.setLabel('bottom', "Time", )
        self.fig.setLabel('top', "Temporal Photon Count")
        self.fig.setLabel('left', "Photon Count", units='photon')

    def init_FCCS_ch2_PC_Figure(self):
        self.fig = pg.PlotWidget()
        self.ui.FCCS_Ch2_photonCount.addWidget(self.fig)
        self.fig.setLabel('left', "Photon Count", units='photon')
        self.fig.setLabel('bottom', "Time", )
        self.fig.setLabel('top', "Temporal Photon Count")
        self.fig.setLabel('left', "Photon Count", units='photon')

    def init_FCCS_ch1_COLL_Figure(self):
        self.Figure = plt.figure()
        # FigureをFigureCanvasに追加
        self.FigureCanvas = FigureCanvas(self.Figure)
        # LayoutにFigureCanvasを追加
        self.ui.FCCS_Ch1_colFunc.addWidget(self.FigureCanvas)
        self.axis = self.Figure.add_subplot(111, position=[0.05, 0.05, 0.05, 0.05])
        plt.xlabel('Time lag')
        plt.ylabel('Coll function')
        plt.tight_layout()

    def init_FCCS_ch2_COLL_Figure(self):
        self.Figure = plt.figure()
        # FigureをFigureCanvasに追加
        self.FigureCanvas = FigureCanvas(self.Figure)
        # LayoutにFigureCanvasを追加
        self.ui.FCCS_Ch2_colFunc.addWidget(self.FigureCanvas)
        self.axis = self.Figure.add_subplot(1,1,1, position=[0.05, 0.05, 0.05, 0.05])
        self.axis.set_xlabel('Time lag')
        self.axis.set_ylabel('Time lag')
        plt.tight_layout()

    def measurePhoton(self, photon_hist):
        """run M9003api_ReadData
                        assign temporal random value """
        photon = np.random.randint(0, 30, 100)
        photon_sum = sum(photon)
        photon_hist.append(photon_sum)
        return photon, photon_hist

    def measurebtnClicked(self, photon_hist_ch1, photon_hist_ch2):
        '''
        print(type(photon_hist_ch1))
        sender = self.sender()
        self.statusBar().showMessage(sender.text() + ' was pressed')

        photon_ch1, photon_hist_ch1 = self.measurePhoton(photon_hist_ch1)
        photon_ch2, photon_hist_ch2 = self.measurePhoton(photon_hist_ch2)

        self.ui.FCCS_Ch1_photonCount.clear()
        self.plotCount_Ch1(photon_ch1)
        self.graph02.clear()
        self.plotHist_Ch1(photon_hist_ch1)

        self.graph03.clear()
        self.plotCount_Ch2(photon_ch2)
        self.graph04.clear()
        self.plotHist_Ch2(photon_hist_ch2)
        '''



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
