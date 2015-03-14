# -*- coding: utf-8 -*-
import yaml
import yaml.constructor
import collections


class YAMLDict(collections.OrderedDict):
    '''
    Order-preserved, attribute-accessible dictionary object for YAML settings
    Improved from:
        https://github.com/mk-fg/layered-yaml-attrdict-config
    '''

    def __init__(self, *args, **kwargs):
        super(YAMLDict, self).__init__(*args, **kwargs)
        # Reset types of all sub-nodes through the hiearchy
        self.update(self)

    def __getattr__(self, k):
        if not (k.startswith('__') or k.startswith('_OrderedDict__')):
            return self[k]
        else:
            return super(YAMLDict, self).__getattr__(k)

    def __setattr__(self, k, v):
        if k.startswith('_OrderedDict__'):
            return super(YAMLDict, self).__setattr__(k, v)
        self[k] = v

    def __str__(self):
        return dump(self, stream=None, default_flow_style=False)

    def __repr__(self):
        return '<' + ', '.join(['{}: {}'.format(repr(k), repr(v))
                               for k, v in self.items()]) + '>'

    def traverse(self, callback):
        ''' Traverse through all keys and values (in-order)
            and replace keys and values with the return values
            from the callback function.
        '''
        def _traverse_node(path, node, callback):
            ret_val = callback(path, node)
            if ret_val is not None:
                # replace node with the return value
                node = ret_val
            else:
                # traverse deep into the hierarchy
                if isinstance(node, YAMLDict):
                    for k, v in node.items():
                        node[k] = _traverse_node(path + [k], v,
                                                 callback)
                elif isinstance(node, list):
                    for i, v in enumerate(node):
                        node[i] = _traverse_node(path + ['[{}]'.format(i)], v,
                                                 callback)
                else:
                    pass
            return node
        _traverse_node([], self, callback)

    def update(self, yaml_dict):
        ''' Update the content (i.e. keys and values) with yaml_dict.
        '''
        def _update_node(base_node, update_node):
                if isinstance(update_node, YAMLDict) or \
                        isinstance(update_node, dict):
                    if not (isinstance(base_node, YAMLDict)):
                        # NOTE: A regular dictionay is replaced by a new
                        #       YAMLDict object.
                        new_node = YAMLDict()
                    else:
                        new_node = base_node
                    for k, v in update_node.items():
                        new_node[k] = _update_node(new_node.get(k), v)
                elif isinstance(update_node, list) or \
                        isinstance(update_node, tuple):
                    # NOTE: A list/tuple is replaced by a new list/tuple.
                    new_node = []
                    for v in update_node:
                        new_node.append(_update_node(None, v))
                    if isinstance(update_node, tuple):
                        new_node = tuple(new_node)
                else:
                    new_node = update_node
                return new_node
        # Convert non-YAMLDict objects to a YAMLDict
        if not (isinstance(yaml_dict, YAMLDict) or
                isinstance(yaml_dict, dict)):
            yaml_dict = YAMLDict(yaml_dict)
        _update_node(self, yaml_dict)

    def clone(self):
        ''' Creates and returns a new copy of self.
        '''
        clone = YAMLDict()
        clone.update(self)
        return clone

    def rebase(self, yaml_dict):
        ''' Use yaml_dict as self's new base and update with existing
            reverse of update.
        '''
        base = yaml_dict.clone()
        base.update(self)
        self.clear()
        self.update(base)

    def limit(self, keys):
        ''' Remove all keys other than the keys specified.
        '''
        if not isinstance(keys, list) and not isinstance(keys, tuple):
            keys = [keys]
        remove_keys = [k for k in self.keys() if k not in keys]
        for k in remove_keys:
            self.pop(k)


class YAMLDictLoader(yaml.Loader):
    '''
    Loader for YAMLDict object
    Adopted from:
        https://gist.github.com/844388
    '''

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)
        # override constructors for maps (i.e. dictionaries)
        self.add_constructor(u'tag:yaml.org,2002:map',
                             type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap',
                             type(self).construct_yaml_map)

    # Method override to create YAMLDict rather than dict
    def construct_yaml_map(self, node):
        data = YAMLDict()
        yield data
        value = self.construct_mapping(node)
        # Call the original update() function here to maintain YAMLDict
        super(YAMLDict, data).update(value)

    # method override to create YAMLDict rather than dict
    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        if not isinstance(node, yaml.MappingNode):
            raise yaml.constructor.ConstructorError(
                None,
                None,
                'expected a mapping node, but found {}'.format(node.id),
                node.start_mark
            )
        mapping = YAMLDict()
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


def load(stream):
    """
    Parse the first YAML document in a stream
    and produce the corresponding YAMLDict object.
    """
    loader = YAMLDictLoader(stream)
    try:
        return loader.get_single_data()
    finally:
        loader.dispose()


def load_all(stream):
    """
    Parse all YAML documents in a stream
    and produce corresponding YAMLDict objects.
    """
    loader = YAMLDictLoader(stream)
    try:
        while loader.check_data():
            yield loader.get_data()
    finally:
        loader.dispose()


class YAMLDictRepresenter(yaml.representer.Representer):

    def represent_YAMLDict(self, mapping):
        value = []
        node = yaml.MappingNode(u'tag:yaml.org,2002:map',
                                value, flow_style=None)
        if self.alias_key is not None:
            self.represented_objects[self.alias_key] = node
        best_style = True
        if hasattr(mapping, 'items'):
            mapping = mapping.items()
        for item_key, item_value in mapping:
            node_key = self.represent_data(item_key)
            node_value = self.represent_data(item_value)
            if not (isinstance(node_key, yaml.ScalarNode) and
                    not node_key.style):
                best_style = False
            if not (isinstance(node_value, yaml.ScalarNode)
                    and not node_value.style):
                best_style = False
            value.append((node_key, node_value))
        if self.default_flow_style is not None:
            node.flow_style = self.default_flow_style
        else:
            node.flow_style = best_style
        return node


YAMLDictRepresenter.add_representer(YAMLDict,
                                    YAMLDictRepresenter.represent_YAMLDict)


class YAMLDictDumper(yaml.emitter.Emitter,
                     yaml.serializer.Serializer,
                     YAMLDictRepresenter,
                     yaml.resolver.Resolver):

    def __init__(self, stream,
                 default_style=None, default_flow_style=None,
                 canonical=None, indent=None, width=None,
                 allow_unicode=None, line_break=None,
                 encoding=None, explicit_start=None, explicit_end=None,
                 version=None, tags=None):
        yaml.emitter.Emitter.__init__(self, stream, canonical=canonical,
                                      indent=indent, width=width,
                                      allow_unicode=allow_unicode,
                                      line_break=line_break)
        yaml.serializer.Serializer.__init__(self,
                                            encoding=encoding,
                                            explicit_start=explicit_start,
                                            explicit_end=explicit_end,
                                            version=version,
                                            tags=tags)
        YAMLDictRepresenter.__init__(self, default_style=default_style,
                                     default_flow_style=default_flow_style)
        yaml.resolver.Resolver.__init__(self)


def dump(data, stream=None, **kwds):
    """
    Serialize YAMLDict into a YAML stream.
    If stream is None, return the produced string instead.
    """
    return yaml.dump_all([data], stream, Dumper=YAMLDictDumper, **kwds)


def dump_all(data_list, stream=None, **kwds):
    """
    Serialize YAMLDict into a YAML stream.
    If stream is None, return the produced string instead.
    """
    return yaml.dump_all(data_list, stream, Dumper=YAMLDictDumper, **kwds)
