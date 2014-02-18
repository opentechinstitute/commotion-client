#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
restart_window

Key componenets handled within:

"""
#Standard Library Imports
import logging

#PyQt imports
from PyQt4 import QtCore
from PyQt4 import QtGui

#Commotion Client Imports
from GUI.ui import Ui_restart_window


class RestartWindow(Ui_restart_window.restart_window):

    def __init__(self):
        super().__init__()
        self.exec_()
    


