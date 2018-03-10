"""Helper functions

"""
# -*- coding: utf-8 -*-
from __future__ import print_function

import os

from yamlsettings import yamldict
from yamlsettings.extensions import registry


def save(yaml_dict, filepath):
    '''
    Save YAML settings to the specified file path.
    '''
    yamldict.dump(yaml_dict, open(filepath, 'w'), default_flow_style=False)


def save_all(yaml_dicts, filepath):
    '''
    Save *all* YAML settings to the specified file path.
    '''
    yamldict.dump_all(yaml_dicts, open(filepath, 'w'),
                      default_flow_style=False)


def update_from_file(yaml_dict, filepaths):
    '''
    Override YAML settings with loaded values from filepaths.

        - File paths in the list gets the priority by their orders of the list.
    '''
    # load YAML settings with only fields in yaml_dict
    yaml_dict.update(registry.load(filepaths, list(yaml_dict)))


def update_from_env(yaml_dict, prefix=None):
    '''
    Override YAML settings with values from the environment variables.

        - The letter '_' is delimit the hierarchy of the YAML settings such
          that the value of 'config.databases.local' will be overridden
          by CONFIG_DATABASES_LOCAL.
    '''
    prefix = prefix or ""

    def _set_env_var(path, node):
        env_path = "{0}{1}{2}".format(
            prefix.upper(),
            '_' if prefix else '',
            '_'.join([str(key).upper() for key in path])
        )
        env_val = os.environ.get(env_path, None)
        if env_val is not None:
            # convert the value to a YAML-defined type
            env_dict = yamldict.load('val: {0}'.format(env_val))
            return env_dict.val
        else:
            return None

    # traverse yaml_dict with the callback function
    yaml_dict.traverse(_set_env_var)


class YamlSettings(object):
    """Deprecated: Old helper class to load settings in a opinionated way.

    It's recommended to write or use an opinionated extension now.

    """
    def __init__(self, default_settings, override_settings, override_envs=True,
                 default_section=None, cur_section=None,
                 param_callback=None, override_required=False,
                 envs_override_defaults_only=False,
                 single_section_load=False):
        defaults = registry.load(default_settings)

        if override_envs and envs_override_defaults_only:
            if default_section:
                prefix = default_section
                section = defaults[default_section]
            else:
                prefix = ""
                section = defaults
            update_from_env(section, prefix)
        self.cur_section = default_section

        if default_section is None:
            # No section support simply update with overrides
            self.settings = defaults
            try:
                # WAS:
                # self.settings.update_yaml(override_settings)
                self.settings.update(registry.load(override_settings))
            except IOError:
                if override_required:
                    raise
            if override_envs and not envs_override_defaults_only:
                update_from_env(self.settings, "")
        else:
            # Load Overrides first and merge with defaults
            try:
                self.settings = registry.load(override_settings)
            except IOError:
                if override_required:
                    raise
                # Note this will copy to itself right now, but
                # will allows for simpler logic to get environment
                # variables to work
                self.settings = defaults

            for cur_section in self.settings:
                cur = self.settings[cur_section]
                cur.rebase(defaults[self.cur_section])

                if override_envs and not envs_override_defaults_only:
                    update_from_env(cur, default_section)

            # Make sure default section is created
            if default_section not in self.settings:
                self.settings[default_section] = defaults[default_section]
                if override_envs and not envs_override_defaults_only:
                    update_from_env(self.settings[default_section],
                                    default_section)

    def get_settings(self, section_name=None):
        if section_name is None:
            section_name = self.cur_section

        if section_name is None:
            return self.settings
        else:
            return self.settings[section_name]
