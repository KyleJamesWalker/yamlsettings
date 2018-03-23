"""Protocol extension support for YamlSettings

Proposed types:
    * parent - Find first file, by searching up through parent directories.
    * each - Open each file found, and update yamldict
      each://defaults.yaml|settings.yaml|more.yaml

"""
from yamlsettings.extensions.local import LocalExtension
from yamlsettings.extensions.package import PackageExtension
from yamlsettings.extensions.registry import ExtensionRegistry, RegistryError

registry = ExtensionRegistry([
    LocalExtension,
    PackageExtension,
])

__all__ = ['registry', 'RegistryError']
