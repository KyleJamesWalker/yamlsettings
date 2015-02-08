# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import mock
import unittest

from yamlsettings import load, update_from_env
from yamlsettings.yamldict import load_all

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
        'CONFIG_SECRET': '!!python/object/apply:tests.get_secret {args: []}'})
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

    def test_clone_changes_isolated(self):
        test_settings = load('defaults.yml')
        test_clone = test_settings.clone()
        test_settings.config.greet = "Hodo"
        self.assertNotEqual(test_settings.config.greet,
                            test_clone.config.greet)

    def test_load_all(self):
        section_count = 0
        for cur_yml in load_all(open('fancy.yml')):
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

if __name__ == '__main__':
    unittest.main()
