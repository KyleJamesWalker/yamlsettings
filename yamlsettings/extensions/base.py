"""Base extension interface"""
import yaml

from six.moves.urllib.parse import parse_qs


class YamlSettingsExtension:
    """Extension Interface"""
    protocols = ()
    # Dictionary of expected kwargs and flag for json loading values (bool/int)
    default_query = {}
    not_found_exception = IOError

    @classmethod
    def conform_query(cls, query):
        """Converts the query string from a target uri, uses
        cls.default_query to populate default arguments.

        :param query: Unparsed query string
        :type query: urllib.parse.unsplit(uri).query
        :returns: Dictionary of parsed values, everything in cls.default_query
            will be set if not passed.

        """
        query = parse_qs(query, keep_blank_values=True)

        # Load yaml of passed values
        for key, vals in query.items():
            # Multiple values of the same name could be passed use first
            # Also params without strings will be treated as true values
            query[key] = yaml.load(vals[0] or 'true', Loader=yaml.FullLoader)

        # If expected, populate with defaults
        for key, val in cls.default_query.items():
            if key not in query:
                query[key] = val

        return query

    @classmethod
    def load_target(cls, scheme, path, fragment, username,
                    password, hostname, port, query,
                    load_method, **kwargs):
        """Override this method to use values from the parsed uri to initialize
        the expected target.

        """
        raise NotImplementedError("load_target must be overridden")
