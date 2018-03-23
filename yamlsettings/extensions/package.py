"""Load a yaml resource from a python package."""
import pkgutil

import yamlsettings
from yamlsettings.extensions.base import YamlSettingsExtension


class PackageExtension(YamlSettingsExtension):
    """Load a yaml resource from a python package.

    Args:
      resource: The resource to load from the package (default: settings.yaml)
      env: When set the yamldict will update with env variables (default: true)
      prefix: Prefix for environment loading (default: None)
      persist: When set the yamldict will only be loaded once. (default: true)

    examples:
      * pkg://example (opens the settings.yaml resource and loads env vars)

    """
    protocols = ['pkg', 'package']
    default_query = {
        'resource': 'settings.yaml',
        'env': True,
        'prefix': None,
        'persist': True,
    }
    _persistence = {}

    @classmethod
    def load_target(cls, scheme, path, fragment, username,
                    password, hostname, port, query,
                    load_method, **kwargs):
        package_path = (hostname or '') + path
        query.update(kwargs)

        resource = query['resource']
        env = query['env']
        prefix = query['prefix']
        persist = query['persist']

        persistence_key = "{}:{}".format(package_path, resource)

        if persist and persistence_key in cls._persistence:
            yaml_contents = cls._persistence[persistence_key]
        else:
            pkg_data = pkgutil.get_data(package_path, resource)
            if pkg_data is None:
                raise IOError("package - {}:{}".format(package_path, resource))

            yaml_contents = load_method(pkg_data)
            if env:
                yamlsettings.update_from_env(yaml_contents, prefix)

            if persist:
                cls._persistence[persistence_key] = yaml_contents

        return yaml_contents
