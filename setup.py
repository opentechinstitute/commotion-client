#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from distutils.core import setup
import py2exe

setup(name="Commotion Client",
      version="1.0",
      url="commotionwireless.net",
      license="Affero General Public License V3 (AGPLv3)",
      platforms="linux",
      packages=['core_extensions', 
                'contrib_extensions'],
      package_dir={'core_extensions': 'commotion_client/extensions/core',
                   'contrib_extensions': 'commotion_client/extensions/contrib'},
      package_data={'core_extensions': ['config_manager'],
                    'contrib_extensions': ['test']},
      )
