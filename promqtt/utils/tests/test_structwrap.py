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
        'd': [1, 2, 3]
    })


def test_structwrap_dict(testdata):
    '''Test access to dict element'''

    assert testdata.a_b == '3'


def test_structwrap_list(testdata):
    '''Test access to list element'''

    assert testdata.d_1 == 2


def test_structwrap_in(testdata):
    '''Test usage of `in` operator.'''

    assert 'a_b' in testdata


def test_structwrap_get(testdata):
    '''Test get function'''

    assert testdata.get('a_b') == '3'


def test_structwrap_raise_keyerror(testdata):
    '''Test failed access to dict member'''

    with pytest.raises(KeyError) as kex:
        _ = testdata.a_e

    assert "Member 'e' not found" in str(kex)


def test_structwrap_raise_indexerror(testdata):
    '''Test failed access to list element'''

    with pytest.raises(IndexError) as iex:
        _ = testdata.d_3

    assert "Member '3' out of range" in str(iex)
