"""Wrapper for a dict/list structure to enable attribute based access."""


class StructWrapper:
    """Wrapper for a dict/list structure to enable attribute based access."""

    # Separator character to split path
    SEP = "/"

    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        """Get attribute by name"""

        parts = key.split(StructWrapper.SEP)

        data = self._data

        for part in parts:
            if isinstance(data, dict):
                if part in data:
                    data = data[part]
                else:
                    raise KeyError(  # pylint: disable=raise-missing-from
                        f"Member '{part}' not found when accessing '{key}'."
                    )

            elif isinstance(data, (list, tuple)):
                part = int(part)
                try:
                    data = data[part]
                except IndexError:
                    raise IndexError(  # pylint: disable=raise-missing-from
                        f"Member '{part}' out of range when accessing '{key}'."
                    )
            else:
                raise Exception(
                    f"Structure has as {data.__class__.__name__} member, "
                    "which we cannot handle."
                )

        return data

    def get(self, key, default=None):
        """Access attribute by name."""

        if key not in self:
            return default

        return self[key]

    def __contains__(self, name):
        """Check if attribute could be accessed."""

        try:
            _ = self[name]
            return True
        except (KeyError, IndexError):
            return False

    @property
    def raw(self):
        """Return the underlying dict / list structure."""

        return self._data

    def get_struct(self, name):
        """Return a substructure as an StructWrapper instance"""

        return StructWrapper(self.get(name))

    def __str__(self):
        return f"StructWrapper({self.raw})"
