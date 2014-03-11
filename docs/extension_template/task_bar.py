#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
task_bar

The task bar for the extension template.

@brief The object that contains the custom task-bar. If not set and a "taskbar" class is not found in the file listed under the "main" option the default taskbar will be implemented.

@note This template ONLY includes the objects for the "task bar" component of the extension template. The other components can be found in their respective locations.

"""

#Standard Library Imports
import logging

#PyQt imports
from PyQt4 import QtCore
from PyQt4 import QtGui

#import python modules created by qtDesigner and converted using pyuic4
from GUI import task_bar


class TaskBar(task_bar.TaskBar):
    """
    
    """

