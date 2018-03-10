#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='yamlsettings-example',
    version='1.0.0',
    author='Kyle Walker',
    author_email='KyleJamesWalker@gmail.com',
    description='Quick Example',
    py_modules=['yamlsettings_example'],
    entry_points={
        'yamlsettings10': [
            'ext = yamlsettings_example:ZxcExtension',
        ],
    },
)
