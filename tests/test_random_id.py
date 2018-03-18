# Test the random_id function in processfile.py

from desutunes.processfile import random_id


def test_random_id_length():
    assert len(random_id()) == 16


def test_random_id_uniqueness():
    assert random_id() != random_id()


def test_random_id_hex():
    int(random_id(), 16)


def test_random_id_case():
    id = random_id()
    assert id == id.upper()
