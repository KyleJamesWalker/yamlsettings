# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import sys

from io import StringIO

# There has to be a better way to do this, that works with both pythons
if sys.version_info > (3, 0):
    builtin_module = 'builtins'
else:
    builtin_module = '__builtin__'

mock_files = {
    'defaults.yml': (
        '---\n'
        'config:\n'
        '  greet: Hello\n'
        '  leave: Goodbye\n'
        '  secret: I have to secrets\n'
    ),
    'settings.yml': (
        '---\n'
        'config:\n'
        '  secret: I have many secrets\n'
        'config_excited:\n'
        '  greet: Whazzzzup!\n'
        'config_cool:\n'
        '  greet: Sup...\n'
    ),
    'defaults_no_sec.yml': (
        '---\n'
        'config:\n'
        '  greet: Hello\n'
        '  leave: Goodbye\n'
        '  secret: I have to secrets\n'
    ),
    'settings_no_sec.yml': (
        '---\n'
        'config:\n'
        '  greet: Why hello good sir or mam.\n'
    ),
}


def path_override(arg):
    return arg in mock_files.keys()


def open_override(filename):
    mock_file = StringIO()

    try:
        mock_file.write(mock_files[filename])
    except KeyError:
        raise IOError("File Needs Mock")

    mock_file.seek(0)

    return mock_file
