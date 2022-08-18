# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 16:59:25 2022

TITLE: 

@author: Alejandro Condori aleja
E-mail: alejandrocondori2@gmail.com
Cel-WhatsApp: +54 9 294 412 5003
"""
from pyqtgraph.Qt import uic, QtGui, QtWidgets

# %%
ui_std, ui_std_parent = uic.loadUiType("stdWid.ui")
ui_pac, ui_pac_parent = uic.loadUiType("pacWid.ui")

# %%


class StdWidget(ui_std_parent, ui_std):

    def __init__(self):
        ui_std_parent.__init__(self)
        ui_std.__init__(self)
        self.setupUi(self)


class PacWidget(ui_pac_parent, ui_pac):

    def __init__(self):
        ui_pac_parent.__init__(self)
        ui_pac.__init__(self)
        self.setupUi(self)
