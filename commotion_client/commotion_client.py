#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Commotion_client

The main python script for implementing the commotion_client GUI.

Key componenets handled within:
 * creation of main GUI
 * command line argument parsing
 * translation
 * initial logging settings

"""

import sys
import argparse
import logging

from PyQt4 import QtGui
from PyQt4 import QtCore

from commotion_client.utils import logger
from commotion_client.utils import thread
from commotion_client.utils import single_application
from commotion_client.utils import extension_manager

from commotion_client.GUI import main_window
from commotion_client.GUI import system_tray

#from controller import CommotionController #TODO Create Controller

import time

def get_args():
    #Handle command line arguments
    arg_parser = argparse.ArgumentParser(description="Commotion Client")
    arg_parser.add_argument("-v", "--verbose",
                            help="Define the verbosity of the Commotion Client.",
                            type=int, choices=range(1, 6))
    arg_parser.add_argument("-l", "--logfile",
                            help="Choose a logfile for this instance")
    arg_parser.add_argument("-d", "--daemon", action="store_true",
                            help="Start the application in Daemon mode (no UI).")
    arg_parser.add_argument("-m", "--message",
                            help="Send a message to any existing Commotion Application")
    arg_parser.add_argument("-k", "--key",
                            help="Choose a unique application key for this Commotion Instance",
                            type=str)
    args = arg_parser.parse_args()
    parsed_args = {}
    parsed_args['message'] = args.message if args.message else False
    #TODO getConfig() #actually want to get this from commotion_config
    parsed_args['logLevel'] = args.verbose if args.verbose else 2
    parsed_args['logFile'] = args.logfile if args.logfile else None
    parsed_args['key'] = ['key'] if args.key else "commotionRocks" #TODO the key is PRIME easter-egg fodder
    parsed_args['status'] = "daemon" if args.daemon else False
    return parsed_args

#==================================
# Main Applicaiton Creator
#==================================

def main():
    """
    Function that handles command line arguments, translation, and creates the main application.
    """
    args = get_args()
    #Create Instance of Commotion Application
    app = CommotionClientApplication(args, sys.argv)

    #Enable Translations #TODO This code needs to be evaluated to ensure that it is pulling in correct translators
    locale = QtCore.QLocale.system().name()
    qt_translator = QtCore.QTranslator()
    if qt_translator.load("qt_"+locale, ":/"):
        app.installTranslator(qt_translator)
        app_translator = QtCore.QTranslator()
        if app_translator.load("imagechanger_"+locale, ":/"): #TODO This code needs to be evaluated to ensure that it syncs with any internationalized images
            app.installTranslator(app_translator)

    #check for existing application w/wo a message
    if app.is_running():
        if args['message']:
            #Checking for custom message
            msg = args['message']
            app.send_message(msg)
            app.log.info(app.translate("logs", "application is already running, sent following message: \n\"{0}\"".format(msg)))
        else:
            app.log.info(app.translate("logs", "application is already running. Application will be brought to foreground"))
            app.send_message("showMain")
        app.end("Only one instance of a commotion application may be running at any time.")

    sys.exit(app.exec_())
    app.log.debug(app.translate("logs", "Shutting down"))

class HoldStateDuringRestart(thread.GenericThread):
    """
    A thread that will run during the restart of all other components to keep the applicaiton alive.
    """

    def __init__(self):
        super().__init__()
        self.restart_complete = None
        self.log = logging.getLogger("commotion_client."+__name__)

    def end(self):
        self.restart_complete = True

    def run(self):
        self.log.debug(QtCore.QCoreApplication.translate("logs", "Running restart thread"))
        while True:
            time.sleep(0.3)
            if self.restart_complete:
                self.log.debug(QtCore.QCoreApplication.translate("logs", "Restart event identified. Thread quitting"))
                break
        self.end()
        
class CommotionClientApplication(single_application.SingleApplicationWithMessaging):
    """
    The final layer of the class onion that is the Commotion client. This class includes functions to enable the sub-processes and modules of the Commotion Client (GUI's and controllers). 
    """

    restarted = QtCore.pyqtSignal()
    
    def __init__(self, args, argv):
        super().__init__(args['key'], argv)
        status = args['status']
        _logfile = args['logFile']
        _loglevel = args['logLevel']
        self.init_logging(_loglevel, _logfile)
        #Set Application and Organization Information
        self.setOrganizationName("The Open Technology Institute")
        self.setOrganizationDomain("commotionwireless.net")
        self.setApplicationName(self.translate("main", "Commotion Client")) #special translation case since we are outside of the main application
        self.setWindowIcon(QtGui.QIcon(":logo48.png"))
        self.setApplicationVersion("1.0") #TODO Generate this on build
        self.translate = QtCore.QCoreApplication.translate
        self.status = status
        self.controller = False
        self.main = False
        self.sys_tray = False

        #initialize client (GUI, controller, etc) upon event loop start so that exit/quit works on errors.
        QtCore.QTimer.singleShot(0, self.init_client)


#=================================================
#               CLIENT LOGIC
#=================================================

    def init_client(self):
        """
        Start up client using current status to determine run_level.
        """
        try:
            if not self.status:
                self.start_full()
            elif self.status == "daemon":
                self.start_daemon()
        except Exception as _excp: #log failure here and exit
            _catch_all = self.translate("logs", "Could not fully initialize applicaiton. Application must be halted.")
            self.log.critical(_catch_all)
            self.log.exception(_excp)
            self.end(_catch_all)

    def init_logging(self, level=None, logfile=None):
        self.logger = logger.LogHandler("commotion_client", level, logfile)
        self.log = self.logger.get_logger()
    
    def start_full(self):
        """
        Start or switch client over to full client.
        """
        extensions = extension_manager.ExtensionManager()
        if not extensions.check_installed():
            extensions.init_extension_libraries()
        if not self.main:
            try:
                self.main = self.create_main_window()
            except Exception as _excp:
                _catch_all = self.translate("logs", "Could not create Main Window. Application must be halted.")
                self.log.critical(_catch_all)
                self.log.exception(_excp)
                self.end(_catch_all)
            else:
                self.init_main()
            try:
                self.sys_tray = self.create_sys_tray()
            except Exception as _excp:
                _catch_all = self.translate("logs", "Could not create system tray. Application must be halted.")
                self.log.critical(_catch_all)
                self.log.exception(_excp)
                self.end(_catch_all)
            else:
                self.init_sys_tray()

    def start_daemon(self):
        """
        Start or switch client over to daemon mode. Daemon mode runs the taskbar without showing the main window.
        """
        try:
            #Close main window without closing taskbar and system tray
            if self.main:
                self.hide_main_window(force=True, errors="strict")
        except Exception as _excp:
            self.log.critical(self.translate("logs", "Could not close down existing GUI componenets to switch to daemon mode."))
            self.log.exception(_excp)
            raise
        try:
            #create controller and sys tray
            self.sys_tray = self.create_sys_tray()
            #if not self.controller: #TODO Actually create a stub controller file
            #    self.controller = create_controller()
        except Exception as _excp:
            self.log.critical(self.translate("logs", "Could not start daemon. Application must be halted."))
            self.log.exception(_excp)
            raise
        else:
            self.init_sys_tray()

    def stop_client(self, force_close=None):
        """
        Stops all running client processes.

        @param force_close bool Whole application exit if clean close fails. See: close_controller() & close_main_window()
        """
        try:
            self.close_main_window(force_close)
            self.close_sys_tray(force_close)
            self.close_controller(force_close)
        except Exception as _excp:
            if force_close:
                _catch_all = self.translate("logs", "Could not cleanly close client. Application must be halted.")
                self.log.critical(_catch_all)
                self.log.exception(_excp)
                self.end(_catch_all)
            else:
                self.log.error(self.translate("logs", "Client could not be closed."))
                self.log.info(self.translate("logs", "It is reccomended that you restart the application."))
                self.log.exception(_excp)

    def restart_client(self, force_close=None):
        """
        Restarts the entire client stack according to current application status.

        @param force_close bool Whole application exit if clean close fails. See: close_controller() & close_main_window()
        """
        #hold applicaiton state while restarting all other components.
        _restart = HoldStateDuringRestart()
        _restart.start()
        try:
            self.stop_client(force_close)
            self.init_client()
        except Exception as _excp:
            if force_close:
                _catch_all = self.translate("logs", "Client could not be restarted. Applicaiton will now be halted")
                self.log.error(_catch_all)
                self.log.exception(_excp)
                self.end(_catch_all)
            else:
                self.log.error(self.translate("logs", "Client could not be restarted."))
                self.log.info(self.translate("logs", "It is reccomended that you restart the application."))
                self.log.exception(_excp)
                raise
        _restart.end()

#=================================================
#                 MAIN WINDOW
#=================================================
        
    def create_main_window(self):
        """
        Will create a new main window or return existing main window if one is already created.
        """
        if self.main:
            self.log.debug(self.translate("logs", "New window requested when one already exists. Returning existing main window."))
            self.log.info(self.translate("logs", "If you would like to close the main window and re-open it please call close_main_window() first."))
            return self.main
        try:
            _main = main_window.MainWindow()
        except Exception as _excp:
            self.log.critical(self.translate("logs", "Could not create Main Window. Application must be halted."))
            raise
        else:
            return _main

    def init_main(self):
        """
        Main window initializer that shows and connects the main window's messaging function to the app message processor.
        """
        try:
            self.main.app_message.connect(self.process_message)
            if self.sys_tray:
                self.sys_tray.exit.triggered.connect(self.main.exitEvent)
                self.sys_tray.show_main.connect(self.main.bring_front)
        except Exception as _excp:
            self.log.error(self.translate("logs", "Could not initialize connections between the main window and other application components."))
            self.log.exception(_excp)
            raise
        try:
            self.main.show()
        except Exception as _excp:
            self.log.error(self.translate("logs", "Could not show the main window."))
            self.log.exception(_excp)
            raise

    def hide_main_window(self, force=None, errors=None):
        """
        Attempts to hide the main window without closing the task-bar.

        @param force bool Force window reset if hiding is unsuccessful.
        @param errors If set to "strict" errors found will be raised before returning the boolean result.
        @return bool Return True if successful and false is unsuccessful.
        """
        try:
            self.main.exit()
        except Exception as _excp:
            self.log.error(self.translate("logs", "Could not hide main window. Attempting to close all and only open taskbar."))
            self.log.exception(_excp)
            if force:
                try:
                    self.main.purge()
                    self.main = None
                    self.main = self.create_main_window()
                except Exception as _excp:
                    self.log.error(self.translate("logs", "Could not force main window restart."))
                    self.log.exception(_excp)
                    raise
            elif errors == "strict":
                raise
            else:
                return False
        else:
            return True
        #force hide settings
        try:
            #if already open, then close first
            if self.main:
                self.close_main_window()
            #re-open
            self.main = main_window.MainWindow()
            self.main.app_message.connect(self.process_message)
        except:
            self.log.error(self.translate("logs", "Could close and re-open the main window."))
            self.log.exception(_excp)
            if errors == "strict":
                raise
            else:
                return False
        else:
            return True
        return False

    def close_main_window(self, force_close=None):
        """
        Closes the main window and task-bar. Only removes the GUI components without closing the application.

        @param force_close bool If the application fails to kill the main window, the whole application should be shut down.
        @return bool
        """
        try:
            self.main.purge
            self.main = False
        except Exception as _excp:
            self.log.error(self.translate("logs", "Could not close main window."))
            if force_close:
                self.log.info(self.translate("logs", "force_close activated. Closing application."))
                try:
                    self.main.deleteLater()
                    self.main = False
                except Exception as _excp:
                    _catch_all = self.translate("logs", "Could not close main window using its internal mechanisms. Application will be halted.")
                    self.log.critical(_catch_all)
                    self.log.exception(_excp)
                    self.end(_catch_all)
            else:
                self.log.error(self.translate("logs", "Could not close main window."))
                self.log.info(self.translate("logs", "It is reccomended that you close the entire application."))
                self.log.exception(_excp)
                raise

#=================================================
#                 CONTROLLER
#=================================================

    def create_controller(self):
        """
        Creates a controller to act as the middleware between the GUI and the commotion core.
        """
        try:
            pass #replace when controller is ready
            #self.controller = CommotionController() #TODO Implement controller
            #self.controller.init() #??????
        except Exception as _excp:
            self.log.critical(self.translate("logs", "Could not create controller. Application must be halted."))
            self.log.exception(_excp)
            raise

    def init_controller(self):
        pass

    def close_controller(self, force_close=None):
        """
        Closes the controller process.

        @param force_close bool If the application fails to kill the controller, the whole application should be shut down.
        """
        try:
            pass #TODO Swap with below when controller close function is instantiated
            #if self.controller.close():
            #    self.controller = None
        except Exception as _excp:
            self.log.error(self.translate("logs", "Could not close controller."))
            if force_close:
                self.log.info(self.translate("logs", "force_close activated. Closing application."))
                try:
                    del self.controller
                except Exception as _excp:
                    _catch_all = self.translate("logs", "Could not close controller using its internal mechanisms. Application will be halted.")
                    self.log.critical(_catch_all)
                    self.log.exception(_excp)
                    self.end(_catch_all)
            else:
                self.log.error(self.translate("logs", "Could not cleanly close controller."))
                self.log.info(self.translate("logs", "It is reccomended that you close the entire application."))
                self.log.exception(_excp)
                raise


#=================================================
#                 SYSTEM TRAY
#=================================================
            
    def init_sys_tray(self):
        """
        System Tray initializer that runs all processes required to connect the system tray to other application commponents
        """
        try:
            if self.main:
                self.sys_tray.exit.triggered.connect(self.main.exitEvent)
                self.sys_tray.show_main.connect(self.main.bring_front)
        except Exception as _excp:
            self.log.error(self.translate("logs", "Could not initialize connections between the system tray and other application components."))
            self.log.exception(_excp)
            raise

    def create_sys_tray(self):
        """
        Starts the system tray
        """
        try:
            tray = system_tray.TrayIcon()
        except Exception as _excp:
            self.log.error(self.translate("logs", "Could not start system tray."))
            self.log.exception(_excp)
            raise
        else:
            return tray

    def close_sys_tray(self, force_close=None):
        """
        Closes the system tray. Only removes the GUI components without closing the application.

        @param force_close bool If the application fails to kill the main window, the whole application should be shut down.
        @return bool 
        """
        try:
            self.sys_tray.close()
            self.sys_tray = False
        except Exception as _excp:
            self.log.error(self.translate("logs", "Could not close system tray."))
            if force_close:
                self.log.info(self.translate("logs", "force_close activated. Closing application."))
                try:
                    self.sys_tray.deleteLater()
                    self.sys_tray.close()
                except:
                    _catch_all = self.translate("logs", "Could not close system tray using its internal mechanisms. Application will be halted.")
                    self.log.critical(_catch_all)
                    self.log.exception(_excp)
                    self.end(_catch_all)
            else:
                self.log.error(self.translate("logs", "Could not close system tray."))
                self.log.info(self.translate("logs", "It is reccomended that you close the entire application."))
                self.log.exception(_excp)
                raise

#=================================================
#               APPLICATION UTILS
#=================================================

    def process_message(self, message):
        """
        Process which processes messages an app receives and takes actions on valid requests.
        """
        if message == "showMain":
            if self.main != False:
                self.main.show()
                self.main.raise_()
        elif message == "restart":
            self.log.info(self.translate("logs", "Received a message to restart. Restarting Now."))
            self.restart_client(force_close=True) #TODO, might not want strict here post-development
        elif message == "debug":
            self.logger.set_verbosity("DEBUG")
        else:
            self.log.info(self.translate("logs", "message \"{0}\" not a supported type.".format(message)))

    def end(self, message=None):
        """
        Handles properly exiting the application.

        @param message string optional exit message to print to standard error on application close. This will FORCE the application to close in an unclean way.
        """
        if message:
            self.log.error(self.translate("logs", message))
            self.exit(1)
        else:
            self.quit()

if __name__ == "__main__":
    main()
