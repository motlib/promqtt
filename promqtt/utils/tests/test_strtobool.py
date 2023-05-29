"""Unit tests for strtobool"""

import pytest

from .. import str_to_bool


@pytest.mark.parametrize("val", ("y", "Y", "On", "TrUE", "1"))
def test_strtobool_true(val):
    """Test true cases for strtobool"""

    assert str_to_bool(val)


@pytest.mark.parametrize("val", ("n", "", "Off", "foo", "False", "0"))
def test_strtobool_false(val):
    """Test false cases for strtobool"""

    assert not str_to_bool(val)
