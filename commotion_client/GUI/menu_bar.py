#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""
MenuBar

The menu bar used for hierarchical navigation of commotion extensions.

Key componenets handled within:
 * 

"""

#Standard Library Imports
import logging
from functools import partial

#PyQt imports
from PyQt4 import QtCore
from PyQt4 import QtGui

#Commotion Client Imports
from utils import config

class MenuBar(QtGui.QWidget):

    #create signal used to communicate with mainWindow on viewport change
    viewport_requested = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()

        self.layout = QtGui.QVBoxLayout()
        
        #set function logger
        self.log = logging.getLogger("commotion_client."+__name__)

        try:
            self.populateMenu()
        except Exception as e:
            self.log.critical(e, exc_info=1)
            #TODO RAISE CRITICAL ERROR WINDOW AND CLOSE DOWN THE APPLICATION HERE
        self.setLayout(self.layout)
        

    def request_viewport(self, viewport):
        """
        When called will emit a request for a viewport change.
        """
        self.log.debug(QtCore.QCoreApplication.translate("logs", "Request to change viewport sent"))
        self.viewport_requested.emit(viewport)

    def populateMenu(self):
        """
        Clears and re-populates the menu using the loaded extensions.
        """
        menuItems = {}
        extensions = list(config.find_configs("extension"))
        if extensions:
            topLevel = self.getParents(extensions)
            for topLevelItem in topLevel:
                try:
                    currentItem = self.addMenuItem(topLevelItem, extensions)
                    if currentItem:
                        menuItems[topLevelItem] = currentItem
                except Exception as e:
                    self.log.error(QtCore.QCoreApplication.translate("logs", "Loading extension \"{0}\" failed for an unknown reason.".format(topLevelItem)))
                    self.log.debug(e, exc_info=1)
            if menuItems:
                for title, section in menuItems.items():
                    try:
                        #Add top level menu item
                        self.layout.addWidget(section[0])
                        #Add sub-menu layout
                        self.layout.addWidget(section[1])
                    except Exception as e:
                        self.log.error(QtCore.QCoreApplication.translate("logs", "Could not add menu item \"{0}\" to menu layout.".format(title)))
                        self.log.debug(e, exc_info=1)
            else:
                self.log.error(QtCore.QCoreApplication.translate("logs", "No menu items could be created from the extensions found. Please re-run the commotion client with full verbosity to identify what went wrong."))
                raise Exception(QtCore.QCoreApplication.translate("exception", "No menu items could be created from the extensions found. Please re-run the commotion client with full verbosity to identify what went wrong."))
        else:
            self.log.error(QtCore.QCoreApplication.translate("logs", "No extensions found. Please re-run the commotion_client with full verbosity to find out what went wrong."))
            raise Exception(QtCore.QCoreApplication.translate("exception", "No extensions found. Please re-run the commotion_client with full verbosity to find out what went wrong."))
            #TODO Add a set of windowed error's for a variety of levels. Fatal err
        
        

    def addMenuItem(self, title, extensions):
        """
        Creates and returns a single top level menu item with cascading sub-menu items from a title and a dictionary of extensions.

        @param title the top level menu item to place everything under
        @param extensions the set of extensions to populate the menu with
        @return tuple containing top level button and hidden sub-menu
        """
        #Create Top level item button
        try:
            titleButton = QtGui.QPushButton(QtCore.QCoreApplication.translate("Menu Item", title))
            titleButton.setCheckable(True)
        except Exception as e:
            self.log.error(QtCore.QCoreApplication.translate("logs", "Could not create top level menu item {0}.".format(title)))
            self.log.debug(e, exc_info=1)
            return False
        #Create sub-menu
        subMenu = QtGui.QFrame()
        subMenuItems = QtGui.QVBoxLayout()
        #populate the sub-menu item table.
        for ext in extensions:
            if ext['parent'] and ext['parent'] == title:
                try: #Create subMenuWidget
                    subMenuItem = subMenuWidget(self)
                    subMenuItem.setText(QtCore.QCoreApplication.translate("Sub-Menu Item", ext['menuItem']))
                    #We use partial here to pass a variable along when we attach the "clicked()" signal to the MenuBars requestViewport function
                    subMenuItem.clicked.connect(partial(self.request_viewport, ext['name']))
                except Exception as e:
                    self.log.error(QtCore.QCoreApplication.translate("logs", "Faile to create sub-menu \"{0}\" object for \"{1}\" object.".format(ext['name'], title)))
                    self.log.debug(e, exc_info=1)
                    return False
                try:
                    subMenuItems.addWidget(subMenuItem)
                except Exception as e:
                    self.log.error(QtCore.QCoreApplication.translate("logs", "Failed to add sub-menu object  \"{0}\" to the sub-menu.".format(ext['name'])))
                    self.log.debug(e, exc_info=1)
                    return False
        subMenu.setLayout(subMenuItems)
        subMenu.hide()
        #Connect toggle on out checkable title button to the visability of our subMenu
        titleButton.toggled.connect(subMenu.setVisible)
        #package and return top level item and its corresponding subMenu
        section = (titleButton, subMenu)
        return section

    def getParents(self, extensionList):
        parents = []
        
        for ext in extensionList:
            parent = None
            if ext["parent"]:
                parent = ext["parent"]
                if parent not in parents:
                    parents.append(parent)
            else:
                if ext["menuItem"] not in parents:
                    parents.append(ext["menuItem"])
        return parents



class subMenuWidget(QtGui.QLabel):
    """
    This class extends QLabel to make clickable labels.
    """
    
    #FUN-FACT: Signals must be created outside of the init statement because "the library distinguishes between unbound and bound signals. The magic is performed as follows: "A signal (specifically an unbound signal) is an attribute of a class that is a sub-class of QObject. When a signal is referenced as an attribute of an instance of the class then PyQt5 automatically binds the instance to the signal in order to create a bound signal."
    clicked = QtCore.pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__()
        
    def mouseReleaseEvent(self, ev):
        self.clicked.emit()
