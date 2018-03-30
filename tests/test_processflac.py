# Tests the processflac function from processfile.py

from desutunes.processfile import processflac
from datetime import datetime, timedelta, timezone
import os
import pathlib
import pytest
path = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))


class File_flac():
    def __init__(self):
        self.file = str(path / "test_audio.flac")
        self.time_before_start = datetime.now(timezone.utc)
        self.result = processflac(self.file)
        self.time_after_end = datetime.now(timezone.utc)
        assert len(self.result) == 1
        self.metadata = self.result[0]


@pytest.fixture
def file_flac():
    return File_flac()


class Test_processflac:
    def test_original_file_name(self, file_flac):
        assert file_flac.metadata.OriginalFileName == file_flac.file

    def test_new_file_name(self, file_flac):
        assert str(file_flac.metadata.Filename)[:-22] == (
            'Tachibana Kanade/Test FLAC file (')
        assert str(file_flac.metadata.Filename)[-6:] == ').flac'

    def test_title(self, file_flac):
        assert file_flac.metadata.Tracktitle == 'Test FLAC file'

    def test_album(self, file_flac):
        assert file_flac.metadata.Album == 'Sounds of the desutunes'

    def test_length(self, file_flac):
        assert file_flac.metadata.Length == 2124

    def test_anime(self, file_flac):
        assert file_flac.metadata.Anime == 'Spam'
        assert file_flac.metadata.Role == 'insert song'
        assert file_flac.metadata.Rolequalifier == ''

    def test_artist(self, file_flac):
        assert file_flac.metadata.Artist == 'Tachibana Kanade'

    def test_composer(self, file_flac):
        assert file_flac.metadata.Composer == '🐱'

    def test_label(self, file_flac):
        assert file_flac.metadata.Label == 'h0m54r records'

    def test_inmyriad(self, file_flac):
        assert file_flac.metadata.InMyriad == 'NO'

    def test_time(self, file_flac):
        time_read = datetime.strptime(
            file_flac.metadata.Dateadded,
            "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        assert file_flac.time_before_start < time_read + timedelta(minutes=1)
        assert time_read < file_flac.time_after_end
