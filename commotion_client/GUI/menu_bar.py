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
from commotion_client.utils.extension_manager import ExtensionManager

class MenuBar(QtGui.QWidget):

    #create signal used to communicate with mainWindow on viewport change
    viewport_requested = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__()

        self.layout = QtGui.QVBoxLayout()
        
        #set function logger
        self.log = logging.getLogger("commotion_client."+__name__)
        self.translate = QtCore.QCoreApplication.translate
        self.ext_mgr = ExtensionManager()
        try:
            self.populate_menu()
        except (NameError, AttributeError) as _excpt:
            self.log.info(self.translate("logs", "The Menu Bar could not populate the menu"))
            raise
        self.log.debug(QtCore.QCoreApplication.translate("logs", "Menu bar has initalized successfully."))

    def request_viewport(self, viewport):
        """
        When called will emit a request for a viewport change.
        """
        self.log.debug(QtCore.QCoreApplication.translate("logs", "Request to change viewport sent"))
        self.viewport_requested.emit(viewport)
        
    def clear_layout(self, layout):
        """Clears a layout of all widgets.
 
        Args:
        layout (QLayout): A QLayout object that needs to be cleared of all objects.
        """        
        if not layout.isEmpty():
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())

    def populate_menu(self):
        """Resets and populates the menu using loaded extensions."""
        if not self.layout.isEmpty():
            self.clear_layout(self.layout)
        menu_items = {}
        if not self.ext_mgr.check_installed():
            self.ext_mgr.init_extension_libraries()
        extensions = self.ext_mgr.get_installed().keys()
        if extensions:
            top_level = self.get_parents(extensions)
            for top_level_item in top_level:
                try:
                    current_item = self.add_menu_item(top_level_item)
                except NameError as _excpt:
                    self.log.debug(self.translate("logs", "No extensions found under the parent item {0}. Parent item will not be added to the menu.".format(top_level_item)))
                    self.log.exception(_excpt)
                else:
                    if current_item:
                        menu_items[top_level_item] = current_item
            if menu_items:
                for title, section in menu_items.items():
                    #Add top level menu item
                    self.layout.addWidget(section[0])
                    #Add sub-menu layout
                    self.layout.addWidget(section[1])
            else:
                raise AttributeError(QtCore.QCoreApplication.translate("exception", "No menu items could be created from the extensions found. Please re-run the commotion client with full verbosity to identify what went wrong."))
        else:
            raise NameError(QtCore.QCoreApplication.translate("exception", "No extensions found. Please re-run the commotion_client with full verbosity to find out what went wrong."))
        self.setLayout(self.layout)
        
    def get_parents(self, extension_list):
        """Gets all unique parents from a list of extensions.

        This function gets the "parent" menu items from a list of extensions and returns a list of the unique members.

        Args:
          extension_list (list): A list containing a set of strings that list the names of extensions.

        Returns:
          A list of all the unique parents of the given extensions.
        
            ['parent item 01', 'parent item 02']
        """
        parents = []
        for ext in extension_list:
            try:
                parent = self.ext_mgr.get_property(ext, "parent")
            except KeyError:
                self.log.debug(self.translate("logs", "Config for {0} does not contain a {1} value. Setting {1} to default value.".format(ext, "parent")))
                parent = "Extensions"
            if parent not in parents:
                parents.append(parent)
        return parents


    def add_menu_item(self, parent):
        """Creates and returns a single top level menu item with cascading sub-menu items.
                
        Args:
        parent (string): The "parent" the top level menu item that is being requested.
        
        Returns:
        A tuple containing a top level button and its hidden sub-menu items.        
        """
        extensions = self.ext_mgr.get_extension_from_property('parent', parent)
        if not extensions:
            raise NameError(self.translate("logs", "No extensions found under the parent item {0}.".format(parent)))
        #Create Top level item button
        title_button = QtGui.QPushButton(QtCore.QCoreApplication.translate("Menu Item", parent))
        title_button.setCheckable(True)
        #Create sub-menu
        sub_menu = QtGui.QFrame()
        sub_menu_layout = QtGui.QVBoxLayout()
        #populate the sub-menu item table.
        for ext in extensions:
            sub_menu_item = subMenuWidget(self)
            try:
                menu_item_title = self.ext_mgr.get_property(ext, 'menu_item')
            except KeyError:
                menu_item_title = ext
            sub_menu_item.setText(QtCore.QCoreApplication.translate("Sub-Menu Item", menu_item_title))
            #We use partial here to pass a variable along when we attach the "clicked()" signal to the MenuBars requestViewport function
            sub_menu_item.clicked.connect(partial(self.request_viewport, ext))
            sub_menu_layout.addWidget(sub_menu_item)
        sub_menu.setLayout(sub_menu_layout)
        sub_menu.hide()
        #Connect toggle on out checkable title button to the visability of our subMenu
        title_button.toggled.connect(sub_menu.setVisible)
        #package and return top level item and its corresponding subMenu
        section = (title_button, sub_menu)
        return section


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
