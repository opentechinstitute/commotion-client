#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Toolbar

The core toolbar object for commotion viewports.

The tool bar is an object that is created in the main viewport. This tool-bar has pre-built objects for common functions and an add-on section that will allow a developer building a extension to add functionality they need.


"""
#Standard Library Imports
import logging

#PyQt imports
from PyQt4 import QtCore
from PyQt4 import QtGui

#Commotion Client Imports
from commotion_client.assets import commotion_assets_rc
from commotion_client.GUI import extension_toolbar


class ToolBar(QtGui.QWidget):
    """
    The Core toolbar object that populates manditory toolbar sections.
    """

    def __init__(self, parent=None, extension_toolbar=None, viewport):
        """Creates the core toolbar including any extension toolbar passed to it.
        
        Initializes the core functionality of the toolbar. If an extension_toolbar object is also passed to the toolbar it will attempt to add the extension toolbar into itself.
        
        Args:
          extension_toolbar (object): The extension specific menu-item to be used by an extension. This class is derived from the "commotion_client/GUI/extension_toolbar.ExtensionToolBar" object.
          viewport (object): The current viewport. This allows menu_items to have its actions interact with the current viewport.

        Raises:
          exception: Description.
        
        """
        super().__init__()
        self._dirty = False
        self.log = logging.getLogger("commotion_client."+__name__)
        self.translate = QtCore.QCoreApplication.translate

        self.viewport = viewport
        #Create toolbar object
        self.toolbar = QtGui.QToolBar(self)
        #Create & add settings item
        self.settings = self.init_settings()
        self.toolbar.addWidget(self.settings)
        #Create & add user item
#        self.user = self.init_user()
#        self.toolbar.addWidget(self.user)
        #Create extension toolbar section if needed
#        if extension_toolbar:
#            self.extension_toolbar = extension_toolbar(self, viewport)
#            self.init_extension_toolbar()

    def init_settings(self):
        """short description
        
        long description
        
        Args:
        name (type): Description.
        
        Returns:
        Description.
        
        Raises:
        exception: Description.
        
        """
        settings_menu = extension_toolbar.MenuItem(self, self.viewport)
        settings_menu.setIcon(extension_toolbar.icon.settings)
        settings_menu.setText(self.translate("menu", "Settings"))
        settings_menu.set_menu = True
        extensions_item = QtGui.QAction(self.translate("menu", "&Extensions"),
                                        statusTip=self.translate("menu", "Open the extensions menu."),
                                        triggered=self.load_extensions,
                                        parent=settings_menu)
        
        settings_item = QtGui.QAction(self.translate("menu", "&Settings"),
                                      QtGui.QIcon("icons/load.png"),
                                      statusTip=self.translate("menu", "Open the settings menu."),
                                      triggered=self.load_settings,
                                      parent=settings_menu)
        about_item = QtGui.QAction(self.translate("menu", "&About"),
                                   QtGui.QIcon("icons/load.png"),
                                   statusTip=self.translate("menu", "Open the \'about us\' page"),
                                   triggered=self.load_about,
                                   parent=settings_menu)
        exit_item = QtGui.QAction(self.translate("menu", "&Exit"),
                                  QtGui.QIcon("icons/load.png"),
                                  statusTip=self.translate("menu", "Exit the application."),
                                  triggered=self.exit_application,
                                  parent=settings_menu)
        update_item = QtGui.QAction(self.translate("menu", "&Update"),
                                    QtGui.QIcon("icons/load.png"),
                                    statusTip=self.translate("menu", "Open the updates page."),
                                    triggered=self.load_update,
                                    parent=settings_menu)
        return settings_menu
        
    def load_settings(self):
       """Opens the settings menu in the main viewport """
       pass
       
    def load_about(self):
       """Opens the about page in the main viewport """
       pass
       
    def load_update(self):
       """Opens the updates menu in the main viewport """
       pass
       
    def load_user(self):
       """Opens the user menu in the main viewport """
       pass
       
    def exit_application(self):
       """Exits the application."""
       pass
       
    def load_extensions(self):
        """Opens the extensions menu in the main viewport """
        pass
        
    def init_user(self):
        """short description
        
        long description
        
        Args:
        name (type): Description.
        
        Returns:
        Description.
        
        Raises:
        exception: Description.
        
        """
        pass



    def init_extension_toolbar(self):
        """short description
        
        long description
        
        Args:
        name (type): Description.
        
        Returns:
        Description.
        
        Raises:
        exception: Description.
        
        """
        for menu_item in self.extension_menu.menu_items:
            try:
                self.toolbar.addWidget(menu_item)
