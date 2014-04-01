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
zip_extensions.py

This module takes all extensions in the commotion_client/extension/ directory and prepares them as commotion packages.
"""

import zipfile
import os

def get_extensions(main_directory):
    """Gets all extension sub-directories within a given directory.

    Args:
      main_directory (string): The path to the main extension directory to check for extensions within.
    
    Returns:
      A list containing of all of the extension directories within the main_directory.
        ['path/to/extension01', 'path/to/extension02', 'path/to/extension03']
    """
    #if not a directory... shame on them
    if not os.path.isdir(main_directory):
                raise NotADirectoryError("{0} is not a directory.".format(main_directory))
    extensions = []
    #walk the directory and add all sub-directories as extensions.
    for dirpath, dirnames, filenames in os.walk(main_directory):
        for directory in dirnames:
            #don't add pycache if it exists
            if directory != "__pycache__":
                extensions.append(os.path.join(dirpath, directory))
        break
    return extensions

def zip_extension(source, destination):
    """short description
    
    long description
    
    Args:
      source (string): The relative path to the source directory which contains the extension files.
      destination (string): The relative path to the destination directory where the zipfile will be placed.
    
    """
    #if extension is not a directory then this won't work
    if not os.path.isdir(source):
                raise NotADirectoryError("{0} is not a directory.".format(main_directory))
    extension_name = os.path.basename(os.path.normpath(source))
    to_zip = []
    #walk the full extension directory.
    for dirpath, dirnames, filenames in os.walk(source):
        if "__init__.py" not in filenames:
            touch_init(dirpath)
            to_zip.append(os.path.join(dirpath, "__init__.py"))
        for zip_file in filenames:
            to_zip.append(os.path.join(dirpath, zip_file))
    #create and populate zipfile
    with zipfile.ZipFile(os.path.join(destination, extension_name), 'a') as compressed_extension:
        for ready_file in to_zip:
            extension_path = os.path.relpath(ready_file, source)
            compressed_extension.write(ready_file, extension_path)
        

def touch_init(extension_dir):
    """ Touches the init file in each directory of an extension to make sure it exists.
    
    Args:
      extension_dir (string): The path to a directory an __init__.py file should exist within.
    """
    with open(os.path.join(extension_dir, "__init__.py"), 'a') as f:
        os.utime("__init__.py")    
    
def zip_all():
    """Zip's all extensions in the main commotion_client directory and moves them into the build directories resources folder.
    """
    main_directory = os.path.join("commotion_client", "extensions")
    zip_directory = os.path.join("build", "resources")
    extension_paths = get_extensions(main_directory)
    for extension_directory in extension_paths:
        zip_extension(extension_directory, zip_directory)

if __name__ == "__main__":
    zip_all()
