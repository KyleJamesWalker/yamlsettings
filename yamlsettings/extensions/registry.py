"""Extension registry, to allow easy opening of various types.

"""
import pkg_resources

from six.moves.urllib.parse import urlsplit
from six import string_types
import yamlsettings


class RegistryError(Exception):
    """The base exception thrown by the registry"""


class NoProtocolError(RegistryError):
    """Thrown when there is no extension for the given protocol"""


class InvalidQuery(RegistryError):
    """Thrown when an extension is passed unexpected arguments"""


class ExtensionRegistry(object):

    def __init__(self, extensions):
        """A registry that stores extensions to open and parse Target URIs

        :param extensions: A list of extensions.
        :type extensions: yamlsettings.extensions.base.YamlSettingsExtension

        """
        self.registry = {}
        self.extensions = {}
        self.default_protocol = 'file'
        for extension in extensions:
            self.add(extension)
        self._discover()

    def _discover(self):
        """Find and install all extensions"""
        for ep in pkg_resources.iter_entry_points('yamlsettings10'):
            ext = ep.load()
            if callable(ext):
                ext = ext()
            self.add(ext)

    def get_extension(self, protocol):
        """Retrieve extension for the given protocol

        :param protocol: name of the protocol
        :type protocol: string
        :raises NoProtocolError: no extension registered for protocol

        """
        if protocol not in self.registry:
            raise NoProtocolError("No protocol for %s" % protocol)
        index = self.registry[protocol]
        return self.extensions[index]

    def add(self, extension):
        """Adds an extension to the registry

        :param extension: Extension object
        :type extension: yamlsettings.extensions.base.YamlSettingsExtension

        """
        index = len(self.extensions)
        self.extensions[index] = extension
        for protocol in extension.protocols:
            self.registry[protocol] = index

    def _load_first(self, target_uris, load_method, **kwargs):
        """Load first yamldict target found in uri list.

        :param target_uris: Uris to try and open
        :param load_method: load callback
        :type target_uri: list or string
        :type load_method: callback

        :returns: yamldict

        """
        if isinstance(target_uris, string_types):
            target_uris = [target_uris]

        # TODO: Move the list logic into the extension, otherwise a
        # load will always try all missing files first.
        # TODO: How would multiple protocols work, should the registry hold
        # persist copies?
        for target_uri in target_uris:
            target = urlsplit(target_uri, scheme=self.default_protocol)

            extension = self.get_extension(target.scheme)
            query = extension.conform_query(target.query)
            try:
                yaml_dict = extension.load_target(
                    target.scheme,
                    target.path,
                    target.fragment,
                    target.username,
                    target.password,
                    target.hostname,
                    target.port,
                    query,
                    load_method,
                    **kwargs
                )
                return yaml_dict
            except extension.not_found_exception:
                pass

        raise IOError("unable to load: {0}".format(target_uris))

    def load(self, target_uris, fields=None, **kwargs):
        """Load first yamldict target found in uri.

        :param target_uris: Uris to try and open
        :param fields: Fields to filter. Default: None
        :type target_uri: list or string
        :type fields: list

        :returns: yamldict

        """
        yaml_dict = self._load_first(
            target_uris, yamlsettings.yamldict.load, **kwargs
        )
        # TODO: Move this into the extension, otherwise every load from
        # a persistant location will refilter fields.
        if fields:
            yaml_dict.limit(fields)

        return yaml_dict

    def load_all(self, target_uris, **kwargs):
        '''
        Load *all* YAML settings from a list of file paths given.

            - File paths in the list gets the priority by their orders
            of the list.
        '''
        yaml_series = self._load_first(
            target_uris, yamlsettings.yamldict.load_all, **kwargs
        )
        yaml_dicts = []
        for yaml_dict in yaml_series:
            yaml_dicts.append(yaml_dict)
        # return YAMLDict objects
        return yaml_dicts
