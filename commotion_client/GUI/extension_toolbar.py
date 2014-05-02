#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extension Toolbar

The toolbar object extensions can use to derive extra menu items from.

"""
#Standard Library Imports
import logging

#PyQt imports
from PyQt4 import QtCore
from PyQt4 import QtGui

#Commotion Client Imports
import commotion_assets_rc

class ExtensionToolBar(object):
    """
    The central widget for the commotion client. This widget initalizes all other sub-widgets and extensions as well as defines the paramiters of the main GUI container.


    An example of adding a single button to the menu that calls a function "save_form()"
    
    new_button = MenuItem
    my_button.setIcon(icon.save)
    my_button.setText(self.translate("menu", "Save"))
    new_button.action = self.save_form
    self.add_item(new_button)

    
    """

    def __init__(self, viewport):
        """Sets up all the translation, logging, and core items needed for an extension toolbar.
        
        Args:
          extension_menu_items (object): The extension specific menu-item to be used by an extension. This class is derived from the  
          viewport (object): The extensions viewport. This allows menu_items to have its actions interact with the current viewport.        
        """
        super().__init__()
        self._dirty = False
        self.log = logging.getLogger("commotion_client."+__name__)
        self.translate = QtCore.QCoreApplication.translate
        self.viewport = viewport
        self.menu_items = {}
        #The basic set of icons for extensions
        self.icon = {
            "save":QtGui.QIcon(":save32.png"),
            "load":QtGui.QIcon(":load32.png"),
            "user":QtGui.QIcon(":user32.png"),
            "settings":QtGui.QIcon(":settings32.png"),
            "full_screen_start":QtGui.QIcon(":full_screen_start32.png"),
            "full_screen_end":QtGui.QIcon(":full_screen_end32.png"),
        }

    def add_item(self, tool_button):
        if tool_button.icon().isNull():
            tool_button.setIcon(self.icon.settings)
        self.menu_items.append(tool_button)

class MenuItem(QtGui.QToolButton):
    """The menu_item template object

    To Make a basic toolbar button simply run the following.

    #From within the ExtensionToolBar
    my_button = MenuItem
    my_button.setIcon(self.icon.save)
    my_button.setText(self.translate("menu", "Save"))
    my_button.triggered.connect(self.my_save_function)

    To Make a toolbar with a menu run the following.

    #From within the ExtensionToolBar
    my_menu = MenuItem
    my_menu.setIcon(self.icon.settings)
    my_menu.setText(self.translate("menu", "Options"))
    my_menu.set_menu(True)
    menu_save = QtGui.QAction("Save", icons.save, self.my_save_function)
    my_menu.sub_menu.addAction(menu_save)
    #Using a custom icon from an extension.
    menu_load = QtGui.QAction("Load", QtGui.QIcon("icons/load.png"), statusTip=self.translate("menu", "Load a item from a file"), triggered=self.my_load_function)
    my_menu.menu.addAction(menu_load)

    menuItems are QToolButtons
    menuItems that have sub menu's are composed of a QMenu with QActions within it.

    QToolButton:http://pyqt.sourceforge.net/Docs/PyQt4/qtoolbutton.html
    QMenu: http://pyqt.sourceforge.net/Docs/PyQt4/qmenu.html
    QAction: http://pyqt.sourceforge.net/Docs/PyQt4/qaction.html
    
    """

    def __init__(self, parent=None, viewport=None):
        """Sets up all the core components needed for a minimal menuItem
        
        Args:
          viewport (object): The current viewport. This allows menu_items to have its actions interact with the current viewport.
        
        """
        super().__init__()
        self._dirty = False
        self.log = logging.getLogger("commotion_client."+__name__)
        self.translate = QtCore.QCoreApplication.translate
        self.viewport = viewport
        
    def set_menu(self, value):
        if value == True:
            self.log.debug(self.translate("logs", "Setting toolbar item {0} to be a menu.".format(self.text())))
            #Set menu to pop up immediately.
            self.setPopupMode(QtGui.QToolButton.InstantPopup)
            #Create a new menu and set it
            self.sub_menu = QtGui.QMenu(self)
            self.setMenu(self.sub_menu)
        elif value == False:
            self.log.debug(self.translate("logs", "Setting toolbar item {0} to NOT be a menu.".format(self.text())))
            #Remove the menu if it exists
            self.sub_menu = None
        else:
            self.log.debug(self.translate("logs", "{0} is not a proper value for set_menu. Please use a bool value True or False.".format(value)))
            raise ValueError(self.translate("logs", "Attempted to set the menu state to an invalid value."))

