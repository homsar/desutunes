import pytest


@pytest.fixture(scope="session")
def audio_path():
    import os
    import pathlib

    path = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
    return path / "audio"


@pytest.fixture(scope="module")
def database_model(tmpdir_factory):
    import pathlib
    from desutunes.tablemodel import loadDatabase

    return loadDatabase("tesutotunes.db",
                        pathlib.Path(tmpdir_factory.mktemp('tesutotunes')))
