from yamlsettings.extensions import YamlSettingsExtension


class ZxcExtension(YamlSettingsExtension):
    """Quick Example Plugin for testing

    Standard file opener, but will merge in values passed to kwargs

    Example:
        import yamlsettings
        # Essentially the same as file://
        yamlsettings.load_uri("zxc://foo.yaml")
        # Load with the value of foo set to 'BAR!'
        yamlsettings.load_uri("zxc://foo.yaml", foo='BAR!')
        # Load and add baz entry
        yamlsettings.load_uri("zxc://foo.yaml", baz='boom')

    """
    protocols = ['zxc']

    @classmethod
    def load_target(cls, scheme, path, fragment, username,
                    password, hostname, port, query,
                    load_method, **kwargs):
        full_path = (hostname or '') + path
        obj = load_method(open(full_path, **query))
        obj.update(kwargs)
        return obj
