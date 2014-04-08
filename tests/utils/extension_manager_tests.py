from PyQt4 import QtCore
from PyQt4 import QtGui


import unittest
import re
import os

from commotion_client.utils import extension_manager

class ExtensionSettingsTestCase(unittest.TestCase):

    def setUp(self):
        self.app = QtGui.QApplication([])
        self.app.setOrganizationName("test_case");
        self.app.setApplicationName("testing_app");
        self.ext_mgr = extension_manager.ExtensionManager()
        
        
    def tearDown(self):
        self.app.deleteLater()
        del self.app
        self.app = None
        self.ext_mgr.user_settings.clear()
        self.ext_mgr = None
        #Delete everything under tests/temp
        for root, dirs, files in os.walk(os.path.abspath("tests/temp/"), topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        
class LoadConfigSettings(ExtensionSettingsTestCase):
    """
    Functions Covered:
      load_all
      init_extension_config
      
    """
    def test_load_core_ext(self):
        """Test that all core extension directories are loaded upon running load_core."""
        #get all extensions currently loaded
        self.ext_mgr.libraries['core'] = os.path.abspath("tests/mock/extensions/")
        self.ext_mgr.libraries['global'] = os.path.abspath("tests/temp/")
        global_dir = QtCore.QDir(self.ext_mgr.libraries['global'])
        global_exts = global_dir.entryList(QtCore.QDir.AllDirs|QtCore.QDir.NoDotAndDotDot)
        loaded = self.ext_mgr.load_core()
        self.ext_mgr.user_settings.beginGroup("extensions")
        k = self.ext_mgr.user_settings.allKeys()
        for ext in global_exts:
            contains = (ext in k)
            self.assertTrue(contains, "Core extension {0} should have been loaded, but was not.".format(ext))

    def test_init_extension_config(self):
        """Test that init extension config properly handles the various use cases."""
        #ext_type MUST be core|global|user
        with self.assertRaises(ValueError):
            self.ext_mgr.init_extension_config('pineapple')

        #Check for an empty directory.
        self.ext_mgr.libraries['user'] = os.path.abspath("tests/temp/")
        self.ext_mgr.init_extension_config('user')
        self.assertFalse(self.ext_mgr.extensions['user'].has_configs())
        self.ext_mgr.extensions['user'] = None

        #populate with populated directory
        self.ext_mgr.libraries['user'] = os.path.abspath("tests/mock/extensions/")
        self.ext_mgr.init_extension_config('user')
        self.assertTrue(self.ext_mgr.extensions['user'].has_configs())
        self.ext_mgr.extensions['user'] = None
        
        #check all types on default call
        self.ext_mgr.libraries['user'] = os.path.abspath("tests/mock/extensions/")
        self.ext_mgr.libraries['global'] = os.path.abspath("tests/mock/extensions/")
        self.ext_mgr.libraries['core'] = os.path.abspath("tests/mock/extensions/")
        self.ext_mgr.init_extension_config()
        self.assertTrue(self.ext_mgr.extensions['user'].has_configs())
        self.assertTrue(self.ext_mgr.extensions['global'].has_configs())
        self.assertTrue(self.ext_mgr.extensions['core'].has_configs())
        self.ext_mgr.extensions['user'] = None
        self.ext_mgr.extensions['global'] = None
        self.ext_mgr.extensions['core'] = None        
        
class GetConfigSettings(ExtensionSettingsTestCase):

    def test_get_installed(self):
        """Test that get_installed function properly checks & returns installed extensions."""
        empty_inst = self.ext_mgr.get_installed()
        self.assertEqual(empty_inst, {})
        #add a value to settings
        self.ext_mgr.user_settings.setValue("test/type", "global")
        self.ext_mgr.user_settings.sync()
        one_item = self.ext_mgr.get_installed()
        self.assertEqual(len(one_item), 1)
        self.assertIn("test", one_item)
        self.assertEqual(one_item['test'], 'global')
 
    def test_check_installed(self):
        """Test that get_installed function properly checks & returns if extensions are installed."""
        #test empty first
        self.assertFalse(self.ext_mgr.check_installed())
        self.assertFalse(self.ext_mgr.check_installed("test"))
        #add a value to settings
        self.ext_mgr.user_settings.setValue("test/type", "global")
        self.ext_mgr.user_settings.sync()
        self.assertTrue(self.ext_mgr.check_installed())
        self.assertTrue(self.ext_mgr.check_installed("test"))
        self.assertFalse(self.ext_mgr.check_installed("pineapple"))

class ExtensionLibraries(ExtensionSettingsTestCase):

    def test_init_libraries(self):
        """Tests that the library are created when provided and fail gracefully when not. """

        #init libraries from library defaults
        self.ext_mgr.set_library_defaults()
        user_dir = self.ext_mgr.libraries['user']
        global_dir = self.ext_mgr.libraries['global']
        self.ext_mgr.init_libraries()
        self.assertTrue(os.path.isdir(os.path.abspath(user_dir)))
        self.assertTrue(os.path.isdir(os.path.abspath(global_dir)))
        #assert that init libraries works with non-default paths.
        
        self.ext_mgr.libraries['user'] = os.path.abspath("tests/temp/oneLevel/")
        self.ext_mgr.libraries['global'] = os.path.abspath("tests/temp/oneLevel/twoLevel/")
        self.ext_mgr.init_libraries()
        self.assertTrue(os.path.isdir(os.path.abspath("tests/temp/oneLevel/twoLevel/")))
        self.assertTrue(os.path.isdir(os.path.abspath("tests/temp/oneLevel/")))

    def test_install_loaded(self):
        """ Tests that all loaded, and currently uninstalled, libraries are installed"""
        #setup directory with extension
        self.ext_mgr.libraries['user'] = os.path.abspath("tests/mock/extensions/")
        #setup empty directory
        self.ext_mgr.libraries['global'] = os.path.abspath("tests/temp/global/")
        #setup paths and configs
        self.ext_mgr.init_libraries()
        self.ext_mgr.init_extension_config("user")
        self.ext_mgr.init_extension_config("global")
        #run function
        user_installed = self.ext_mgr.install_loaded()
        self.assertEqual(user_installed, ["config_editor"])

        #Test that the mock extension was loaded
        self.assertTrue(self.ext_mgr.check_installed("config_editor"))
        #Test that ONLY the mock extension was loaded and in the user section
        one_item_only = self.ext_mgr.get_installed()
        self.assertEqual(len(one_item_only), 1)
        self.assertIn("config_editor", one_item_only)
        self.assertEqual(one_item_only['config_editor'], 'user')
        #Test that the config_manager was "initialized".
        initialized = self.ext_mgr.get_extension_from_property("initialized", True)
        self.assertIn("config_editor", initialized)
        #test not initialize an existing, intialized, extension

    def test_get_extension_from_property(self):
        #setup directory with extension
        self.ext_mgr.libraries['user'] = os.path.abspath("tests/mock/extensions/")
        #setup config
        self.ext_mgr.init_extension_config("user")
        #Install loaded configs
        self.ext_mgr.install_loaded()
        
        has_value = self.ext_mgr.get_extension_from_property("menu_item", "Commotion Config File Editor")
        self.assertIn("config_editor", has_value)
        #key MUST be one of the approved keys
        with self.assertRaises(KeyError):
            self.ext_mgr.get_extension_from_property('pineapple', "made_of_fire")
        does_not_have = self.ext_mgr.get_extension_from_property("menu_item", "I am not called this")
        self.assertNotIn("config_editor", does_not_have)
        


        
    def test_get_property(self):
        self.fail("This test for function get_property (line 302) needs to be implemented")
        
    def test_get_type(self):
        self.fail("This test for function get_type (line 333) needs to be implemented... but this function may actually need to be removed too.")
        
    def test_load_user_interface(self):
        self.fail("This test for function load_user_interface (line 359) needs to be implemented")

    def test_import_extension(self):
        self.fail("This test for function import_extension (line 376) needs to be implemented")

    def test_load_settings(self):
        self.fail("This test for function load_settings (line 391) needs to be implemented")

    def test_remove_extension_settings(self):
        self.fail("This test for function remove_extension_settings (line 429) needs to be implemented... or moved to a settings module that will eventually handle all the encrypted stuff... but that actually might be better done outside of this.")

    def test_save_settings(self):
        self.fail("This test for function save_settings (line 444) needs to be implemented")

    def test_save_extension(self):
        self.fail("This test for function save_extension (line 561) needs to be implemented")
        
    def test_add_config(self):
        self.fail("This test for function add_config (line 670) needs to be implemented... but the function should actually just be removed.")
        
    def test_remove_config(self):
        self.fail("This test for function remove_config (line 699) needs to be implemented... but the function should actually just be removed.")

    def test_unpack_extension(self):
        self.fail("This test for function unpack_extension (line 723) needs to be implemented... but that function actually MUST be removed since we are not unpacking extension objects")
        
    def test_save_unpacked_extension(self):
        self.fail("This test for function save_unpacked_extension (line 743) needs to be implemented... but that function actually MUST be removed since we are not unpacking extension objects")

class ConfigManagerTests(unittest.TestCase):

    #Create a new setUp and CleanUP set of functions for these configManager tests

    def test_init(self):
        self.fail("This test for the init function (line 788) needs to be implemented")

    def test_has_configs(self):
        self.fail("This test for function has_configs (line 806) needs to be implemented")

    def test_find(self):
        self.fail("This test for function find (line 817) needs to be implemented")

    def test_get_path(self):
        self.fail("This test for function get_paths (line 838) needs to be implemented")
        
    def test_get(self):
        self.fail("This test for function get (line 881) needs to be implemented")
        
    def test_load(self):
        self.fail("This test for function load (line 899) needs to be implemented")

