"""YamlSettings Library

"""
# -*- coding: utf-8 -*-
from __future__ import print_function

from yamlsettings import yamldict
from yamlsettings.helpers import (
    save,
    save_all,
    update_from_file,  # Deprecated: TODO: Move out of helpers
    update_from_env,
    YamlSettings,  # Deprecated: TODO: Move out of helpers
)
from yamlsettings.extensions import (
    registry,
    RegistryError,
)

load = registry.load
load_all = registry.load_all

__all__ = [
    'yamldict',
    'load',
    'load_all',
    'save',
    'save_all',
    'update_from_file',
    'update_from_env',
    'YamlSettings',
    'registry',
    'RegistryError',
]
