'''Wrapper for a dict/list structure to enable attribute based access.'''


STRUCTWRAPPER_SEPATATOR = '_'


class StructWrapper():
    '''Wrapper for a dict/list structure to enable attribute based access.'''

    def __init__(self, data):
        self._data = data


    def __getattr__(self, name):
        '''Get attribute by name'''

        parts = name.split(STRUCTWRAPPER_SEPATATOR)

        data = self._data

        for part in parts:
            if isinstance(data, dict):
                if part in data:
                    data = data[part]
                else:
                    raise KeyError( # pylint: disable=raise-missing-from
                        f"Member '{part}' not found when accessing '{name}'.")

            elif isinstance(data, list):
                part = int(part)
                try:
                    data = data[part]
                except IndexError:
                    raise IndexError( # pylint: disable=raise-missing-from
                        f"Member '{part}' out of range when accessing '{name}'.")
            else:
                raise Exception('Hmmm....')

        return data


    def get(self, name):
        '''Access attribute by name.'''

        return getattr(self, name)


    def __contains__(self, name):
        '''Check if attribute could be accessed.'''

        try:
            getattr(self, name)
            return True
        except (KeyError, IndexError):
            return False


    @property
    def raw(self):
        '''Return the underlying dict / list structure.'''

        return self._data


    def get_struct(self, name):
        '''Return a substructure as an StructWrapper instance'''

        return StructWrapper(self.get(name))
