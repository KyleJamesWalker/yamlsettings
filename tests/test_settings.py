# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import unicode_literals

import json
import unittest.mock as mock
import unittest

from yamlsettings import YamlSettings
from . import builtin_module, path_override, open_override, isfile_override


class YamlSettingsWithSectionsTestCase(unittest.TestCase):

    def setUp(self):
        path_patcher = mock.patch('os.path.exists')
        path_patch = path_patcher.start()
        path_patch.side_effect = path_override
        self.addCleanup(path_patcher.stop)

        isfile_patcher = mock.patch('os.path.isfile')
        isfile_patch = isfile_patcher.start()
        isfile_patch.side_effect = isfile_override
        self.addCleanup(isfile_patcher.stop)

    @mock.patch('{}.open'.format(builtin_module))
    def test_settings_with_sections(self, open_patch):
        open_patch.side_effect = open_override

        test_settings = YamlSettings('defaults.yml', 'settings.yml',
                                     default_section='config')
        # Verify Base Settings
        base_settings = test_settings.get_settings()
        self.assertEqual(base_settings.greet, 'Hello')
        self.assertEqual(base_settings.leave, 'Goodbye')
        self.assertEqual(base_settings.secret, 'I have many secrets')

        # Verify Excited Settings (greet overridden, leave inherits)
        excited_settings = test_settings.get_settings('config_excited')
        self.assertEqual(excited_settings.greet, 'Whazzzzup!')
        self.assertEqual(excited_settings.leave, 'Goodbye')

        # Verify Cool Settings (greet overridden, leave inherits)
        cool_settings = test_settings.get_settings('config_cool')
        self.assertEqual(cool_settings.greet, 'Sup...')
        self.assertEqual(cool_settings.leave, 'Goodbye')

    @mock.patch('{}.open'.format(builtin_module))
    def test_settings_without_sections(self, open_patch):
        open_patch.side_effect = open_override

        test_settings = YamlSettings('defaults_no_sec.yml',
                                     'settings_no_sec.yml')
        base_settings = test_settings.get_settings()
        self.assertEqual(base_settings.config.greet,
                         'Why hello good sir or mam.')
        self.assertEqual(base_settings.config.leave,
                         'Goodbye')

    @mock.patch.dict('os.environ', {'CONFIG_GREET': 'Howdy'})
    @mock.patch('{}.open'.format(builtin_module))
    def test_settings_without_environment(self, open_patch):
        open_patch.side_effect = open_override

        test_settings = YamlSettings('defaults.yml', 'settings.yml',
                                     default_section='config',
                                     override_envs=False)
        base_settings = test_settings.get_settings('config_cool')
        self.assertEqual(base_settings.greet, 'Sup...')
        self.assertEqual(base_settings.leave, 'Goodbye')

    @mock.patch.dict('os.environ', {'CONFIG_GREET': 'Howdy'})
    @mock.patch('{}.open'.format(builtin_module))
    def test_settings_with_environment(self, open_patch):
        open_patch.side_effect = open_override

        test_settings = YamlSettings('defaults.yml', 'settings.yml',
                                     default_section='config')
        base_settings = test_settings.get_settings('config_cool')
        self.assertEqual(base_settings.greet, 'Howdy')
        self.assertEqual(base_settings.leave, 'Goodbye')

    @mock.patch.dict('os.environ', {'CONFIG_GREET': 'Howdy',
                                    'CONFIG_LEAVE': 'Later'})
    @mock.patch('{}.open'.format(builtin_module))
    def test_settings_with_environment_pre(self, open_patch):
        open_patch.side_effect = open_override

        test_settings = YamlSettings('defaults.yml', 'settings.yml',
                                     default_section='config',
                                     envs_override_defaults_only=True)
        base_settings = test_settings.get_settings('config_cool')
        self.assertEqual(base_settings.greet, 'Sup...')
        self.assertEqual(base_settings.leave, 'Later')

    @mock.patch.dict('os.environ', {'CONFIG_GREET': 'Howdy'})
    @mock.patch('{}.open'.format(builtin_module))
    def test_settings_without_sections_or_environment(self, open_patch):
        open_patch.side_effect = open_override

        test_settings = YamlSettings('defaults_no_sec.yml',
                                     'settings_no_sec.yml',
                                     override_envs=False)
        base_settings = test_settings.get_settings()
        self.assertEqual(base_settings.config.greet,
                         'Why hello good sir or mam.')
        self.assertEqual(base_settings.config.leave,
                         'Goodbye')

    @mock.patch.dict('os.environ', {'CONFIG_GREET': 'Howdy',
                                    'CONFIG_LEAVE': 'Later'})
    @mock.patch('{}.open'.format(builtin_module))
    def test_settings_without_sections_with_environment(self, open_patch):
        open_patch.side_effect = open_override

        test_settings = YamlSettings('defaults_no_sec.yml',
                                     'settings_no_sec.yml',
                                     override_envs=True)
        base_settings = test_settings.get_settings()
        self.assertEqual(base_settings.config.greet, 'Howdy')
        self.assertEqual(base_settings.config.leave, 'Later')

    @mock.patch.dict('os.environ', {'CONFIG_GREET': 'Howdy',
                                    'CONFIG_LEAVE': 'Later'})
    @mock.patch('{}.open'.format(builtin_module))
    def test_settings_without_sections_with_environment_pre(self, open_patch):
        open_patch.side_effect = open_override

        test_settings = YamlSettings('defaults_no_sec.yml',
                                     'settings_no_sec.yml',
                                     override_envs=True,
                                     envs_override_defaults_only=True)
        base_settings = test_settings.get_settings()
        self.assertEqual(base_settings.config.greet,
                         'Why hello good sir or mam.')
        self.assertEqual(base_settings.config.leave,
                         'Later')

    @mock.patch('{}.open'.format(builtin_module))
    def test_settings_without_required_override_file(self, open_patch):
        open_patch.side_effect = open_override

        self.assertRaises(IOError, YamlSettings, 'defaults.yml',
                          'no_settings.yml', override_required=True)

    @mock.patch('{}.open'.format(builtin_module))
    def test_settings_without_optional_override_file(self, open_patch):
        open_patch.side_effect = open_override

        test_settings = YamlSettings('defaults.yml',
                                     'no_settings.yml',
                                     override_required=False)
        base_settings = test_settings.get_settings()
        self.assertEqual(base_settings.config.greet, 'Hello')
        self.assertEqual(base_settings.config.leave, 'Goodbye')

    @mock.patch('{}.open'.format(builtin_module))
    def test_settings_bad_default_section(self, open_patch):
        open_patch.side_effect = open_override

        self.assertRaises(KeyError, YamlSettings, 'defaults.yml',
                          'settings.yml', default_section='configuration')

    @mock.patch('{}.open'.format(builtin_module))
    def test_serialization(self, open_patch):
        open_patch.side_effect = open_override

        test_settings = YamlSettings('defaults.yml', 'settings.yml',
                                     default_section='config')

        base_settings = test_settings.get_settings()

        self.assertEqual(
            dict(base_settings),
            {
                'greet': 'Hello',
                'leave': 'Goodbye',
                'secret': 'I have many secrets',
                'meaning': 42
            }
        )

        self.assertEqual(
            json.dumps(base_settings),
            '{"greet": "Hello", "leave": "Goodbye", '
            '"secret": "I have many secrets", "meaning": 42}'
        )

    def test_all_without_override_file(self):
        pass

    def test_single_section_load(self):
        pass

    def test_callback_support(self):
        # Might add at least one configurable callback
        # Shell example
        def build_connections(path, format):
            search_path = path
            path_format = format

            def callback(settings):
                # Do stuff with search_path and path_format
                settings[search_path] = path_format

            return callback
        pass

if __name__ == '__main__':
    unittest.main()
