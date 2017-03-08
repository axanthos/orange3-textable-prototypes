#!/usr/bin/env python

""" File setup.py

Copyright 2016 University of Lausanne (aris.xanthos@unil.ch)

This file is part of the Orange3 Textable Prototypes extension to 
Orange Canvas.

Orange3 Textable Prototypes is free software: you can redistribute it 
and/or modify it under the terms of the GNU General Public License as published 
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Orange3 Textable Prototypes is distributed in the hope that it will be 
useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Orange3 Textable Prototypes. If not, see 
http://www.gnu.org/licenses
"""

from __future__ import unicode_literals

from os import path, walk
import sys

if sys.version_info < (3, ):
    raise RuntimeError("Orange3-Textable-Prototypes requires Python 3")

from setuptools import setup, find_packages

__version__ = "0.1"   # file version

NAME = 'Orange3-Textable-Prototypes'
DOCUMENTATION_NAME = 'Textable Prototypes'

VERSION = '0.1'  # package version

DESCRIPTION = 'Additional widgets for the Textable add-on to Orange 3.'
LONG_DESCRIPTION = open(
    path.join(path.dirname(__file__), 'README.md')
).read()
AUTHOR = 'University of Lausanne'
AUTHOR_EMAIL = 'aris.xanthos@unil.ch'
URL = 'https://github.com/axanthos/orange3-textable-prototypes'
DOWNLOAD_URL = 'https://github.com/axanthos/orange3-textable-prototypes/archive/master.zip'
LICENSE = 'GPLv3'

KEYWORDS = (
    'text mining',
    'text analysis',
    'textable',
    'orange3',
    'orange3 add-on',
)

CLASSIFIERS = (
    'Development Status :: 3 - Alpha',
    'Environment :: X11 Applications :: Qt',
    'Environment :: Plugins',
    'Programming Language :: Python :: 3 :: Only',
    'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
    'Operating System :: OS Independent',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Text Processing :: General',
    'Topic :: Text Processing :: Linguistic',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
)

PACKAGES = find_packages()

PACKAGE_DATA = {
    'orangecontrib.textable_prototypes': ['tutorials/*.ows'],
    'orangecontrib.textable_prototypes.widgets': [
        'icons/*', 
        'cached_title_list',
    ],
}

DATA_FILES = [
    # Data files that will be installed outside site-packages folder
]

INSTALL_REQUIRES = (
    'Orange3 >= 3.3.8',
    'setuptools',
    'future',
    'LTTL >= 2.0.1',
    'Orange3-Textable >= 3.0b0',
),

EXTRAS_REQUIRE = {
}

DEPENDENCY_LINKS = (
)

ENTRY_POINTS = {
    'orange3.addon': (
        'textable_prototypes = orangecontrib.textable_prototypes',
    ),
    'orange.widgets.tutorials': (
        'textable_prototypes_tutorials = orangecontrib.textable_prototypes.tutorials',
    ),
    'orange.widgets': (
        'Textable Prototypes = orangecontrib.textable_prototypes.widgets',
    ),
    "orange.canvas.help": (
        'html-index = orangecontrib.textable_prototypes:WIDGET_HELP_PATH',
    ),
}

NAMESPACE_PACKAGES = ["orangecontrib"]

TEST_SUITE = "orangecontrib.textable_prototypes.tests.suite"

def include_documentation(local_dir, install_dir):
    global DATA_FILES
    if 'bdist_wheel' in sys.argv and not path.exists(local_dir):
        print("Directory '{}' does not exist. "
              "Please build documentation before running bdist_wheel."
              .format(path.abspath(local_dir)))
        sys.exit(0)

    doc_files = []
    for dirpath, dirs, files in walk(local_dir):
        doc_files.append((dirpath.replace(local_dir, install_dir),
                          [path.join(dirpath, f) for f in files]))
    DATA_FILES.extend(doc_files)

if __name__ == '__main__':
    include_documentation('doc/_build', 'help/orange3-textable-prototypes')
    setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        license=LICENSE,
        packages=PACKAGES,
        package_data=PACKAGE_DATA,
        data_files=DATA_FILES,
        install_requires=INSTALL_REQUIRES,
        entry_points=ENTRY_POINTS,
        keywords=KEYWORDS,
        namespace_packages=NAMESPACE_PACKAGES,
        test_suite=TEST_SUITE,
        include_package_data=True,
        zip_safe=False,
    )
