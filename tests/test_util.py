import pytest

from telebot import util


def test_validate_token_invalid_tokens():
    with pytest.raises(ValueError):
        util.validate_token(':token')
    with pytest.raises(ValueError):
        util.validate_token('1234:')
    with pytest.raises(ValueError):
        util.validate_token('1234:abcd:extra')
    with pytest.raises(ValueError):
        util.validate_token('12a4:abcd')


def test_validate_token_valid():
    assert util.validate_token('1234:abcd') is True


def test_extract_bot_id():
    assert util.extract_bot_id('1234:abcd') == 1234
    assert util.extract_bot_id('bad') is None
