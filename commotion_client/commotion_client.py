#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Commotion_client

The main python script for implementing the commotion_client GUI.

"""

import sys
import argparse

from PyQt4 import QtCore
from PyQt4 import QtGui
from PyQt4 import QtNetwork

from assets import assets
from utils import logger
from GUI.MainWindow import MainWindow
#from commotion_controller import CommotionController #TODO Create Controller


#==================================
# Main Applicaiton Creator
#==================================
def main():
    """
    The main application start up system. 
    """
    
    #Handle command line arguments
    argParser = argparse.ArgumentParser(description="Commotion Client")
    argParser.add_argument("-v", "--verbose", help="Define the verbosity of the Commotion Client.", type=int, choices=range(1, 6))
    argParser.add_argument("-l", "--logfile", help="Choose a logfile for this instance")
    argParser.add_argument("-d", "--daemon", action="store_true", help="Start the application in Daemon mode (no UI).")
    argParser.add_argument("--headless", action="store_true", help="Start the application in full headless mode (no status bar or UI).")
    argParser.add_argument("-m", "--message", help="Send a message to any existing Commotion Application.")
    argParser.add_argument("-k", "--key", help="Choose a unique application key for this Commotion Instance", type=str)
    args = argParser.parse_args()
    if args.verbose:
        logLevel = args.verbose
    else:
        logLevel = 2 #getConfig() #actually want to get this from commotion_config
    if args.logfile:
        logFile = args.logfile
    else:
        logFile = "temp/logfile.temp" #TODO change the logfile to be grabbed from the commotion config reader
    if args.key:
        key = args.key
    else:
        key = "commotionRocks" #TODO Should there be a default key?
    if args.headless:
        headless = True
    else:
        headless = False
    if args.daemon:
        daemon = True
    else:
        daemon = False

        
    #Enable Logging
    log = logger.set_logging("commotion_client", logLevel, logFile)

    #Create Instance of Commotion Application
    #check w/wo a message
    if args.message:
        msg = args.message
        app = SingleApplicationWithMessage(sys.argv, key)
        if app.isRunning():
            log.info("Commotion client called when already running. Checking for message.")
            #Checking for custom message
            app.sendMessage(msg)
            log.info("application is already running, sent following message: \n\"{0}\"".format(msg))
            sys.exit(1)
    else:
        app = SingleApplication(sys.argv, key)
        if app.isRunning():
            log.info("application is already running. No message has been sent")
            sys.exit(1)

    #Enable Translations
    locale = QtCore.QLocale.system().name()
    qtTranslator = QtCore.QTranslator()
    if qtTranslator.load("qt_"+locale, ":/"):
        app.installTranslator(qtTranslator)
        appTranslator = QtCore.QTranslator()
        if appTranslator.load("imagechanger_"+locale, ":/"):
            app.installTranslator(appTranslator)

    #Set Application and Organization Information
    app.setOrganizationName("The Open Technology Institute")
    app.setOrganizationDomain("commotionwireless.net")
    app.setApplicationName(app.translate("main", "Commotion Client")) #special translation case since we are outside of the main application
    app.setWindowIcon(QtGui.QIcon(":commotion_logo.png"))
    __version__ = "1.0"

    #Start GUI if not started at boot
    if not headless:
        pass #TODO implement status bar and contrroller
        ##statusBar = StatusBar.StatusBar()
        ##controller = CommotionController.CommotionController()
        if not daemon:
            if app.main == False:
                app.main = MainWindow()
                app.main.show()
    else:
        #Always start controller
        pass #TODO IMplement controller
        ##controller = CommotionController.CommotionController()

    #Start Application
    sys.exit(app.exec_())
    print(app.main)
    
    #Log at shutdown on verbose
    log.debug(app.translate("logs", "Shutting down"))
    
class SingleApplication(QtGui.QApplication):
    """
    Single application instance uses a key and shared memory to ensure that only one instance of the Commotion client is ever running at the same time.
    """

    def __init__(self, argv, key):
        super(SingleApplication, self).__init__(argv)
        #Keep Track of main widgets, so as not to recreate them.
        self.main = False
        self.statusBar = False
        self.controlPanel = False
        #Actual SinglePr
        self._key = key
        self.sharedMemory = QtCore.QSharedMemory(self)
        self.sharedMemory.setKey(key)
        if self.sharedMemory.attach():
            self._isRunning=True
        else:
            self._isRunning=False
            if not self.sharedMemory.create(1):
                log.info("Application shared memory already exists.")
                raise RuntimeError(self.sharedMemory.errorString())
                
    def isRunning(self):
        return self._isRunning


class SingleApplicationWithMessaging(SingleApplication):
    """
    The message enabled class for Commotion Client. This class extends the single application to allow for command line instantiations of the Commotion Client to pass messages to the existing client if it is already running by using its unique key.

    e.g:
    python3.3 CommotionClient.py -k commotion --message "COMMAND"
    """
    
    def __init__(self, argv, key, mode):
        super(SingleApplicationWithMessaging).__init__(self, argv, key)
        self._key = key
        self._timeout = 1000
        self._server = QtNetwork.QLocalServer(self)

        if not self.IsRunning():
            bytes.decode
            self._server.newConnection.connect(self.handleMessage)
            self._server.listen(self._key)

    def handleMessage(self):
        socket = self.localServer.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            self.emit(QtCore.SIGNAL("messageAvailable"), bytes(socket.readAll().data()).decode('utf-8'))
            socket.disconnectFromServer()
        else:
            log.error(socket.errorString())

    def sendMessage(self, message):
        if self.isRunning():
            socket = QtNetwork.QLocalSocket(self)
            socket.connectToServer(self._key, QtCore.QIODevice.WriteOnly)
            if not socket.WaitForConnected(self._timeout):
                log.error(socket.errorString())
                return False
            socket.disconnectFromServer()
            return True
        log.debug("Attempted to send message when commotion client application was not currently running.")
        return False

if __name__ == "__main__":
    main()
