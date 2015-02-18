# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import mock
import unittest

from mock import mock_open
from yamlsettings import load, load_all, save, save_all, update_from_env, update_from_file

from . import builtin_module, path_override, open_override, isfile_override


class YamlDictTestCase(unittest.TestCase):

    def setUp(self):
        # Patch open related functions.
        open_patcher = mock.patch('{}.open'.format(builtin_module))
        open_patch = open_patcher.start()
        open_patch.side_effect = open_override
        self.addCleanup(open_patcher.stop)

        path_patcher = mock.patch('os.path.exists')
        path_patch = path_patcher.start()
        path_patch.side_effect = path_override
        self.addCleanup(path_patcher.stop)

        isfile_patcher = mock.patch('os.path.isfile')
        isfile_patch = isfile_patcher.start()
        isfile_patch.side_effect = isfile_override
        self.addCleanup(isfile_patcher.stop)

    def test_load_single_file(self):
        test_defaults = load('defaults.yml')
        self.assertEqual(test_defaults.config.greet, 'Hello')
        self.assertEqual(test_defaults.config.leave, 'Goodbye')
        self.assertEqual(test_defaults.config.secret, 'I have no secrets')
        self.assertEqual(test_defaults.config.meaning, 42)

    def test_load_first_found(self):
        test_settings = load(['missing.yml', 'defaults.yml', 'settings.yml'])
        self.assertEqual(test_settings.config.greet, 'Hello')
        self.assertEqual(test_settings.config.leave, 'Goodbye')
        self.assertEqual(test_settings.config.secret, 'I have no secrets')
        self.assertEqual(test_settings.config.meaning, 42)

    @mock.patch.dict('os.environ', {
        'CONFIG_MEANING': '42.42',
        'CONFIG_SECRET': '!!python/object/apply:tests.get_secret []'})
    def test_load_with_envs(self):
        test_defaults = load('defaults.yml')
        update_from_env(test_defaults)
        self.assertEqual(test_defaults.config.greet, 'Hello')
        self.assertEqual(test_defaults.config.leave, 'Goodbye')
        self.assertEqual(test_defaults.config.secret, 's3cr3tz')
        self.assertEqual(test_defaults.config.meaning, 42.42)

    def test_update(self):
        test_settings = load('defaults.yml')
        test_settings.update(load('settings.yml'))
        self.assertEqual(test_settings.config.greet, 'Hello')
        self.assertEqual(test_settings.config.leave, 'Goodbye')
        self.assertEqual(test_settings.config.secret, 'I have many secrets')
        self.assertEqual(test_settings.config.meaning, 42)
        self.assertEqual(test_settings.config_excited.greet, "Whazzzzup!")

    def test_rebase(self):
        test_settings = load('settings.yml')
        test_settings.rebase(load('defaults.yml'))
        self.assertEqual(test_settings.config.greet, 'Hello')
        self.assertEqual(test_settings.config.leave, 'Goodbye')
        self.assertEqual(test_settings.config.secret, 'I have many secrets')
        self.assertEqual(test_settings.config.meaning, 42)
        self.assertEqual(test_settings.config_excited.greet, "Whazzzzup!")

    def test_limit(self):
        test_settings = load('settings.yml')
        test_settings.limit(['config'])
        self.assertEqual(list(test_settings), ['config'])

    def test_clone_changes_isolated(self):
        test_settings = load('defaults.yml')
        test_clone = test_settings.clone()
        test_settings.config.greet = "Hodo"
        self.assertNotEqual(test_settings.config.greet,
                            test_clone.config.greet)

    def test_load_all(self):
        section_count = 0
        for cur_yml in load_all('fancy.yml'):
            if section_count is 0:
                self.assertEqual(cur_yml.test.id1.name, 'hi')
                self.assertEqual(cur_yml.test.test[2].sub_test.a, 10)
                self.assertEqual(cur_yml.test.test[2].sub_test.b.name, 'hi')
            elif section_count is 1:
                self.assertEqual(cur_yml.test_2.test2.message, 'same here')
            elif section_count is 2:
                self.assertEqual(cur_yml.test_3.test.name, 'Hello')
            section_count += 1
        self.assertEqual(section_count, 3)

    def test_save_all(self):
        cur_ymls = load_all('fancy.yml')
        m = mock_open()
        with mock.patch('{}.open'.format(builtin_module), m, create=True):
            save_all(cur_ymls, 'out.yml')
        m.assert_called_once_with('out.yml', 'w')

    def test_update_from_file(self):
        test_defaults = load('defaults.yml')
        update_from_file(test_defaults, 'settings.yml')
        self.assertEqual(test_defaults.config.secret, 'I have many secrets')
        self.assertEqual(list(test_defaults), ['config'])

    @mock.patch.dict('os.environ', {
        'TEST_GREETING_INTRODUCE': 'The environment says hello!',
        'TEST_DICT_VAR_MIX_B': 'Goodbye Variable',
    })
    def test_variable_override(self):
        test_settings = load("single_fancy.yml")
        update_from_env(test_settings)
        self.assertEqual(test_settings.test.greeting.introduce,
                         'The environment says hello!')
        self.assertEqual(test_settings.test.dict_var_mix.b,
                         'Goodbye Variable')

    @mock.patch.dict('os.environ', {
        'TEST_CONFIG_DB': 'OurSQL',
    })
    def test_stupid_override(self):
        test_settings = load("stupid.yml")
        update_from_env(test_settings)
        self.assertEqual(test_settings.test.config.db,
                         'OurSQL')
        self.assertEqual(test_settings.test.config_db,
                         'OurSQL')

    @mock.patch.dict('os.environ', {
        'TEST_GREETING_INTRODUCE': 'The environment says hello!',
    })
    def test_file_writing(self):
        test_settings = load("single_fancy.yml")
        update_from_env(test_settings)

        m = mock_open()
        with mock.patch('{}.open'.format(builtin_module), m, create=True):
            with open('current_file.yml', 'w') as h:
                h.write(str(test_settings))

        m.assert_called_once_with('current_file.yml', 'w')
        handle = m()
        handle.write.assert_called_with(
            'test:\n'
            '  id1: &id001\n'
            '    name: hi\n'
            '  id2: &id002\n'
            '    name: hello\n'
            '  var_list:\n'
            '  - *id001\n'
            '  - *id002\n'
            '  dict_var_mix:\n'
            '    a: 10\n'
            '    b: *id001\n'
            '  dict_with_list:\n'
            '    name: jin\n'
            '    set:\n'
            '    - 1\n'
            '    - 2\n'
            '    - 3\n'
            '  greeting:\n'
            '    introduce: The environment says hello!\n'
            '    part: Till we meet again\n'
            '  crazy:\n'
            '    type: !!python/name:logging.handlers.SysLogHandler \'\'\n'
            '    module: !!python/module:sys \'\'\n'
            '    instance: !!python/object:tests.SoftwareEngineer\n'
            '      name: jin\n'
        )


if __name__ == '__main__':
    unittest.main()
