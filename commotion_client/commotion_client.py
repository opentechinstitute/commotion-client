#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Commotion_client

The main python script for implementing the commotion_client GUI.

Key componenets handled within:
 * singleApplication mode
 * cross instance messaging
 * creation of main GUI
 * command line argument parsing
 * translation
 * initial logging settings

"""

import sys
import argparse
import logging

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
    Function that handles command line arguments, translation, and creates the main application.
    """
    
    #Handle command line arguments
    argParser = argparse.ArgumentParser(description="Commotion Client")
    argParser.add_argument("-v", "--verbose", help="Define the verbosity of the Commotion Client.", type=int, choices=range(1, 6))
    argParser.add_argument("-l", "--logfile", help="Choose a logfile for this instance")
    argParser.add_argument("-d", "--daemon", action="store_true", help="Start the application in Daemon mode (no UI).")
    argParser.add_argument("--headless", action="store_true", help="Start the application in full headless mode (no status bar or UI).")
    argParser.add_argument("-m", "--message", help="Send a message to any existing Commotion Application")
    argParser.add_argument("-k", "--key", help="Choose a unique application key for this Commotion Instance", type=str)
    args = argParser.parse_args()
    if args.verbose:
        logLevel = args.verbose
    else:
        logLevel = 2 #TODO getConfig() #actually want to get this from commotion_config
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
    app = SingleApplicationWithMessaging(sys.argv, key)

    #Enable Translations
    locale = QtCore.QLocale.system().name()
    qtTranslator = QtCore.QTranslator()
    if qtTranslator.load("qt_"+locale, ":/"):
        app.installTranslator(qtTranslator)
        appTranslator = QtCore.QTranslator()
        if appTranslator.load("imagechanger_"+locale, ":/"):
            app.installTranslator(appTranslator)


    #check w/wo a message
    if app.isRunning():
        if args.message:
            #Checking for custom message
            msg = args.message
            app.sendMessage(msg)
            log.info(app.translate("logs", "application is already running, sent following message: \n\"{0}\"".format(msg)))
        else:
            log.info(app.translate("logs", "application is already running. Application will be brought to foreground"))
            app.sendMessage("showMain")
        sys.exit(1)


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
    
    #Log at shutdown when verbose is specified
    log.debug(app.translate("logs", "Shutting down"))
    
class SingleApplication(QtGui.QApplication):
    """
    Single application instance uses a key and shared memory to ensure that only one instance of the Commotion client is ever running at the same time.
    """

    def __init__(self, argv, key):
        super().__init__(argv)

        #set function logger
        self.log = logging.getLogger("commotion_client."+__name__)
        
        #Keep Track of main widgets, so as not to recreate them.
        self.main = False
        self.statusBar = False
        self.controlPanel = False
        #Check for shared memory from other instances and if not created, create them.
        self._key = key
        self.sharedMemory = QtCore.QSharedMemory(self)
        self.sharedMemory.setKey(key)
        if self.sharedMemory.attach():
            self._isRunning=True
        else:
            self._isRunning=False
            if not self.sharedMemory.create(1):
                self.log.info(self.translate("logs", "Application shared memory already exists."))
                raise RuntimeError(self.sharedMemory.errorString())
                
    def isRunning(self):
        return self._isRunning


class SingleApplicationWithMessaging(SingleApplication):
    """
    The interprocess messaging class for the Commotion Client. This class extends the single application to allow for instantiations of the Commotion Client to pass messages to the existing client if it is already running. When a second instance of a Commotion Client is run without a message specified it will reaise the earler clients main window to the front and then close itself.

    e.g:
    python3.3 CommotionClient.py --message "COMMAND"
    """
    
    def __init__(self, argv, key):
        super().__init__(argv, key)

        self._key = key
        self._timeout = 1000
        #create server to listen for messages
        self._server = QtNetwork.QLocalServer(self)
        #Connect to messageAvailable signal created by handleMessage.
        self.connect(self, QtCore.SIGNAL('messageAvailable'), self.processMessage)

        if not self.isRunning():
            bytes.decode
            self._server.newConnection.connect(self.handleMessage)
            self._server.listen(self._key)

    def handleMessage(self):
        """
        Server side implementation of the messaging functions. This function waits for signals it receives and then emits a SIGNAL "messageAvailable" with the decoded message.
        
        (Emits a signal instead of just calling a function in case we decide we would like to allow other components or modules to listen for messages from new instances.)
        """
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            self.emit(QtCore.SIGNAL("messageAvailable"), bytes(socket.readAll().data()).decode('utf-8'))
            socket.disconnectFromServer()
            self.log.debug(self.translate("logs", "message received and emitted in a messageAvailable signal"))
        else:
            self.log.error(socket.errorString())

    def sendMessage(self, message):
        """
        Message sending function. Connected to local socket specified by shared key and if successful writes the message to it and returns. 
        """
        if self.isRunning():
            socket = QtNetwork.QLocalSocket(self)
            socket.connectToServer(self._key, QtCore.QIODevice.WriteOnly)
            if not socket.waitForConnected(self._timeout):
                self.log.error(socket.errorString())
                return False
            socket.write(str(message).encode("utf-8"))
            if not socket.waitForBytesWritten(self._timeout):
                self.log.error(socket.errorString())
                return False
            socket.disconnectFromServer()
            return True
        self.log.debug(self.translate("logs", "Attempted to send message when commotion client application was not currently running."))
        return False

    def processMessage(self, message):
        """
        Process which processes messages an app receives and takes actions on valid requests.
        """
        if message == "showMain":
            if self.main != False:
                self.main.show()
                self.main.raise_()
        else:
            self.log.info(self.translate("logs", "message \"{0}\" not a supported type.".format(message)))

if __name__ == "__main__":
    main()
