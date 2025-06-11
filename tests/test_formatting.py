from telebot import formatting


def test_mitalic():
    assert formatting.mitalic('abc') == '_abc_'
