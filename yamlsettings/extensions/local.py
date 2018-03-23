"""Load a yaml from from the local filesystem"""
from yamlsettings.extensions.base import YamlSettingsExtension


class LocalExtension(YamlSettingsExtension):
    """Local filesystem, works with any valid system path. This
    is the default and will be used if you don't include the scheme.

    examples:
      * file://relative/foo/bar/baz.txt (opens a relative file)
      * file:///home/user (opens a directory from a absolute path)
      * foo/bar.baz (file:// is the default)

    """
    protocols = ['file']
    default_query = {}

    @classmethod
    def load_target(cls, scheme, path, fragment, username,
                    password, hostname, port, query,
                    load_method, **kwargs):
        full_path = (hostname or '') + path
        query.update(kwargs)
        return load_method(open(full_path, **query))
