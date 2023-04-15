# -*- coding: utf-8 -*-
"""
Created on Thu May 26 09:49:21 2022

TITLE: Hola

@author: Alejandro Condori
E-mail: alejandrocondori2@gmail.com
Cel-WhatsApp: +54 9 294 412 5003
"""

import os
import sys
import copy
import pathlib
import pydicom
import qdarkstyle
# import GDCM
import pylibjpeg
import numpy as np
import pyqtgraph as pg
# from wids import PacWidget, StdWidget
from pyqtgraph.Qt import QtWidgets, QtGui, QtCore, uic
from pyqtgraph.dockarea import Dock, DockArea

# %%
pydicom.config.datetime_conversion = True
ui_pac, ui_pac_parent = uic.loadUiType("pacWid.ui")


class PacWidget(ui_pac_parent, ui_pac):

    def __init__(self):
        ui_pac_parent.__init__(self)
        ui_pac.__init__(self)
        self.setupUi(self)


class DockArea2(DockArea):

    def makeContainer(self, typ):
        # new = super(DockArea, self).makeContainer(typ)
        new = super().makeContainer(typ)
        new.setChildrenCollapsible(False)
        return new


class Dock2(Dock):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nStyle = """
        Dock > QWidget {
            border: 1px solid #000;
            border-radius: 0px;
        }"""
        self.hideTitleBar()
        self.updateStyle()


class IodoQuant(QtWidgets.QMainWindow):

    def __init__(self, config):
        QtWidgets.QMainWindow.__init__(self)
        self.setStyleSheet(
            '''
            QTabWidget::tab-bar {alignment: center;}
            QWidget { font-size: 10pt;}
            '''
        )
        self.config = config
        wid = QtWidgets.QWidget()
        lay1 = QtWidgets.QVBoxLayout()
        self.setCentralWidget(wid)
        wid.setLayout(lay1)
        lay2 = QtWidgets.QVBoxLayout(self)
        lay3 = QtWidgets.QHBoxLayout(self)
        lay4 = QtWidgets.QHBoxLayout(self)
        dock1 = Dock2(self, 'Archivos', size=(300, 450))
        dock2 = Dock2(self, 'Visualizador', size=(700, 400))
        dock3 = Dock2(self, 'TabWidget', size=(250, 400))
        dock4 = Dock2(self, 'Vis', size=(300, 350))
        area = DockArea2(self)
        self.btn = QtWidgets.QPushButton('   Seleccione Carpeta   ', self)
        self.addBtn = QtWidgets.QPushButton(self)
        self.addBtn.setIcon(QtGui.QIcon('icons/add.png'))
        self.addBtn.setIconSize(QtCore.QSize(30, 30))
        self.lockBtn = QtWidgets.QPushButton(self)
        self.op = QtGui.QIcon('icons/open1.png')
        self.cl = QtGui.QIcon('icons/lock.png')
        self.lockBtn.setIcon(self.op)
        self.lockBtn.setIconSize(QtCore.QSize(20, 20))
        self.lockBtn.setCheckable(True)
        spc1 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum
        )
        spc2 = QtWidgets.QSpacerItem(
            40, 20, QtWidgets.QSizePolicy.Expanding,
            QtWidgets.QSizePolicy.Minimum
        )
        self.list = QtWidgets.QListWidget()
        self.pac_tab = PacWidget()
        self.pac_tab.setEnabled(False)
        self.pac_tab.roiLay2.addWidget(self.lockBtn)
        self.win = pg.GraphicsLayoutWidget()
        self.plt = self.win.addPlot(title="")  # pg.PlotWidget()
        self.plt_prev = pg.PlotWidget()
        self.img = pg.ImageItem()
        self.img_prev = pg.ImageItem()
        self.img.setTransform(QtGui.QTransform().rotate(270))
        self.img_prev.setTransform(QtGui.QTransform().rotate(270))
        self.label = QtWidgets.QLabel('')
        self.label.setMaximumHeight(15)
        lay1.addWidget(area)
        area.addDock(dock1, 'left')
        area.addDock(dock2, 'right', dock1)
        area.addDock(dock3, 'right', dock2)
        area.addDock(dock4, 'bottom', dock1)
        dock1.layout.addLayout(lay2, 0, 0)
        dock4.layout.addLayout(lay4, 0, 0)
        lay2.addLayout(lay3)
        lay2.addWidget(self.list)
        lay4.addWidget(self.plt_prev)
        lay4.addWidget(self.addBtn)
        lay3.addItem(spc1)
        lay3.addWidget(self.btn)
        lay3.addItem(spc2)
        dock2.addWidget(self.win)
        dock3.addWidget(self.pac_tab)
        self.plt.setAspectLocked(True)
        self.plt_prev.setAspectLocked(True)
        # self.plt.showAxis('bottom', False)
        self.plt_prev.showAxis('bottom', False)
        # self.plt.showAxis('left', False)
        self.plt_prev.showAxis('left', False)
        self.plt.addItem(self.img)
        self.plt_prev.addItem(self.img_prev)
        self.hist = pg.HistogramLUTItem()
        self.roi = pg.CircleROI([80, 80], [20, 20], pen=(4, 9))
        self.plt.addItem(self.roi)
        self.plt.removeItem(self.roi)
        self.bound = QtCore.QRectF(0, 0, 20, 20)
        # self.bound.rotate(270)
        self.roi.maxBounds = self.bound
        self.hist.setImageItem(self.img)
        self.win.addItem(self.hist)
        self.hist.vb.setMouseEnabled(y=False)
        self.path = self.config["data_path"]
        self.files = []
        self.prevData = None
        self.currentData = None
        self.state = False  # active
        self.pacSt = [True, False, False]  # std, bkg, pac
        
        # Conección de señales
        self.btn.clicked.connect(self.btn_clicked)
        self.list.currentRowChanged.connect(self.itemChanged)
        self.roi.sigRegionChanged.connect(self.updData)
        self.pac_tab.vol.valueChanged.connect(self.verif)
        self.addBtn.clicked.connect(self.sendData)
        self.lockBtn.clicked.connect(self.lockRoi)
        self.pac_tab.setStd.clicked.connect(self.setStd)
        self.pac_tab.setBkg.clicked.connect(self.setBkg)
        self.pac_tab.setPac.clicked.connect(self.setPac)
        self.pac_tab.calculate.clicked.connect(self.calculate)
        self.pac_tab.radStd.toggled.connect(self.radPacToggled)
        self.pac_tab.radBkg.toggled.connect(self.radPacToggled)
        self.pac_tab.radPac.toggled.connect(self.radPacToggled)

    def calculate(self):
        S = self.pac_tab.stdTotal.value()
        F = self.pac_tab.bkgTotal.value()
        M = self.pac_tab.pacTotal.value()
        V = self.pac_tab.vol.value()
        capt = 100 * (M - F) / (S - F) / V
        print(capt)
        self.pac_tab.capt.setValue(capt)

    def setStd(self):
        self.pac_tab.stdTotal.setValue(self.pac_tab.stdCounts.value())
        self.verif()

    def setBkg(self):
        self.pac_tab.bkgTotal.setValue(self.pac_tab.bkgCounts.value())
        self.verif()

    def setPac(self):
        self.pac_tab.pacTotal.setValue(self.pac_tab.pacCounts.value())
        self.verif()

    def verif(self):
        a = self.pac_tab.stdTotal.value() != 0
        b = self.pac_tab.bkgTotal.value() != 0
        c = self.pac_tab.pacTotal.value() != 0
        d = self.pac_tab.vol.value() != 0
        e = (self.pac_tab.stdCounts.value() - self.pac_tab.bkgCounts.value()) \
            != 0
        if a and b and c:
            self.pac_tab.calcGroup.setEnabled(True)
            if d and e:
                self.pac_tab.calculate.setEnabled(True)
        else:
            self.pac_tab.calcGroup.setEnabled(False)
            self.pac_tab.calculate.setEnabled(False)

    def lockRoi(self, check):
        if check:
            self.lockBtn.setIcon(self.cl)
            self.handle = copy.copy(self.roi.handles[0])
            self.roi.removeHandle(0)
        else:
            self.lockBtn.setIcon(self.op)
            # self.roi.addHandle(self.handle)
            self.roi.addScaleHandle(self.handle['pos'], self.handle['pos'])

    def updData(self):
        pxdata = self.files[self.currentData].pixel_array
        roi = self.roi
        slc = roi.getArraySlice(pxdata, self.img, returnSlice=False)[0]
        xmin = slc[0][0]
        xmax = slc[0][1]
        ymin = slc[1][0]
        ymax = slc[1][1]
        xwi = xmax-xmin
        ywi = ymax-ymin
        if xwi >= ywi:
            wi = xwi
            ymax = ymin + wi
            ywi = ymax-ymin
        else:
            wi = ywi
            xmax = xmin + wi
            xwi = xmax-xmin
        r = (wi-1)/2
        A = np.arange(-r, r+1)**2
        dists = np.sqrt(A[:, None] + A)
        circ = (dists - r < 0.3).astype(int)
        mask = np.zeros((len(pxdata), len(pxdata)))
        mask[xmin:xmax, ymin:ymax] = circ
        res = (pxdata*mask)[xmin:xmax, ymin:ymax]
        cts = int(res.sum())
        data = self.files[self.currentData]
        ps = float(data.PixelSpacing[0])
        area = np.pi * (wi * ps / 20)**2
        rate = cts/area
        std = self.pac_tab.radStd.isChecked()
        bkg = self.pac_tab.radBkg.isChecked()
        pac = self.pac_tab.radPac.isChecked()
        self.pac_tab.roiArea.setValue(area)
        date = QtCore.QDateTime.fromString(
            data.AcquisitionDate.__str__(),
            "yyyyMMdd"
        )
        if std:
            self.pac_tab.stdCounts.setValue(cts)
            self.pac_tab.stdRate.setValue(rate)
            self.pac_tab.stdDate.setDateTime(date)
        elif bkg:
            self.pac_tab.bkgCounts.setValue(cts)
            self.pac_tab.bkgRate.setValue(rate)
            self.pac_tab.bkgDate.setDateTime(date)
        elif pac:
            self.pac_tab.pacCounts.setValue(cts)
            self.pac_tab.pacRate.setValue(rate)
            self.pac_tab.pacDate.setDateTime(date)

    def sendData(self):
        ind = self.prevData
        self.currentData = ind
        ds = self.files[ind]
        pxdata = ds.pixel_array
        le = len(pxdata)
        self.img.setImage(pxdata)
        self.plt.autoBtnClicked()
        if not self.state:
            self.pac_tab.setEnabled(True)
            self.plt.addItem(self.roi)
            self.state = True
        ps = float(ds.PixelSpacing[0])
        px = round(110 / ps - 0.5)
        # self.roi.setSize([px, px])
        self.roi.setPos([(le-px)/2, -(le+px)/2])
        self.bound.setRect(0, -le+1, le-1, le)
        self.verif()

    def radPacToggled(self):
        std = self.pac_tab.radStd.isChecked()
        bkg = self.pac_tab.radBkg.isChecked()
        pac = self.pac_tab.radPac.isChecked()
        if self.pacSt[0] != std:
            print('aqui 1')
            if std:
                self.pac_tab.stdGroup.setEnabled(True)
                self.pacSt[0] = True
            else:
                self.pac_tab.stdGroup.setEnabled(std)
                self.pacSt[0] = std
        elif self.pacSt[1] != bkg:
            print('aqui 2')
            if bkg:
                self.pac_tab.bkgGroup.setEnabled(True)
                self.pacSt[1] = True
            else:
                self.pac_tab.bkgGroup.setEnabled(bkg)
                self.pacSt[1] = bkg
        elif self.pacSt[2] != pac:
            print('aqui 3')
            if pac:
                self.pac_tab.pacGroup.setEnabled(True)
                self.pacSt[2] = True
            else:
                self.pac_tab.pacGroup.setEnabled(pac)
                self.pacSt[2] = pac
        self.updData()

    def itemChanged(self, ind):
        ds = self.files[ind]
        pxdata = ds.pixel_array
        self.prevData = ind
        self.img_prev.setImage(pxdata)
        self.plt_prev.autoBtnClicked()

    def btn_clicked(self):
        old = self.path
        self.path = QtWidgets.QFileDialog.getExistingDirectory(
            self, 'Elegir Carpeta', self.path
        )
        if self.path:
            self.list.clear()
            self.files.clear()
            self.files = self.find_files(self.path)
            if self.files:
                for file in self.files:
                    name = file.PatientName.components[0][:3] + \
                        ' ' + file.SeriesDescription + ' ' + file.PatientID
                    self.list.addItem(QtWidgets.QListWidgetItem(name))
                self.list.setCurrentRow(0)
                return True
        else:
            self.path = old

    def find_files(self, search_path):
        result = []
        # Wlaking top-down from the root
        for root, folders, files in os.walk(search_path):
            for i in files:
                if pathlib.Path(i).suffix in ['.dcm', '.DCM']:
                    filename = os.path.join(root, i)
                    result.append(pydicom.dcmread(filename))
        return result

# %% Checked


def find_files(search_path):
    result = []
    # Wlaking top-down from the root
    for root, folders, files in os.walk(search_path):
        for i in files:
            if pathlib.Path(i).suffix in ['.dcm', '.DCM']:
                filename = os.path.join(root, i)
                result.append(pydicom.dcmread(filename))
    return result


# %%
if __name__ == "__main__":
    path = 'D:/Docs/GitHub/IODO'
    a = find_files(path)
    print('Hola QT')
    dark_theme = True
    app = QtWidgets.QApplication(sys.argv)
    import yaml
    with open("config/config.yml", 'rt', encoding='utf8') as file:
        config = yaml.safe_load(file)
        print(config["data_path"])
    window = IodoQuant(config)
    if dark_theme:
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    else:
        app.setStyleSheet('')
    window.show()
    sys.exit(app.exec_())
