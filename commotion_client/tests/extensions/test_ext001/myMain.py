#Standard Library Imports
import logging

#PyQt imports
from PyQt4 import QtCore
from PyQt4 import QtGui

#import python modules created by qtDesigner and converted using pyuic4
from tests.extensions.test_ext001 import Ui_warning001
from tests.extensions.test_ext001 import Ui_mainWin


class viewport(QtGui.QWidget, Ui_mainWin.Ui_testExt001): #inheret from both widget and out object

    #signals for crash reporter
    start_report_collection = QtCore.pyqtSignal()
    data_report = QtCore.pyqtSignal(str, dict)
    error_report = QtCore.pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__()
        self.setupUi(self) #run setup function from pyuic4 object
        self.start_report_collection.connect(self.send_signal)
        #make central app main button turn on crash reporter
        self.warningButton.clicked.connect(self.send_error)

    
    def send_signal(self):
        self.data_report.emit("myModule", {"value01":"value", "value02":"value", "value03":"value"})

    def send_error(self):
        self.error_report.emit("THIS IS AN ERROR")
