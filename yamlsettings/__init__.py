# -*- coding: utf-8 -*-
from __future__ import print_function

import os

import yamldict
from yamldict import YAMLDict, YAMLDictLoader


def load(filepaths, fields=[]):
    '''
    Load YAML settings from a list of file paths given.

        - File paths in the list gets the priority by their orders of the list.
        - if fields are set, only the selected fields are loaded in the returned object.
          For example, fields=['users', 'hosts'] will eliminate all of the other loaded fields except for them.
    '''
    # locate settings file from list of filepaths
    if not isinstance(filepaths, list) and not isinstance(filepaths, tuple):
        filepaths = [filepaths]
    for filepath in filepaths:
        filepath = os.path.expanduser(filepath)
        if os.path.isfile(filepath):
            break
    else:
        if len(filepaths) > 1:
            raise IOError("unable to locate the settings file from:\n{}".format('\n'.join(filepaths)))
        else:
            raise IOError("unable to locate the settings file from: {}".format(filepaths))

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


def update_from_env(yaml_dict):
    '''
    Override YAML settings with values from the environment variables.

        - The letter '_' is delimit the hierarchy of the YAML settings such that
          the value of 'config.databases.local' will be overriden by CONFIG_DATABASES_LOCAL.
    '''
    # get the flat structure from which environment variables are retrieved
    yaml_flat = yaml_dict.flat()

    # update settings
    for path, value in yaml_flat:
        # get value from environment settings
        env_path = [str(key).upper() for key in path]
        env_val = os.environ.get('_'.join(env_path), None)
        if env_val is not None:
            # replace value of the current settings path
            yaml_dict.inflate([(path, env_val)])


def update_from_callback(yaml_dict, callback):
    '''
    Override YAML settings with retrun values from the specified callback function.

        - callback function must be as follows:
            def callback(path, value):
                ...
                do some processing
                ...
                return value

            'value' contains setting value while 'path' contains the flattened path to the value.
    '''
    # get the flat structure from which environment variables are retrieved
    yaml_flat = yaml_dict.flat()

    # update settings
    for path, value in yaml_flat:
        # call the callback function
        ret_val = callback(path, value)
        if ret_val is not None:
            # replace value of the current settings path
            yaml_dict.inflate([(path, ret_val)])
