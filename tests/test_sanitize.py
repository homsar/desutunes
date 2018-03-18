# Test the sanitize function in processfile.py

from desutunes.processfile import sanitize


def test_sanitize_slash():
    assert sanitize('ON/OFF') == 'ONOFF'


def test_sanitize_backslash():
    assert sanitize(r'C:\WINDOWS') == 'C:WINDOWS'


def test_sanitize_newline():
    assert sanitize('Sakamoto \nMaaya') == 'Sakamoto Maaya'


def test_sanitize_noop():
    assert sanitize('Tachibana Kanade') == 'Tachibana Kanade'
