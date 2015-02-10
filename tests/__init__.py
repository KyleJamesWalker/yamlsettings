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
        '  secret: I have no secrets\n'
        '  meaning: 42'
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
    'fancy.yml': (
        '---\n'
        'test:\n'
        '  id1: &id001\n'
        '    name: hi\n'
        '  id2: &id002\n'
        '    name: hello\n'
        '  test:\n'
        '    - *id001\n'
        '    - *id002\n'
        '    - sub_test:\n'
        '        a: 10\n'
        '        b: *id001\n'
        '    - sub_tester:\n'
        '        name: jin\n'
        '        set: [1, 2, 3]\n'
        '  test2:\n'
        '    message: hello there\n'
        '---\n'
        'test_2:\n'
        '  test2:\n'
        '    message: same here\n'
        '    type: Test\n'
        '---\n'
        'test_3:\n'
        '  test:\n'
        '    name: Hello\n'
     ),
    'single_fancy.yml': (
        '---\n'
        'test:\n'
        '  id1: &id001\n'
        '    name: hi\n'
        '  id2: &id002\n'
        '    name: hello\n'
        '  var_list:\n'
        '    - *id001\n'
        '    - *id002\n'
        '  dict_var_mix:\n'
        '    a: 10\n'
        '    b: *id001\n'
        '  dict_with_list:\n'
        '    name: jin\n'
        '    set: [1, 2, 3]\n'
        '  greeting:\n'
        '    introduce: Hello there\n'
        '    part: Till we meet again'
    ),
}


def isfile_override(arg):
    return arg in mock_files.keys()


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


def get_secret():
    return "s3cr3tz"
