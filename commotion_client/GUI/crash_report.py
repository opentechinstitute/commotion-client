#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

crash_reporter

The crash handler for the gui components of the commotion client.

Key components handled within.
 * creation of the crash report #TODO
 * loading the crash-report window #TODO
 * sending crash report when internet is available #TODO

"""

#Standard Library Imports
import logging
import traceback
import uuid

#PyQt imports
from PyQt4 import QtCore
from PyQt4 import QtGui

from commotion_client.GUI.ui import Ui_crash_report_window

class CrashReport(Ui_crash_report_window.crash_window):

    #A signal userd to alert the crash reporter to create a crash report window and await report information.
    crash_override = QtCore.pyqtSignal()
    crash_info = QtCore.pyqtSignal(str, dict) #generate a signal process that can accept a string containing the module name and a dict of the report data
    crash = QtCore.pyqtSignal(str)
    alert_user = QtCore.pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__()
        self.log = logging.getLogger("commotion_client."+__name__) #TODO commotion_client is still being called directly from one level up so it must be hard coded as a sub-logger if called from the command line.
        self.setupUi(self) #run setup function from ui_crash_window
        self.create_uuid() #create uuid for this crash report instance
        self.report_timer = QtCore.QTimer()
        #if alert_user signal received show the crash window
        self.alert_user.connect(self.crash_alert)
        
        self.send_report.clicked.connect(self.generate_report)

        #Capture Quit and Reset Buttons
        self.restart_button.clicked.connect(self.check_restart)
        self.quit_button.clicked.connect(self.check_quit)

    def crash_alert(self, error):
        if error:
            self.error_text.setText(error)
            self.error_msg = error
            self.retranslateUi(self)
                
        self.crash_override.emit()
        self.exec_()
        
    def check_restart(self):
        if self.send_report.isChecked():
            self.save_report()
        self.crash.emit("restart")
                    
    def check_quit(self):
        if self.send_report.isChecked():
            self.save_report()
        self.crash.emit("quit")

    def generate_report(self):
        #Check if report is already generated
        self.gatherer = ReportGatherer(self)
        
        #Add initial error
        if self.error_msg:
            self.gatherer.add_item("error", {"error":self.error_msg})

        #connect the add_report signal to the report gatherer's add report function.
        #called from mainWindow as: self.SUBSECTION.crashReport.connect(self.CrashReport.add_report)
        self.crash_info.connect(self.gatherer.add_item)

        #TODO: Meaure how long it takes to return reports from various numbers of functions and modules to see how long this countdown should be (currently 5 seconds).
        self.countdown = 5
        self.countdown_timer = QtCore.QTimer()
        self.countdown_timer.timeout.connect(self.update_countdown)
        self.countdown_timer.start()

    def update_countdown(self):
        """
        Slot for countdown timer timeout that populates the graphical countdown if required.        
        """
        self.countdown -= 1
        self.report_gen_countdown.setProperty("intValue", self.countdown)
        if self.countdown <= 0:
            self.countdown_timer.stop()
            self.report_loading_label.hide()
            self.report_gen_countdown.hide()
            self.set_report() #set report upon completion


    def set_report(self):
        """
        set_report creates and saves the current error report and then disconnects crash_info signal.
        """
        #turn off report gatherer
        self.crash_info.disconnect()
        try:
            self.compiled_report = self.gatherer.get_report()
        except Exception as e:
            self.log.error(QtCore.QCoreApplication.translate("logs", "Faile to create a crash report."))
            self.log.debug(e, exc_info=1)
            self.crash_report.setPlainText(QtCore.QCoreApplication.translate("A crash report could not be generated."))
            return
        else:
            #send to user if window activated
            printable_report = []
            try:
                for section, results in self.compiled_report.items():
                    printable_report.append("\n==========  "+section+"  ==========\n")
                    #format and append each name-value pair to the report.
                    printable_report.append("\n".join(['%s = %s' %(name, value) for name, value in results.items()]))
            except Exception as e:
                self.log.error(QtCore.QCoreApplication.translate("logs", "Failed to format crash report for user to view."))
                self.log.debug(e, exc_info=1)
                self.crash_report.setPlainText(QtCore.QCoreApplication.translate("Unable to parse crash report for viewing. You can send the report without viewing it or un-check \"Send crash report\" to cancel sending this report."))
            else:
                self.crash_report.setPlainText("\n".join(printable_report))
                #todo add logs

    def save_report(self):
        """
        TODO ADD python-gnupg encryption to all data saved here.
        """
        #Save user comments
        try:
            self.compiled_report['error']['comments'] = str(self.comment_field.toPlainText())
        except Exception as e:
            self.log.info(QtCore.QCoreApplication.translate("logs", "The crash reporter could not store user comments in the crash report."))
            self.log.debug(e, exc_info=1)
        _settings = QtCore.QSettings()
        _settings.beginGroup("CrashReport/"+self.uuid) #create a unique crash report
        for section, results in self.compiled_report.items():
            for name, value in results.items():
                _settings.setValue(section+"/"+name, value)
        _settings.endGroup()

    def create_uuid(self):
        dash_map = str.maketrans({"-":None}) #create a map of the dash char
        self.uuid = str.translate(str(uuid.uuid1()), dash_map) #create a uuid and remove dashes


class ReportGatherer():

    def __init__(self, parent=None):
        self.report = {}
        super().__init__()
        self.log = logging.getLogger("commotion_client."+__name__) #TODO commotion_client is still being called directly from one level up so it must be hard coded as a sub-logger if called from the command line.

    def get_report(self):
        #Add system info into report
        try:
            self.report['system'] = self.get_defaults()
        except Exception as e:
            self.log.warn(QtCore.QCoreApplication.translate("logs", "Could not add system information into the crash report."))
            self.log.debug(e, exc_info=1)
        return self.report

    def add_item(self, name, item):
        try:
            self.report[name] = item
        except Exception as e:
            self.log.warn(QtCore.QCoreApplication.translate("logs", "The crash reporter could not add data from {0} into the crash report.").format(name))
            self.log.debug(e, exc_info=1)

    def get_defaults(self):
        system_values = {}
        #get current app instance and the application version set there
        system_values['version'] = QtGui.QApplication.instance().applicationVersion()
        
        if QtCore.QSysInfo.ByteOrder == 0:
            system_values['endian'] = "big endian"
        else:
            system_values['endian'] =  "little endian"
        system_values['architecture'] = str(QtCore.QSysInfo.WordSize)+"bit"

        return system_values
