#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from cx_Freeze import setup, Executable


icon = "assets/images/logo32.png"


# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

#define core packages
core_pkgs = ["commotion_client", "utils", "GUI", "assets"]
core_extensions = ["config_editor"]
packages = []
assets_file = os.path.join("commotion_client", "assets", "commotion_assets_rc.py")

#add core_extensions to core packages
for ext in core_extensions:
    core_pkgs.append("extensions."+ext)

exe = Executable(
    targetName="Commotion",
    script="commotion_client/commotion_client.py",
    packages=core_pkgs,
    )

setup(name="Commotion Client",
      version="1.0",
#      packages=["commotion_client"],
#      include_dirs=['commotion_client'],
#      ext_modules=[Extension("Commotion Client", ['commotion_client'])],
      url="commotionwireless.net",
      license="Affero General Public License V3 (AGPLv3)",
      executables = [exe],
      options = {"build_exe":{"include_files": [(assets_file, "commotion_assets_rc.py")]}}
  )
