# -*- coding: utf-8 -*-
import yaml
import yaml.constructor
import collections


# ==========================================================================================================

class YAMLDict(collections.OrderedDict):
    '''
    Order-preserved, attribute-accessible dictionary object for YAML settings
    Improved from:
        https://github.com/mk-fg/layered-yaml-attrdict-config
    '''

    def __init__(self, *args, **kwargs):
        super(YAMLDict, self).__init__(*args, **kwargs)
        # reset types of all sub-nodes through the hiearchy
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
        return yaml.safe_dump(self, stream=None, default_flow_style=False, encoding='utf-8')

    def __repr__(self):
        return '<' + ', '.join(['{}: {}'.format(repr(k), repr(v)) for k, v in self.items()]) + '>'

    # override the standard update() method
    def update(self, yaml_dict):
        def _update_node(base_node, update_node):
                if isinstance(update_node, YAMLDict) or isinstance(update_node, dict):
                    if not (isinstance(base_node, YAMLDict)):
                        new_node = YAMLDict()
                    else:
                        new_node = base_node
                    for k, v in update_node.items():
                        new_node[k] = _update_node(new_node.get(k), v)
                elif isinstance(update_node, list) or isinstance(update_node, tuple):
                    # if not isinstance(base_node, list):
                    #     new_node = []
                    # else:
                    #     new_node = base_node
                    # NOTE: the whole list is replaced rather than appending an item
                    new_node = []
                    for v in update_node:
                        new_node.append(_update_node(None, v))
                else:
                    new_node = update_node
                return new_node
        # convert non-YAMLDict objects to a YAMLDict
        if not (isinstance(yaml_dict, YAMLDict) or isinstance(yaml_dict, dict)):
            yaml_dict = YAMLDict(yaml_dict)
        _update_node(self, yaml_dict)

    # clone from another object
    def clone(self, yaml_dict):
        self.clear()
        self.update(yaml_dict)

    # rebase from another object
    def rebase(self, yaml_dict):
        base = YAMLDict(yaml_dict)
        base.update(self)
        self.clone(base)

    # remove all keys other than the keys specified
    def limit(self, keys):
        if not isinstance(keys, list) and not isinstance(keys, tuple):
            keys = [keys]
        remove_keys = [k for k in self.keys() if k not in keys]
        for k in remove_keys:
            self.pop(k)

    # evaluate all *values* by calling the callback function and replace them with the return values
    def evaluate(self, callback):
        def _evaluate_node(node, callback):
            if isinstance(node, YAMLDict):
                for k, v in node.items():
                    node[k] = _evaluate_node(v, callback)
            elif isinstance(node, list):
                for i, v in enumerate(node[:]):
                    node[i] = _evaluate_node(v, callback)
            else:
                # replace a value with the return value of the callback function
                node = callback(node)
            return node
        _evaluate_node(self, callback)

    # return the flat structure
    def flat(self):
        def _traverse_node(path, node, yaml_flat):
            if isinstance(node, YAMLDict):
                for k, v in node.items():
                    _traverse_node(path + [k], v, yaml_flat)
            elif isinstance(node, list):
                # for i, v in enumerate(node):
                #     _traverse_node(path + ['${}'.format(i)], v)
                # NOTE: list node is not supported currently
                pass
            else:
                yaml_flat += [(path, node)]
        yaml_flat = []
        _traverse_node([], self, yaml_flat)
        return yaml_flat

    # update from a flat structure
    def inflate(self, yaml_flat):
        for path, value in yaml_flat:
            cur_node = self
            for i, key in enumerate(path):
                if key not in cur_node:
                    cur_node[key] = YAMLDict()
                if i < len(path) - 1:
                    cur_node = cur_node[key]
                else:
                    cur_node[key] = value


# add representer for YAMLDict
yaml.representer.SafeRepresenter.add_representer(YAMLDict, yaml.representer.SafeRepresenter.represent_dict)


# ==========================================================================================================

class YAMLDictLoader(yaml.Loader):
    '''
    Loader for YAMLDict object
    Adopted from:
        https://gist.github.com/844388
    '''

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)
        # override constructors for maps (i.e. dictionaries)
        self.add_constructor(u'tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor(u'tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    # method override to create YAMLDict rather than dict
    def construct_yaml_map(self, node):
        data = YAMLDict()
        yield data
        value = self.construct_mapping(node)
        super(YAMLDict, data).update(value)     # we want to call the original update() function here

    # method override to create YAMLDict rather than dict
    def construct_mapping(self, node, deep=False):
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

# ==========================================================================================================

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
