"""Config related module

"""
import os
from collections import defaultdict
import pkgutil

import yamlsettings


def validate(cfg: yamlsettings.yamldict.YAMLDict):
    """Asserts if a value in the required_keys paths is not defined
    Args:
        cfg: Configuration Settings
    Raises:
        RuntimeError: When a required key is null
    """
    check_paths = [x.split('.') for x in cfg.get('required_keys', {})]

    def _null_traverse(path, node):
        """Callback for yamlsettings traverse"""
        if node is None and any(path[:len(x)] == x for x in check_paths):
            raise RuntimeError("{} is not set".format(".".join(path)))
        return None

    cfg.traverse(_null_traverse)


def get_config(package: str, resource: str=None) -> \
        yamlsettings.yamldict.YAMLDict:
    """Get the package's configuration

    Args:
        package: Package to get configuration
        resource: Resource to load from the requested module.
            Default: settings.yaml

    Returns:
        The current configuration for the module

    Raises:
        RuntimeError: When the module has not been initialized

    """
    resource = resource or "settings.yaml"
    if _CONFIG[package].get(resource) is None:
        app_settings = yamlsettings.yamldict.load(
            pkgutil.get_data(package, resource)
        )

        override_file = "{}_OVERRIDE".format(package.upper().replace('.', '_'))
        if os.environ.get(override_file):
            app_settings.update(
                yamlsettings.load(os.environ[override_file]),
            )

        # TODO: Would we want to also add prefix here based on the package?
        yamlsettings.update_from_env(app_settings)
        validate(app_settings)

        _CONFIG[package][resource] = app_settings

    return _CONFIG[package][resource]


_CONFIG = defaultdict(dict)
