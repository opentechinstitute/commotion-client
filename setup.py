#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cx_freeze import setup, Executable
import py2exe


base = "commotion_client"
icon = "assets/images/logo32.png"

#define core packages
core_pkgs = ["utils", "GUI", "assets"]
core_extensions = ["config_editor"]

#add core_extensions to core packages
for ext in core_extensions:
    core_pkgs.append("extensions."+ext)


exe = Executable(
    script="commotion_client.py",
    packages=core_pkgs
    )

setup(name="Commotion Client",
      version="1.0",
      url="commotionwireless.net",
      license="Affero General Public License V3 (AGPLv3)",
      executables = [exe],
      include_files=[os.path.join("assets", "commotion_assets_rc.py")]
      )
