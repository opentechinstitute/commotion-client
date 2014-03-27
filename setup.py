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
setup.py

This module includes the cx_freeze functionality for building the bundled extensions.

You can find further documentation on this in the build/ directory under README.md.
"""
import os
import sys
#import the setup.py version of setup
from cx_Freeze import setup, Executable

#---------- OS Setup -----------#

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

# Windows requires the icon to be specified in the setup.py.
icon = "commotion_client/assets/images/logo32.png"

#---------- Packages -----------#
    
# Define core packages.
core_pkgs = ["commotion_client", "utils", "GUI", "assets"]
# Define bundled "core" extensions here.
core_extensions = ["config_editor"]
# Add core_extensions to core packages.
for ext in core_extensions:
    core_pkgs.append("extensions."+ext)


# Include compiled assets file.
assets_file = os.path.join("commotion_client", "assets", "commotion_assets_rc.py")
# Place compiled assets file into the root directory.
include_assets = (assets_file, "commotion_assets_rc.py")

#---------- Executable Setup -----------#

exe = Executable(
    targetName="Commotion",
    script="commotion_client/commotion_client.py",
    packages=core_pkgs,
    )

#---------- Core Setup -----------#

setup(name="Commotion Client",
      version="1.0",
      url="commotionwireless.net",
      license="Affero General Public License V3 (AGPLv3)",
      executables = [exe],
      options = {"build_exe":{"include_files": [include_assets]}}
  )
