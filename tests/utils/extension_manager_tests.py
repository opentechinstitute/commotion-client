from PyQt4 import QtCore
from PyQt4 import QtGui


import unittest
import re

from commotion_client.utils import extension_manager

class ExtensionSettingsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = QtGui.QApplication([])
        self.ext_mgr = extension_manager.ExtensionManager()
        self.settings = QtCore.QSettings("test_case", "testing_app")
        
    def tearDown(self):
        self.app = None
        self.ext_mgr = None
        self.settings.clear()

class CoreExtensionMgrTestCase(unittest.TestCase):

    def setUp(self):
        self.app = QtGui.QApplication([])
        self.ext_mgr = extension_manager.ExtensionManager()
        
    def tearDown(self):
        self.app = None
        self.ext_mgr = None
        
class LoadSettings(ExtensionSettingsTestCase):
    """
    Functions Covered:
      load_all
    """

    def test_load_all_settings(self):
        """Test that settings are saved upon running load_all."""
        #Test that there are no extensions loaded
        count = self.settings.allKeys()
        assertIs(type(count), int)
        assertEquals(count, 0)
        #Load extensions
        loaded = self.ext_mgr.load_all()
        #load_all returns extensions that are loaded
        assertIsNot(loaded, False)
        #Check that some extensions were added to settings
        post_count = self.settings.allKeys()
        assertIs(type(count), int)
        assertGreater(count, 0)
        
    def test_load_all_core_ext(self):
        """Test that all core extension directories are saved upon running load_all."""
        #get all extensions currently loaded
        global_ext = QtCore.QDir(self.ext_mgr.extension_dir['global']).files(QtCore.QDir.AllDirs|QtCore.QDir.NoDotAndDotDot)
        loaded = self.ext_mgr.load_all()
        self.settings.beginGroup("extensions")
        k = self.settings.AllKeys()
        for ext in global_ext:
            assertTrue(k.contains(ext), "Core extension {0} should have been loaded, but was not.".format(ext))

    def test_load_all_user_ext(self):
        """Test that all user extension directories are saved upon running load_all."""
        #get user extensions
        user_ext = QtCore.QDir(ext_mgr.extension_dir['user']).files(QtCore.QDir.AllDirs|QtCore.QDir.NoDotAndDotDot)
        #If no user extensions exist (which they should not) set the current user directory to the model extension directory.
        if not user_ext.count() > 0:
            main_dir = dirname(os.path.abspath(QtCore.QDir.currentPath()))
            model_directory = os.path.join(main_dir, "tests/models/extensions")
            ext_mgr.extension_dirs['user'] = model_directory
            #refresh user_ext list
            user_ext = QtCore.QDir(ext_mgr.extension_dir['user']).files(QtCore.QDir.AllDirs|QtCore.QDir.NoDotAndDotDot)
        loaded = self.ext_mgr.load_all()
        self.settings.beginGroup("extensions")
        k = self.settings.AllKeys()
        for ext in user_ext:
            assertTrue(k.contains(ext), "Extension {0} should have been loaded, but was not.".format(ext))

class InitTestCase(CoreExtensionMgrTestCase):

    def test_init(self):
        #TODO:  TEST THESE
        fail("test not implemented")
        ext_mgr.log = False
        ext_mgr.extensions = False
        ext_mgr.translate = False
        ext_mgr.config_values = False
        ext_mgr.extension_dir = False

class FileSystemManagement(CoreExtensionMgrTestCase):

    
    
