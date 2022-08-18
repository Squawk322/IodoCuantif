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
import pathlib
import pydicom
import qdarkstyle
# import GDCM
import pylibjpeg
import numpy as np
import pyqtgraph as pg
from wids import PacWidget, StdWidget
from pyqtgraph.Qt import QtWidgets, QtGui, QtCore
from pyqtgraph.dockarea import Dock, DockArea

# %%
pydicom.config.datetime_conversion = True


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

    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setStyleSheet(
            '''
            QTabWidget::tab-bar {alignment: center;}
            QWidget { font-size: 10pt;}
            '''
        )

        wid = QtWidgets.QWidget()
        lay1 = QtWidgets.QVBoxLayout()
        self.setCentralWidget(wid)
        wid.setLayout(lay1)
        lay2 = QtGui.QVBoxLayout(self)
        lay3 = QtGui.QHBoxLayout(self)
        lay4 = QtGui.QHBoxLayout(self)
        dock1 = Dock2(self, 'Archivos', size=(300, 450))
        dock2 = Dock2(self, 'Visualizador', size=(700, 400))
        dock3 = Dock2(self, 'TabWidget', size=(250, 400))
        dock4 = Dock2(self, 'Vis', size=(300, 350))
        area = DockArea2(self)
        self.btn = QtGui.QPushButton('   Seleccione Carpeta   ', self)
        self.addBtn = QtWidgets.QPushButton(self)
        self.addBtn.setIcon(QtGui.QIcon('icons/add.png'))
        self.addBtn.setIconSize(QtCore.QSize(30, 30))
        spc1 = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum
        )
        spc2 = QtGui.QSpacerItem(
            40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum
        )
        self.list = QtGui.QListWidget()
        self.tabWidget = QtGui.QTabWidget()
        self.pac_tab = PacWidget()
        self.std_tab = StdWidget()
        self.win = pg.GraphicsLayoutWidget()
        self.plt = self.win.addPlot(title="")  # pg.PlotWidget()
        self.plt_prev = pg.PlotWidget()
        self.img = pg.ImageItem()
        self.img_prev = pg.ImageItem()
        self.img.setTransform(QtGui.QTransform().rotate(270))
        self.img_prev.setTransform(QtGui.QTransform().rotate(270))
        self.tabWidget.addTab(self.pac_tab, 'Captación')
        self.tabWidget.addTab(self.std_tab, 'Estándar')
        self.tabWidget.setEnabled(False)
        self.label = QtGui.QLabel('')
        self.label.setMaximumHeight(15)
        lay1.addWidget(area)
        # lay1.addWidget(self.label)
        area.addDock(dock1, 'left')
        area.addDock(dock2, 'right', dock1)
        area.addDock(dock3, 'right', dock2)
        area.addDock(dock4, 'bottom', dock1)
        dock1.layout.addLayout(lay2, 0, 0)
        dock4.layout.addLayout(lay4, 0, 0)
        lay2.addLayout(lay3)
        lay2.addWidget(self.list)
        # lay2.addLayout(lay4)
        lay4.addWidget(self.plt_prev)
        lay4.addWidget(self.addBtn)
        lay3.addItem(spc1)
        lay3.addWidget(self.btn)
        lay3.addItem(spc2)
        dock2.addWidget(self.win)
        dock3.addWidget(self.tabWidget)
        self.plt.setAspectLocked(True)
        self.plt_prev.setAspectLocked(True)
        # self.plt.showAxis('bottom', False)
        self.plt_prev.showAxis('bottom', False)
        # self.plt.showAxis('left', False)
        self.plt_prev.showAxis('left', False)
        self.plt.addItem(self.img)
        self.plt_prev.addItem(self.img_prev)
        # self.plt_prev.setMaximumHeight(300)
        # self.plt_prev.setMinimumWidth(300)
        # self.iso = pg.IsocurveItem(level=0.8, pen='g')
        # self.iso.setParentItem(self.img)
        # self.iso.setZValue(12)
        self.hist = pg.HistogramLUTItem()
        self.roi = pg.CircleROI([80, 80], [20, 20], pen=(4,9))
        self.plt.addItem(self.roi)
        self.roi.removeHandle(0)
        self.plt.removeItem(self.roi)
        self.bkgRoi = pg.CircleROI([80, 80], [80, 80], pen=(4,9))
        self.bound = QtCore.QRectF(0, 0, 20, 20)
        # self.bound.rotate(270)
        self.roi.maxBounds = self.bound
        self.bkgRoi.maxBounds = self.bound
        
        self.hist.setImageItem(self.img)
        self.win.addItem(self.hist)
        # self.plt.addItem(self.iso)
        # self.isoLine = pg.InfiniteLine(angle=0, movable=True, pen='g')
        # self.hist.vb.addItem(self.isoLine)
        self.hist.vb.setMouseEnabled(y=False)
        # self.isoLine.setValue(0.4)
        # self.isoLine.setZValue(1000) 
        
        self.path = os.path.abspath(os.getcwd())
        self.files = []
        self.prevData = None
        self.currentData = None
        self.state = [False, False] # roi, bkgRoi
        self.pacSt = [True, False]
        self.stdSt = [True, False]
        self.btn.clicked.connect(self.btn_clicked)
        self.list.currentRowChanged.connect(self.itemChanged)
        # self.isoLine.sigDragged.connect(self.updateIsocurve)
        self.addBtn.clicked.connect(self.sendData)
        self.roi.sigRegionChanged.connect(self.updData)
        self.bkgRoi.sigRegionChanged.connect(self.updData)
        self.pac_tab.radBkg.toggled.connect(self.radPacToggled)
        self.pac_tab.radPac.toggled.connect(self.radPacToggled)
        self.std_tab.radBkg.toggled.connect(self.radStdToggled)
        self.std_tab.radStd.toggled.connect(self.radStdToggled)
        self.tabWidget.currentChanged.connect(self.tabChanged)

    def tabChanged(self, ind):
        if ind == 0:
            if self.pac_tab.radBkg.isChecked():
                if self.state[1] == False:
                    self.plt.removeItem(self.roi)
                    self.plt.addItem(self.bkgRoi)
                    self.state[1] = True
                    self.state[0] = False
            else:
                if self.state[0] == False:
                    self.plt.removeItem(self.bkgRoi)
                    self.plt.addItem(self.roi)
                    # ds = self.files[self.currentData]
                    # ps = float(ds.PixelSpacing[0])      
                    # px = round(110 / ps - 0.5)
                    # self.roi.setSize([px, px])
                    self.state[0] = True
                    self.state[1] = False
        else:
            if self.std_tab.radBkg.isChecked():
                if self.state[1] == False:
                    self.plt.removeItem(self.roi)
                    self.plt.addItem(self.bkgRoi)
                    self.state[1] = True
                    self.state[0] = False
            else:
                if self.state[0] == False:
                    self.plt.removeItem(self.bkgRoi)
                    self.plt.addItem(self.roi)
                    # ds = self.files[self.currentData]
                    # ps = float(ds.PixelSpacing[0])      
                    # px = round(110 / ps - 0.5)
                    # self.roi.setSize([px, px])
                    self.state[0] = True
                    self.state[1] = False


    def radPacToggled(self):
        bkg = self.pac_tab.radBkg.isChecked()
        pac = self.pac_tab.radPac.isChecked()
        if self.pacSt[0] != bkg:
            print('aqui 1')
            if bkg:
                self.plt.addItem(self.bkgRoi)
                self.state[1] = True
                self.pac_tab.bkgGroup.setEnabled(True)
                self.pacSt[0] = True
            else:
                self.plt.removeItem(self.bkgRoi)
                self.state[1] = False
                self.pac_tab.bkgGroup.setEnabled(False)
                self.pacSt[0] = False
        elif self.pacSt[1] != pac:
            print('aqui 2')
            if pac:
                self.plt.addItem(self.roi)
                self.state[0] = True
                self.pac_tab.pacGroup.setEnabled(True)
                self.pacSt[1] = True
            else:
                self.plt.removeItem(self.roi)
                self.state[0] = False
                self.pac_tab.pacGroup.setEnabled(False)
                self.pacSt[1] = False

    def radStdToggled(self):
        bkg = self.std_tab.radBkg.isChecked()
        pac = self.std_tab.radStd.isChecked()
        if self.stdSt[0] != bkg:
            if bkg:
                self.plt.addItem(self.bkgRoi)
                self.state[1] = True
                self.std_tab.bkgGroup.setEnabled(True)
                self.stdSt[0] = True
            else:
                self.plt.removeItem(self.bkgRoi)
                self.state[1] = False
                self.std_tab.bkgGroup.setEnabled(False)
                self.stdSt[0] = False
        elif self.stdSt[1] != pac:
            if pac:
                self.plt.addItem(self.roi)
                self.state[0] = True
                self.std_tab.stdGroup.setEnabled(True)
                self.stdSt[1] = True
            else:
                self.plt.removeItem(self.roi)
                self.state[0] = False
                self.std_tab.stdGroup.setEnabled(False)
                self.stdSt[1] = False

    # def updateIsocurve(self):
    #     self.iso.setLevel(self.isoLine.value())

    def updData(self, roi):
        pxdata = self.files[self.currentData].pixel_array
        # roi.getArraySlice(pxdata, self.img)[0]
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
        A = np.arange(-r,r+1)**2
        dists = np.sqrt(A[:,None] + A)
        circ = (dists-r<0.3).astype(int)
        mask = np.zeros((len(pxdata), len(pxdata)))
        mask[xmin:xmax, ymin:ymax] = circ
        res = (pxdata*mask)[xmin:xmax, ymin:ymax]
        cts = int(res.sum())
        ps = float(self.files[self.currentData].PixelSpacing[0])  
        area = np.pi * (wi * ps / 20)**2
        rate = cts/area
        if roi is self.roi:
            self.pac_tab.pacCounts.setValue(cts)
            self.pac_tab.pacArea.setValue(area)
            self.pac_tab.pacRate.setValue(rate)
            self.std_tab.stdCounts.setValue(cts)
            self.std_tab.stdArea.setValue(area)
            self.std_tab.stdRate.setValue(rate)
        else:
            self.pac_tab.bkgCounts.setValue(cts)
            self.pac_tab.bkgArea.setValue(area)
            self.pac_tab.bkgRate.setValue(rate)
            self.std_tab.bkgCounts.setValue(cts)
            self.std_tab.bkgArea.setValue(area)
            self.std_tab.bkgRate.setValue(rate)
        

    def sendData(self):
        if self.state[0]:
            self.state[0] = False
            self.plt.removeItem(self.roi)
        else:
            self.state[1] = False
            self.plt.removeItem(self.bkgRoi)
        ind = self.prevData
        self.currentData = ind
        ds = self.files[ind]
        pxdata = ds.pixel_array
        le = len(pxdata)
        self.img.setImage(pxdata)
        self.plt.autoBtnClicked()
        tab = self.tabWidget.currentIndex()
        if tab == 0:
            if self.pac_tab.radBkg.isChecked():
                self.plt.addItem(self.bkgRoi)
                self.state[1] = True
            else:
                self.plt.addItem(self.roi)
                self.state[0] = True
        else:
            if self.std_tab.radBkg.isChecked():
                self.plt.addItem(self.bkgRoi)
                self.state[1] = True
            else:
                self.plt.addItem(self.roi)
                self.state[0] = True
        ps = float(ds.PixelSpacing[0])      
        px = round(110 / ps - 0.5)
        self.roi.setSize([px, px])
        self.roi.setPos([(le-px)/2, -(le+px)/2])
        px = round(le * 0.75 + 0.5)
        self.bkgRoi.setSize([px, px])
        self.bkgRoi.setPos([(le-px)/2, -(le+px)/2])
        self.bound.setRect(0, -le+1, le-1, le)
        self.tabWidget.setEnabled(True)

    def itemChanged(self, ind):
        ds = self.files[ind]
        pxdata = ds.pixel_array
        self.prevData = ind
        self.img_prev.setImage(pxdata)
        self.plt_prev.autoBtnClicked()

    def btn_clicked(self):
        old = self.path
        self.path = QtGui.QFileDialog.getExistingDirectory(
            self, 'Elegir Carpeta', self.path
        )
        if self.path:
            self.list.clear()
            self.files.clear()
            self.files = find_files(self.path)
            if self.files:
                for file in self.files:
                    name = file.SeriesDescription
                    self.list.addItem(QtGui.QListWidgetItem(name))
                # self.tabs[0].newFolder(self.files, self.path)
                # self.tabs[1].newFolder(self.files, self.path)
                # # self.tabs[2].newFolder(self.files, self.path)
                # self.tabs[3].newFolder(self.files, self.path)
                # # self.tabs[4].newFolder(self.files, self.path)
                self.list.setCurrentRow(0)
                
                return True
        else:
            self.path = old


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
    path = '220502\\2'
    a = find_files(path)
    print('Hola QT')
    dark_theme = True
    app = QtWidgets.QApplication(sys.argv)
    window = IodoQuant()
    if dark_theme:
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    else:
        app.setStyleSheet('')
    window.show()
    sys.exit(app.exec_())
