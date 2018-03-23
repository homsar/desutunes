# Test the role_detail function from processfile.py

from desutunes.processfile import role_detail


def test_role_detail_blank():
    result = role_detail("")
    assert len(result) == 4
    assert set(result.values()) == {''}
    assert set(result.keys()) == {'anime', 'role', 'rolepre', 'rolepost'}


def test_role_detail_noqual():
    result = role_detail("Digimon Adventure OP")
    assert result == {
        'anime': 'Digimon Adventure',
        'role': 'OP', 'rolepre': '', 'rolepost': ''
    }


def test_role_detail_bad():
    result = role_detail("Blah")
    assert result == {
        'anime': '',
        'role': '', 'rolepre': '', 'rolepost': 'Blah'
    }


def test_role_detail_qualpost():
    result = role_detail("Macross Frontier OP2")
    assert result == {
        'anime': 'Macross Frontier',
        'role': 'OP', 'rolepre': '', 'rolepost': '2'
    }


def test_role_detail_qualpre():
    result = role_detail("Eden of the East rebroadcast OP")
    assert result == {
        'anime': 'Eden of the East',
        'role': 'OP', 'rolepre': 'rebroadcast', 'rolepost': ''
    }


def test_role_detail_qualboth():
    result = role_detail("Eden of the East rebroadcast OP season 4")
    assert result == {
        'anime': 'Eden of the East',
        'role': 'OP', 'rolepre': 'rebroadcast', 'rolepost': 'season 4'
    }
