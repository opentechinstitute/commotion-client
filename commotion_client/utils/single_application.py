#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
single_application

The single application handler classes the commotion client inherets its cross process communication from.

Key componenets handled within:
 * singleApplication mode
 * cross instance messaging

"""

import logging

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtNetwork


class SingleApplication(QtGui.QApplication):
    """
    Single application instance uses a key and shared memory to ensure that only one instance of the Commotion client is ever running at the same time.
    """

    def __init__(self, key, argv):
        super().__init__(argv)

        #set function logger
        self.log = logging.getLogger("commotion_client."+__name__)
        
        #Keep Track of main widgets, so as not to recreate them.
        self.main = False
        self.status_bar = False
        self.control_panel = False
        #Check for shared memory from other instances and if not created, create them.
        self._key = key
        self.shared_memory = QtCore.QSharedMemory(self)
        self.shared_memory.setKey(key)
        if self.shared_memory.attach():
            self._is_running = True
        else:
            self._is_running = False
            if not self.shared_memory.create(1):
                self.log.info(self.translate("logs", "Application shared memory already exists."))
                raise RuntimeError(self.shared_memory.errorString())
                
    def is_running(self):
        return self._is_running


class SingleApplicationWithMessaging(SingleApplication):
    """
    The interprocess messaging class for the Commotion Client. This class extends the single application to allow for instantiations of the Commotion Client to pass messages to the existing client if it is already running. When a second instance of a Commotion Client is run without a message specified it will reaise the earler clients main window to the front and then close itself.

    e.g:
    python3.3 CommotionClient.py --message "COMMAND"
    """
    
    def __init__(self, key, argv):
        super().__init__(key, argv)

        self._key = key
        self._timeout = 1000
        #create server to listen for messages
        self._server = QtNetwork.QLocalServer(self)
        #Connect to messageAvailable signal created by handle_message.
        self.connect(self, QtCore.SIGNAL('messageAvailable'), self.process_message)

        if not self.is_running():
            bytes.decode
            self._server.newConnection.connect(self.handle_message)
            self._server.listen(self._key)

    def handle_message(self):
        """
        Server side implementation of the messaging functions. This function waits for signals it receives and then emits a SIGNAL "messageAvailable" with the decoded message.
        
        (Emits a signal instead of just calling a function in case we decide we would like to allow other components or extensions to listen for messages from new instances.)
        """
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            self.emit(QtCore.SIGNAL("messageAvailable"), bytes(socket.readAll().data()).decode('utf-8'))
            socket.disconnectFromServer()
            self.log.debug(self.translate("logs", "message received and emitted in a messageAvailable signal"))
        else:
            self.log.error(socket.errorString())

    def send_message(self, message):
        """
        Message sending function. Connected to local socket specified by shared key and if successful writes the message to it and returns.
        """
        if self.is_running():
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

    def process_message(self, message):
        """
        Process which processes messages an app receives and takes actions on valid requests.
        """
        self.log.debug(self.translate("logs", "Applicaiton received a message {0}, but does not have a message parser to handle it.").format(message))
