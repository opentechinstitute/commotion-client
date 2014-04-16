#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

This program is a part of The Commotion Client

Copyright (C) 2014  Seamus Tuohy s2e@opentechinstitute.org

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

"""
CURRENTLY A DEVELOPMENT STUB!


setting.py

The Settings Manager

Key componenets handled within:
 * Loading and Unloading User Settings Files
 * Validating the scope of settings

"""
#Standard Library Imports
import logging

#PyQt imports
from PyQt4 import QtCore

#Commotion Client Imports


class UserSettingsManager(object):

    def __init__(self):
        """Create a settings object that is tied to a specific scope.
        CURRENTLY A DEVELOPMENT STUB!
        """
        self.settings = QtCore.QSettings()

    def save(self):
        """CURRENTLY A DEVELOPMENT STUB!"""
        #call PGP to save temporary file to correct encrypted file
        pass

    def load(self):
        """CURRENTLY A DEVELOPMENT STUB!"""

        #call pgp to get location of decrypted user file, if any
        #load global settings file.
        # QSettings.setUserIniPath (QString dir)
        #get
        pass
        
    def get(self):
        """CURRENTLY A DEVELOPMENT STUB!"""
        return self.settings

    

