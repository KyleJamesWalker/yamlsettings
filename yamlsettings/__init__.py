# -*- coding: utf-8 -*-
from __future__ import print_function

import os

from yamlsettings import yamldict


def _locate_file(filepaths):
    '''
    Locate settings file from list of filepaths.
    '''
    if not isinstance(filepaths, list) and not isinstance(filepaths, tuple):
        filepaths = [filepaths]
    for filepath in filepaths:
        filepath = os.path.expanduser(filepath)
        if os.path.isfile(filepath):
            break
    else:
        if len(filepaths) > 1:
            raise IOError("unable to locate the settings file from:\n{}".
                          format('\n'.join(filepaths)))
        else:
            raise IOError("unable to locate the settings file from: {}".
                          format(filepaths))
    return filepath


def load(filepaths, fields=[]):
    '''
    Load YAML settings from a list of file paths given.

        - File paths in the list gets the priority by their orders
          of the list.
        - If fields are set, only the selected fields are loaded in the
          returned object. For example, fields=['users', 'hosts'] will
          eliminate all of the other loaded fields except for them.
    '''
    filepath = _locate_file(filepaths)

    # TODO:
    # Add support to load the selected fields only.
    # It could take some time if you had a very large amount of fields.
    # Currently, all settings are loaded and then pruned out.
    # --------------------------------------------
    # load settings into a YAMLDict object
    yaml_dict = yamldict.load(open(filepath))
    # if set, limit the YAMLDict object to only the selected fields
    if fields:
        yaml_dict.limit(fields)
    # --------------------------------------------

    # return YAMLDict object
    return yaml_dict


def load_all(filepaths):
    '''
    Load *all* YAML settings from a list of file paths given.

        - File paths in the list gets the priority by their orders
          of the list.
    '''
    filepath = _locate_file(filepaths)

    # load all settings into YAMLDict objects
    yaml_series = yamldict.load_all(open(filepath))
    yaml_dicts = []
    for yaml_dict in yaml_series:
        yaml_dicts.append(yaml_dict)
    # return YAMLDict objects
    return yaml_dicts


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
    yaml_dict.update(load(filepaths, list(yaml_dict)))


def update_from_env(yaml_dict, prefix=""):
    '''
    Override YAML settings with values from the environment variables.

        - The letter '_' is delimit the hierarchy of the YAML settings such
          that the value of 'config.databases.local' will be overridden
          by CONFIG_DATABASES_LOCAL.
    '''
    def _set_env_var(path, node):
        env_path = "{}{}{}".format(
            prefix.upper(),
            '_' if prefix else '',
            '_'.join([str(key).upper() for key in path])
        )
        env_val = os.environ.get(env_path, None)
        if env_val is not None:
            # convert the value to a YAML-defined type
            env_dict = yamldict.load('val: {}'.format(env_val))
            return env_dict.val
        else:
            return None

    # traverse yaml_dict with the callback function
    yaml_dict.traverse(_set_env_var)


class YamlSettings(object):
    ''' Note you can easily get the same effect, with more flexibility
        by using the functions above directly.
    '''
    def __init__(self, default_settings, override_settings, override_envs=True,
                 default_section=None, cur_section=None,
                 param_callback=None, override_required=False,
                 envs_override_defaults_only=False,
                 single_section_load=False):
        defaults = load(default_settings)

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
                self.settings.update(load(override_settings))
            except IOError:
                if override_required:
                    raise
            if override_envs and not envs_override_defaults_only:
                update_from_env(self.settings, "")
        else:
            # Load Overrides first and merge with defaults
            try:
                self.settings = load(override_settings)
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
