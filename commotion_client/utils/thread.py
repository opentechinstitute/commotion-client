#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
thread

Implementation of a generic thread class.

Key componenets handled within:

"""
import logging

from PyQt4 import QtCore
import time

class GenericThread(QtCore.QThread):
    def __init__(self):
        QtCore.QThread.__init__(self)
        self.log = logging.getLogger("commotion_client."+__name__) #TODO commotion_client is still being called directly from one level up so it must be hard coded as a sub-logger if called from the command line.
        self.log.debug(QtCore.QCoreApplication.translate("logs","Created thread."))

        def __del__(self):
            self.wait()

        def run(self):
            self.log.debug(QtCore.QCoreApplication.translate("logs","Starting thread."))
            return
        
        
