'''Tests creating and loading an empty desutunes database'''


def test_loadDatabase(database_model):
    assert database_model != False
    assert database_model._lock_edits
    assert database_model.sortColumn == -1
    assert database_model.sortOrder is None
    assert (database_model.libraryPath / "tesutotunes.db").stat().st_size > 0
