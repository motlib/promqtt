'''Unittests for structwrap module'''

import pytest

from ..structwrap import StructWrapper

# pylint: disable=redefined-outer-name

@pytest.fixture
def testdata():
    '''Generate testdata for StructWrapper unit tests'''

    return StructWrapper({
        'a': {'b': '3'},
        'c': 4,
        'd': [1, 2, 3],
        'tuple': (1, 2, 3),
    })


def test_structwrap_dict(testdata):
    '''Test access to dict element'''

    assert testdata['a/b'] == '3'


def test_structwrap_list(testdata):
    '''Test access to list element'''

    assert testdata['d/1'] == 2


def test_structwrap_in(testdata):
    '''Test usage of `in` operator.'''

    assert 'a/b' in testdata


def test_structwrap_in_no_member(testdata):
    '''Test usage of `in` operator.'''

    assert 'a/e' not in testdata


def test_structwrap_in_no_index(testdata):
    '''Test usage of `in` operator.'''

    assert 'd/4' not in testdata


def test_structwrap_get(testdata):
    '''Test get function'''

    assert testdata.get('a/b') == '3'


def test_structwrap_get_default(testdata):
    '''Test get function'''

    assert testdata.get('a/x', 42) == 42


def test_structwrap_raise_keyerror(testdata):
    '''Test failed access to dict member'''

    with pytest.raises(KeyError) as kex:
        _ = testdata['a/e']

    assert "Member 'e' not found" in str(kex)


def test_structwrap_raise_indexerror(testdata):
    '''Test failed access to list element'''

    with pytest.raises(IndexError) as iex:
        _ = testdata['d/3']

    assert "Member '3' out of range" in str(iex)


def test_structwrap_get_raw():
    '''Ensure that raw returns the underlying data structure'''

    data = {'a': 3}
    wrap = StructWrapper(data)

    assert wrap.raw == data


def test_structwrap_member_access(testdata):
    '''Test getting a substructure'''

    sub = testdata.get_struct('a')

    assert isinstance(sub, StructWrapper)
    assert sub['b'] == '3'


def test_structwrap_str(testdata):
    '''Check that a structwrap instance can be converted to string'''

    # just ensure we do not raise an exception
    assert str(testdata) == (
        "StructWrapper("
        "{'a': {'b': '3'}, 'c': 4, 'd': [1, 2, 3], 'tuple': (1, 2, 3)}"
        ")")
