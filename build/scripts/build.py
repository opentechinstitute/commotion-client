#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import compile_ui
import fnmatch

def clean():
    sourceDir = "commotion_client"
    # Compile .ui files
    print("\nCompiling user interface files ...")
    # step 1: remove old Ui_*.py files
    try:
        for root, _, files in os.walk(sourceDir):
            for file in [f for f in files if fnmatch.fnmatch(f, 'Ui_*.py')]:
                os.remove(os.path.join(root, file))
    except Exception as e:
        sys.exit(e)


def build():
    #compile the forms
    try:
        compile_ui.compileUiFiles()
    except Exception as e:
        sys.exit(e)



if __name__ == "__main__":
    if sys.argv[1] == "clean":
        clean()
    elif sys.argv[1] == "build":
        build()
    else:
        sys.exit("Build.py received an incorrect command line argument.")
