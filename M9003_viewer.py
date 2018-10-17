# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 16:18:12 2018

@author: Gembu MARYU
"""
import sys
from PyQt5.QtWidgets import (QGraphicsScene, QApplication, QMainWindow, QGridLayout, QVBoxLayout, QFileDialog,
                             QHBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QSizePolicy, QGraphicsPixmapItem)
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenu, QMessageBox

from math import pow

import numpy as np
import pyqtgraph as pg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from ui import qt_ui
from FCS import calCorr

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
        self.setObjectName("Photon Counter M9003")
        self.setWindowTitle("Photon Counter M9003")
        self.setObjectName("Photon Counter M9003")
        self.ui = qt_ui.Ui_MainWindow()
        self.ui.setupUi(self)
        self.timer = QtCore.QTimer()

        # set measurement time value
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

        # watch tab index
        self.ui.tabWidget.currentChanged.connect(self.on_tab_changed)

        # set initial tab
        self.ui.tabWidget.setCurrentIndex(0)

        # initiate figures
        ''' FCS '''
        self.init_FCS_PC_Figure()
        self.init_FCS_SUM_Figure()
        self.init_FCS_CORR_Figure()

        ''' FCCS '''
        self.init_FCCS_ch1_PC_Figure()
        self.init_FCCS_ch2_PC_Figure()
        self.init_FCCS_ch1_CORR_Figure()
        self.init_FCCS_ch2_CORR_Figure()

        # set photon_hist list
        photon_hist = []

        # single measurement
        self.ui.measureBtn.clicked.connect(lambda: self.measurebtnClicked(photon_hist))
        self.ui.measureBtn.clicked.connect(lambda: self.calcCorrFunc(self.photon))

        # loop measurement
        self.ui.btn_loopStart.clicked.connect(lambda: self.loop_measurment(photon_hist))
        self.ui.btn_loopStop.clicked.connect(self.loop_stop)

        # save photon count data as csv file
        self.ui.saveDataBtn.clicked.connect(lambda: self.saveasCSV(self.photon))
        self.ui.saveFigBtn.clicked.connect(lambda: self.saveasEPS())


    # テキストボックスに数字が入力されているかを確認
    def check_blank(self):
        gt = self.ui.gate_time.text()
        rd = self.ui.read_data.text()
        if gt.isnumeric() == True and rd.isnumeric() == True:
            print(gt, rd)
            self.calc_time()
        else:
            print('error')

    # 測定にかかる時間を計算
    def calc_time(self):
        g = int(self.ui.gate_time.text()) * 50
        r = int(self.ui.read_data.text())
        self.ui.m_time.setText(str((r * g) / pow(10, 9)))

    # チャンネルの情報の変更に伴うタブの切替え
    def on_combobox_changed(self, value):
        self.loop_stop()
        #self.clearAllFigs()
        if value != 2:
            self.ui.tabWidget.setCurrentIndex(0)
        else:
            self.ui.tabWidget.setCurrentIndex(1)

    def on_tab_changed(self, value):
        self.loop_stop()
        #self.clearAllFigs()
        if value == 0:
            self.ui.channelBox.setCurrentIndex(0)
        else:
            self.ui.channelBox.setCurrentIndex(2)

    # Figureを作成
    pg.setConfigOption('background', None)
    pg.setConfigOption('foreground', 'k')

    def init_FCS_SUM_Figure(self):
        self.FCS_PS_fig = pg.PlotWidget()
        self.ui.FCS_PS_Layout.addWidget(self.FCS_PS_fig)
        self.FCS_PS_fig.setLabel('left', "Total Photon Count", units='photon')
        self.FCS_PS_fig.setLabel('bottom', "Time", )
        self.FCS_PS_fig.setLabel('top', "Total Photon Count")

    def init_FCS_PC_Figure(self):
        self.FCS_PC_fig = pg.PlotWidget()
        self.ui.FCS_PC_Layout.addWidget(self.FCS_PC_fig)
        self.FCS_PC_fig.setLabel('left', "Photon Count", units='photon')
        self.FCS_PC_fig.setLabel('bottom', "Time", )
        self.FCS_PC_fig.setLabel('top', "Temporal Photon Count")

    def init_FCS_CORR_Figure(self):
        self.FCS_CORR_fig = pg.PlotWidget()
        self.ui.FCS_CF_Layout.addWidget(self.FCS_CORR_fig)
        self.FCS_CORR_fig.setLabel('bottom', "Time [frame]", )
        self.FCS_CORR_fig.setLabel('top', "Correlation function")

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

    def init_FCCS_ch1_CORR_Figure(self):
        self.FCCS_CH1_CORR_fig = pg.PlotWidget()
        self.ui.FCCS_Ch1_colFunc.addWidget(self.FCCS_CH1_CORR_fig)
        self.FCCS_CH1_CORR_fig.setLabel('bottom', "Time [frame]", )
        self.FCCS_CH1_CORR_fig.setLabel('top', "Correlation function")

    def init_FCCS_ch2_CORR_Figure(self):
        self.FCCS_CH2_CORR_fig = pg.PlotWidget()
        self.ui.FCCS_Ch2_colFunc.addWidget(self.FCCS_CH2_CORR_fig)
        self.FCCS_CH2_CORR_fig.setLabel('bottom', "Time [frame]", )
        self.FCCS_CH2_CORR_fig.setLabel('top', "Correlation function")

    def measurePhoton(self, photon_hist):
        """run M9003api_ReadData
                        assign temporal random value """
        self.photon = np.random.randint(0, 10, 10000)
        photon_sum = sum(self.photon)
        photon_hist.append(photon_sum)
        self.ui.calc_total_photon.setText(str(photon_sum))
        return photon_hist

    def calcCorrFunc(self, photon):
        A = 1  # 振幅
        fs = np.random.randint(100)  # サンプリング周波数
        f0 = 4  # 基本周波数(今回はラ)
        sec = 10  # 秒
        point = np.arange(0, fs * sec)
        sin_wave = A * np.sin(2 * np.pi * f0 * point / fs)
        sin_wave = [int(x * 32767.0) for x in sin_wave]
        self.FCS_CORR_fig.clear()
        self.FCS_CORR_fig.plot(sin_wave)
        self.FCS_CORR_fig.show()

    def measurebtnClicked(self, photon_hist):
        self.check_measure()
        photon_hist = self.measurePhoton(photon_hist)
        if self.ui.tabWidget.currentIndex() != 1:
            # FCS
            self.plotFCSphotoncount(self.photon)
            self.plotFCShist(photon_hist)
        else:
            print('FCCS')

    def plotFCSphotoncount(self, photon):
        self.FCS_PC_fig.clear()
        self.FCS_PC_fig.plot(photon, pen=None, symbol='o', symbolSize=2)
        self.FCS_PC_fig.setXRange(0, 1000)
        self.FCS_PC_fig.show()

    def plotFCShist(self, photon_hist):
        self.FCS_PS_fig.clear()
        if len(photon_hist) > 10:
            photon_hist.pop(0)
        self.FCS_PS_fig.plot(photon_hist)
        self.FCS_PS_fig.show()

    '''
    def clearAllFigs(self):
        self.FCS_PC_fig.clear()
        self.FCS_PS_fig.clear()
        self.FCS_CORR_fig.clear()
        self.FCCS_CH1_CORR_fig.clear()
        self.FCCS_CH2_CORR_fig.clear()
    '''

    def loop_measurment(self, photon_hist):
        self.timer.timeout.connect(lambda: self.measurebtnClicked(photon_hist))
        interval = (int(self.ui.gate_time.text()) * 50) * int(self.ui.read_data.text()) / pow(10, 6)
        print(interval)
        self.timer.start(interval)

    def loop_stop(self):
        print('loop stop!')
        self.timer.stop()

    def check_measure(self):
        gt = self.ui.gate_time.text()
        rd = self.ui.read_data.text()
        if gt.isnumeric() != True or rd.isnumeric() != True:
            errorPopup()
        else:
            pass

    def saveasCSV(self, photon):
        import csv
        name = QFileDialog.getSaveFileName(self, 'Save as CSV File')
        f = open(name[0], 'w')
        print(f)
        writer = csv.writer(f, lineterminator=',')
        writer.writerow(photon)
        f.close()

    def saveasEPS(self):
        import pyqtgraph.exporters
        name = QFileDialog.getSaveFileName(self, 'Save as EPS File')
        print(name)
        ex = pg.exporters.SVGExporter(self.FCS_CORR_fig.plotItem)
        ex.export('test.svg')

class errorPopup(QWidget):
    def __init__(self) -> object:
        ew = QWidget.__init__(self)
        self.showError()

    def showError(self):
        print("showError is working")
        qmb = QMessageBox(self)
        qmb.setIcon(QMessageBox.Warning)
        qmb.setText("Value must be integer.")
        qmb.setWindowTitle("Measurement Error")
        qmb.exec()

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
