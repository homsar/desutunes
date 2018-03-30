# Tests the processm4a function from processfile.py

from desutunes.processfile import processm4a
from datetime import datetime, timedelta
import os
import pathlib
import pytest
path = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))


class File_m4a():
    def __init__(self):
        self.file = str(path / "test_audio.m4a")
        self.time_before_start = datetime.now()
        self.result = processm4a(self.file)
        self.time_after_end = datetime.now()
        assert len(self.result) == 1
        self.metadata = self.result[0]


@pytest.fixture
def file_m4a():
    return File_m4a()


class Test_processid3_M4A:
    def test_original_file_name(self, file_m4a):
        assert file_m4a.metadata.OriginalFileName == file_m4a.file

    def test_new_file_name(self, file_m4a):
        assert str(file_m4a.metadata.Filename)[:-21] == (
            'Tachibana Kanade/Test M4A file (')
        assert str(file_m4a.metadata.Filename)[-5:] == ').m4a'

    def test_title(self, file_m4a):
        assert file_m4a.metadata.Tracktitle == 'Test M4A file'

    def test_album(self, file_m4a):
        assert file_m4a.metadata.Album == 'Sounds of the desutunes'

    def test_length(self, file_m4a):
        assert file_m4a.metadata.Length == 2148

    def test_anime(self, file_m4a):
        assert file_m4a.metadata.Anime == 'Spam'
        assert file_m4a.metadata.Role == 'ED'
        assert file_m4a.metadata.Rolequalifier == 'episode 3'

    def test_artist(self, file_m4a):
        assert file_m4a.metadata.Artist == 'Tachibana Kanade'

    def test_composer(self, file_m4a):
        assert file_m4a.metadata.Composer == '🐱'

    def test_label(self, file_m4a):
        assert file_m4a.metadata.Label == 'h0m54r records'

    def test_inmyriad(self, file_m4a):
        assert file_m4a.metadata.InMyriad == 'NO'

    def test_time(self, file_m4a):
        time_read = datetime.strptime(file_m4a.metadata.Dateadded,
                                      "%Y-%m-%d %H:%M")
        assert file_m4a.time_before_start < time_read + timedelta(minutes=1)
        assert time_read < file_m4a.time_after_end
