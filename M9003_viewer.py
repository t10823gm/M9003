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
        self.ui.measureBtn.clicked.connect(lambda: self.calcCorrFunc())

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
        if value != 2:
            self.ui.tabWidget.setCurrentIndex(0)
        else:
            self.ui.tabWidget.setCurrentIndex(1)

    # Figureを作成
    pg.setConfigOption('background', None)
    pg.setConfigOption('foreground', 'k')

    def init_FCS_PC_Figure(self):
        self.FCS_PC_fig = pg.PlotWidget()
        self.ui.FCS_PC_Layout.addWidget(self.FCS_PC_fig)
        self.FCS_PC_fig.setLabel('left', "Photon Count", units='photon')
        self.FCS_PC_fig.setLabel('bottom', "Time", )
        self.FCS_PC_fig.setLabel('top', "Temporal Photon Count")
        self.FCS_PC_fig.setLabel('left', "Photon Count", units='photon')

    def init_FCS_SUM_Figure(self):
        self.FCS_PS_fig = pg.PlotWidget()
        self.ui.FCS_PS_Layout.addWidget(self.FCS_PS_fig)
        self.FCS_PS_fig.setLabel('left', "Total Photon Count", units='photon')
        self.FCS_PS_fig.setLabel('bottom', "Time", )
        self.FCS_PS_fig.setLabel('top', "Total Photon Count")
        self.FCS_PS_fig.setLabel('left', "Photon Count", units='photon')

    def init_FCS_CORR_Figure(self):
        self.FCS_CORR_fig = plt.figure()
        # FigureをFigureCanvasに追加
        self.FCS_CORR_FigureCanvas = FigureCanvas(self.FCS_CORR_fig)
        # LayoutにFigureCanvasを追加
        self.ui.FCS_CF_Layout.addWidget(self.FCS_CORR_FigureCanvas)
        self.axis_FCS_CORR = self.FCS_CORR_fig.add_subplot(111, position=[0.05, 0.05, 0.05, 0.05])
        self.FCS_CORR_fig.patch.set_facecolor('white')
        self.FCS_CORR_fig.patch.set_alpha(0.0)
        self.axis_FCS_CORR.patch.set_facecolor('white')
        self.axis_FCS_CORR.patch.set_alpha(0.0)
        plt.xlabel('Time lag')
        plt.ylabel('Corr function')
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

    def init_FCCS_ch1_CORR_Figure(self):
        self.Figure = plt.figure()
        # FigureをFigureCanvasに追加
        self.FigureCanvas = FigureCanvas(self.Figure)
        # LayoutにFigureCanvasを追加
        self.ui.FCCS_Ch1_colFunc.addWidget(self.FigureCanvas)
        self.axis = self.Figure.add_subplot(111, position=[0.05, 0.05, 0.05, 0.05])
        self.Figure.patch.set_facecolor('white')
        self.Figure.patch.set_alpha(0.0)
        self.axis.patch.set_facecolor('white')
        self.axis.patch.set_alpha(0.0)
        plt.xlabel('Time lag')
        plt.ylabel('Corr function')
        plt.tight_layout()

    def init_FCCS_ch2_CORR_Figure(self):
        self.Figure = plt.figure()
        # FigureをFigureCanvasに追加
        self.FigureCanvas = FigureCanvas(self.Figure)
        # LayoutにFigureCanvasを追加
        self.ui.FCCS_Ch2_colFunc.addWidget(self.FigureCanvas)
        self.axis = self.Figure.add_subplot(1,1,1, position=[0.05, 0.05, 0.05, 0.05])
        self.Figure.patch.set_facecolor('white')
        self.Figure.patch.set_alpha(0.0)
        self.axis.patch.set_facecolor('white')
        self.axis.patch.set_alpha(0.0)
        self.axis.set_xlabel('Time lag')
        self.axis.set_ylabel('Time lag')
        plt.tight_layout()

    def measurePhoton(self, photon_hist):
        """run M9003api_ReadData
                        assign temporal random value """
        self.photon = np.random.randint(0, 30, 100)
        photon_sum = sum(self.photon)
        photon_hist.append(photon_sum)
        self.ui.calc_total_photon.setText(str(photon_sum))
        return photon_hist

    def calcCorrFunc(self):
        A = 1  # 振幅
        fs = np.random.randint(100)  # サンプリング周波数
        f0 = 4  # 基本周波数(今回はラ)
        sec = 10  # 秒
        point = np.arange(0, fs * sec)
        sin_wave = A * np.sin(2 * np.pi * f0 * point / fs)
        sin_wave = [int(x * 32767.0) for x in sin_wave]
        self.axis_FCS_CORR.clear()
        self.axis_FCS_CORR.plot(sin_wave)
        self.FCS_CORR_FigureCanvas.draw()

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
        self.FCS_PC_fig.plot(photon)
        self.FCS_PC_fig.show()

    def plotFCShist(self, photon_hist):
        self.FCS_PS_fig.clear()
        if len(photon_hist) > 10:
            photon_hist.pop(0)
        self.FCS_PS_fig.plot(photon_hist)
        self.FCS_PS_fig.show()

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
        name = QFileDialog.getSaveFileName(self, 'Save as EPS File')
        self.FCS_CORR_fig.savefig(name[0])


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
