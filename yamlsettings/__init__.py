# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import six
import yaml
import yaml.constructor

from collections import Mapping, OrderedDict, defaultdict


class YamlSettings(object):
    def __init__(self, default_settings, override_settings, override_envs=True,
                 default_section=None, cur_section=None,
                 param_callback=None, override_required=False,
                 envs_override_defaults_only=False,
                 single_section_load=False):
        defaults = AttrDict.from_yaml(default_settings)

        if override_envs and envs_override_defaults_only:
            if default_section:
                prefix = default_section
                section = defaults[default_section]
            else:
                prefix = ""
                section = defaults
            self._get_env_vars(prefix, section)
        self.cur_section = default_section

        if default_section is None:
            # No section support simply update with overrides
            self.settings = defaults
            try:
                self.settings.update_yaml(override_settings)
            except IOError:
                if override_required:
                    raise
            if override_envs and not envs_override_defaults_only:
                self._get_env_vars("", self.settings)
        else:
            # Load Overrides first and merge with defaults
            try:
                self.settings = AttrDict.from_yaml(override_settings)
            except IOError:
                if override_required:
                    raise
                # Note this will copy to itself right now, but
                # will allows for simpler logic to get environment
                # variables to work
                self.settings = defaults

            for cur_section in self.settings:
                cur = self.settings[cur_section]
                tmp = cur.clone()
                cur.rebase(defaults[self.cur_section])
                cur.update_dict(tmp)
                if override_envs and not envs_override_defaults_only:
                    self._get_env_vars(default_section, cur)

            # Make sure default section is created even
            if default_section not in self.settings:
                self.settings[default_section] = defaults[default_section]
                if override_envs and not envs_override_defaults_only:
                    self._get_env_vars(default_section,
                                       self.settings[default_section])

        #TODO: single_section_load
        # Add support to only load the single requested override, not all
        # aka no get_settings with section support as an option as this
        # could take some time if you had a very large amount of sections.

        #TODO: param_callback
        # Allow detection of special sections, to build for example
        # connection strings
        '''
        # Create DB Connection Strings.
        for cur_db in config[environment].databases:
            try:
                config[environment].databases[cur_db].conn_string = \
                    get_connection_string(config[environment].
                                          databases[cur_db])
            except AttributeError:
                print("Error {} is not a valid database entry".format(cur_db))
        '''

    def get_settings(self, section_name=None):
        if section_name is None:
            section_name = self.cur_section

        if section_name is None:
            return self.settings
        else:
            return self.settings[section_name]

    def _get_env_vars(self, prefix, section):
        for key, val in six.iteritems(section):
            if isinstance(val, dict):
                delimiter = "_" if prefix else ""
                self._get_env_vars("{}{}{}".format(prefix, delimiter, key),
                                   section[key])
            else:
                new_val = os.environ.get("{}_{}".format(prefix.upper(),
                                                        key.upper()), None)
                if new_val is not None:
                    section[key] = new_val


class OrderedDictYAMLLoader(yaml.Loader):
    'Based on: https://gist.github.com/844388'

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)
        self.add_constructor(u'tag:yaml.org,2002:map',
                             type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap',
                             type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(
                None,
                None,
                'expected a mapping node, but found {}'.format(node.id),
                node.start_mark
            )

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            try:
                hash(key)
            except TypeError as exc:
                raise yaml.constructor.ConstructorError(
                    'while constructing a mapping',
                    node.start_mark,
                    'found unacceptable key ({})'.format(exc),
                    key_node.start_mark
                )
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping


class AttrDict(OrderedDict):
    'Based on: https://github.com/mk-fg/layered-yaml-attrdict-config'

    def __init__(self, *argz, **kwz):
        super(AttrDict, self).__init__(*argz, **kwz)

    def __setitem__(self, k, v):
        super(AttrDict, self).__setitem__(k,
                                          AttrDict(v) if isinstance(v, Mapping)
                                          else v)

    def __getattr__(self, k):
        if not (k.startswith('__') or k.startswith('_OrderedDict__')):
            return self[k]
        else:
            return super(AttrDict, self).__getattr__(k)

    def __setattr__(self, k, v):
        if k.startswith('_OrderedDict__'):
            return super(AttrDict, self).__setattr__(k, v)
        self[k] = v

    @classmethod
    def from_yaml(cls, path, if_exists=False):
        if if_exists and not os.path.exists(path):
            return cls()
        return cls(yaml.load(open(path), OrderedDictYAMLLoader))

    @staticmethod
    def flatten_dict(data, path=tuple()):
        dst = list()
        for k, v in six.iteritems(data):
            k = path + (k,)
            if isinstance(v, Mapping):
                for v in v.flatten(k):
                    dst.append(v)
            else:
                dst.append((k, v))
        return dst

    def flatten(self, path=tuple()):
        return self.flatten_dict(self, path=path)

    def update_flat(self, val):
        if isinstance(val, AttrDict):
            val = val.flatten()
        for k, v in val:
            dst = self
            for slug in k[:-1]:
                if dst.get(slug) is None:
                    dst[slug] = AttrDict()
                dst = dst[slug]
            if v is not None or not isinstance(dst.get(k[-1]), Mapping):
                dst[k[-1]] = v

    def update_dict(self, data):
        self.update_flat(self.flatten_dict(data))

    def update_yaml(self, path):
        self.update_flat(self.from_yaml(path))

    def clone(self):
        clone = AttrDict()
        clone.update_dict(self)
        return clone

    def rebase(self, base):
        base = base.clone()
        base.update_dict(self)
        self.clear()
        self.update_dict(base)

    def dump(self, stream):
        yaml.representer.SafeRepresenter.add_representer(
            AttrDict, yaml.representer.SafeRepresenter.represent_dict)
        yaml.representer.SafeRepresenter.add_representer(
            OrderedDict, yaml.representer.SafeRepresenter.represent_dict)
        yaml.representer.SafeRepresenter.add_representer(
            defaultdict, yaml.representer.SafeRepresenter.represent_dict)
        yaml.representer.SafeRepresenter.add_representer(
            set, yaml.representer.SafeRepresenter.represent_list)
        yaml.safe_dump(self, stream,
                       default_flow_style=False, encoding='utf-8')
