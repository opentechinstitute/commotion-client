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
Unit Tests for commotion_client/utils/extension_manager.py


=== Mock Extension ===
This set of tests uses a mock extension with the following properties.

location: tests/mock/extensions/unit_test_mock

---files in extension archive:---
  * main.py
  * units.py
  * test_bar.py
  * __init__.py
  * test.conf
  * ui/Ui_test.py
  * ui/test.ui

---Config Values---
"name":"mock_test_extension",
"menu_item":"A Mock Testing Object",
"parent":"Testing",
"main":"main",
"settings":"main",
"toolbar":"test_bar",
"tests":"units"


"""


from PyQt4 import QtCore
from PyQt4 import QtGui


import unittest
import re
import os
import sys
import copy

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
        self.assertEqual(user_installed, ["unit_test_mock"])

        #Test that the mock extension was loaded
        self.assertTrue(self.ext_mgr.check_installed("unit_test_mock"))
        #Test that ONLY the mock extension was loaded and in the user section
        one_item_only = self.ext_mgr.get_installed()
        self.assertEqual(len(one_item_only), 1)
        self.assertIn("unit_test_mock", one_item_only)
        self.assertEqual(one_item_only['unit_test_mock'], 'user')
        #Test that the config_manager was "initialized".
        initialized = self.ext_mgr.get_extension_from_property("initialized", True)
        self.assertIn("unit_test_mock", initialized)

    def test_get_extension_from_property(self):
        #setup directory with extension
        self.ext_mgr.libraries['user'] = os.path.abspath("tests/mock/extensions/")
        #setup config
        self.ext_mgr.init_extension_config("user")
        #Install loaded configs
        self.ext_mgr.install_loaded("user")
        
        has_value = self.ext_mgr.get_extension_from_property("menu_item", "A Mock Testing Object")
        self.assertIn("unit_test_mock", has_value)
        #key MUST be one of the approved keys
        with self.assertRaises(KeyError):
            self.ext_mgr.get_extension_from_property('pineapple', "made_of_fire")
        does_not_have = self.ext_mgr.get_extension_from_property("menu_item", "I am not called this")
        self.assertNotIn("unit_test_mock", does_not_have)

        
    def test_get_property(self):
        #setup directory with extension
        self.ext_mgr.libraries['user'] = os.path.abspath("tests/mock/extensions/")
        #setup config
        self.ext_mgr.init_extension_config("user")
        #Install loaded configs
        self.ext_mgr.install_loaded("user")
        #test that values which do exist are correct
        menu_item = self.ext_mgr.get_property("unit_test_mock", "menu_item")
        self.assertEqual(menu_item, "A Mock Testing Object")
        #test that invalid keys are correct
        with self.assertRaises(KeyError):
            self.ext_mgr.get_property("unit_test_mock", "bunnies_per_second")
        #test that valid keys, which don't exist in this extension settings are correct
        #add a false value to the values checked against.
        self.ext_mgr.config_keys.append('pineapple')
        with self.assertRaises(KeyError):
            self.ext_mgr.get_property("unit_test_mock", "pineapple")
        
    def test_load_user_interface(self):
        #Add required extension resources file from mock to path since we are not running it in the bundled state.
        sys.path.append("tests/mock/assets")
        #setup directory with extension
        self.ext_mgr.libraries['user'] = os.path.abspath("tests/mock/extensions/")
        #setup config
        self.ext_mgr.init_extension_config("user")
        #Install loaded configs
        self.ext_mgr.install_loaded("user")
        #test main viewport
        main = self.ext_mgr.load_user_interface("unit_test_mock", "main")
        self.assertTrue(main.is_loaded())
        #test pulling object from "main" file
        settings = self.ext_mgr.load_user_interface("unit_test_mock", "settings")
        self.assertTrue(settings.is_loaded())
        #test pulling object from another file
        toolbar = self.ext_mgr.load_user_interface("unit_test_mock", "toolbar")
        self.assertTrue(settings.is_loaded())
        #test invalid user interface type
        with self.assertRaises(AttributeError):
            self.ext_mgr.load_user_interface("unit_test_mock", "pineapple")
        #reject uninitialized extensions
        self.ext_mgr.user_settings.setValue("unit_test_mock/initialized", False)
        with self.assertRaises(AttributeError):
            self.ext_mgr.load_user_interface("unit_test_mock", "toolbar")

    def test_get_config(self):
        #setup directory with extension
        self.ext_mgr.libraries['user'] = os.path.abspath("tests/mock/extensions/")
        #setup config
        self.ext_mgr.init_extension_config("user")
        #Install loaded configs
        self.ext_mgr.install_loaded("user")
        #test that a full config is returned from a extension
        config = self.ext_mgr.get_config("unit_test_mock")
        correct_vals = {"menu_item":"A Mock Testing Object",
                        "parent":"Testing",
                        "main":"main",
                        'name': 'unit_test_mock',
                        "settings":"main",
                        "toolbar":"test_bar",
                        "tests":"units",
                        "type":"user",
                        "menu_level":10,
                        "initialized":True}
        self.assertDictEqual(config, correct_vals)
        #test that a key error is raised on un-implemented extensions
        with self.assertRaises(KeyError):
            self.ext_mgr.get_config("pineapple")

    def test_reset_settings_group(self):
        #ensure that default is set to extensions
        default = self.ext_mgr.user_settings.group()
        self.assertEqual(default, "extensions")
        #test it works when already in proper group
        self.ext_mgr.reset_settings_group()
        already_there = self.ext_mgr.user_settings.group()
        self.assertEqual(already_there, "extensions")
        
        #create a set of groups nested down a few levels
        self.ext_mgr.user_settings.setValue("one/two/three/four", True)
        #move a level and ensure that .group() shows NOT in extensions
        self.ext_mgr.user_settings.beginGroup("one")
        one_lev = self.ext_mgr.user_settings.group()
        self.assertNotEqual(one_lev, "extensions")
        #Test that it works one group down
        self.ext_mgr.reset_settings_group()
        one_lev_up = self.ext_mgr.user_settings.group()
        self.assertEqual(one_lev_up, "extensions")
        #Move the rest of the way down.
        self.ext_mgr.user_settings.beginGroup("one")
        self.ext_mgr.user_settings.beginGroup("two")
        self.ext_mgr.user_settings.beginGroup("three")
        multi_lev = self.ext_mgr.user_settings.group()
        self.assertNotEqual(multi_lev, "extensions")
        #test it works multiple levels down.
        self.ext_mgr.reset_settings_group()
        multi_lev_up = self.ext_mgr.user_settings.group()
        self.assertEqual(multi_lev_up, "extensions")

    def test_remove_extension_settings(self):
        #setup directory with extension
        self.ext_mgr.libraries['user'] = os.path.abspath("tests/mock/extensions/")
        #setup config
        self.ext_mgr.init_extension_config("user")
        #Install loaded configs
        self.ext_mgr.install_loaded("user")
        #test that a '' string raises an error
        with self.assertRaises(ValueError):
            self.ext_mgr.remove_extension_settings("")
        #remove the "unit_test_mock" extension
        self.ext_mgr.remove_extension_settings("unit_test_mock")
        #test that it no longer exists.
        with self.assertRaises(KeyError):
            self.ext_mgr.get_config("unit_test_mock")
        
    def test_save_settings(self):
        #setup directory with extension
        self.ext_mgr.libraries['user'] = os.path.abspath("tests/mock/extensions/")
        #setup config
        self.ext_mgr.init_extension_config("user")
        #Test config added with proper values
        config = self.ext_mgr.extensions["user"].find("unit_test_mock")
        self.ext_mgr.save_settings(config, "user")
        #Show that the extension group was created
        name = self.ext_mgr.user_settings.childGroups()
        self.assertEqual(name[0], "unit_test_mock")
        #enter group and check values
        self.ext_mgr.user_settings.beginGroup("unit_test_mock")
        keys = self.ext_mgr.user_settings.childKeys()
        for _k in list(config.keys()):
            self.assertIn(_k, keys)
            self.assertEqual(config[_k], self.ext_mgr.user_settings.value(_k))
        #check for type and initialization
        self.assertIn('type', keys)
        self.assertIn("initialized", keys)
        self.ext_mgr.user_settings.endGroup()
        #Check an invalid extension type
        self.assertFalse(self.ext_mgr.save_settings(config, "pinapple"))
        #Check an empty config fails
        self.assertFalse(self.ext_mgr.save_settings({}, "user"))
        #check a incorrect name fails (using longer string than all system's support)
        name_conf = copy.deepcopy(config)
        name_conf['name'] = "s2e" * 250 
        self.assertFalse(self.ext_mgr.save_settings(name_conf, "user"))
        #check that an empty name fails.
        emp_name_conf = copy.deepcopy(config)
        emp_name_conf['name'] = ""
        self.assertFalse(self.ext_mgr.save_settings(emp_name_conf, "user"))
        settings = {'toolbar':'main',
                    'main':None,
                    'settings':'main',
                    'parent':'Extensions',
                    'menu_item':'unit_test_mock',
                    'menu_level':10,
                    'tests':'tests'}
        
        for key in settings.keys():
            conf = copy.deepcopy(config)
            #test invalid value
            conf[key] = "s2e" * 250
            self.assertFalse(self.ext_mgr.save_settings(conf, "user"))
            #test empty
            del(conf[key])
            self.ext_mgr.save_settings(conf, "user")
            self.assertEqual(self.ext_mgr.user_settings.value('unit_test_mock/'+key), settings[key])


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

