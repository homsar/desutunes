# Tests the processid3 function from processfile.py for mp3s

from desutunes.processfile import processid3
from datetime import datetime, timedelta, timezone
from mutagen import aac
import os
import pathlib
import pytest
path = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))


class File_aac():
    def __init__(self):
        self.file = str(path / "test_audio.aac")
        self.time_before_start = datetime.now(timezone.utc)
        self.result = processid3(self.file, audioengine=aac.AAC)
        self.time_after_end = datetime.now(timezone.utc)
        assert len(self.result) == 1
        self.metadata = self.result[0]


@pytest.fixture
def file_aac():
    return File_aac()


class Test_processid3_AAC:
    def test_original_file_name(self, file_aac):
        assert file_aac.metadata.OriginalFileName == file_aac.file

    def test_new_file_name(self, file_aac):
        assert str(file_aac.metadata.Filename)[:-21] == (
            'Tachibana Kanade/Test AAC file (')
        assert str(file_aac.metadata.Filename)[-5:] == ').aac'

    def test_title(self, file_aac):
        assert file_aac.metadata.Tracktitle == 'Test AAC file'

    def test_album(self, file_aac):
        assert file_aac.metadata.Album == 'Sounds of the desutunes'

    def test_length(self, file_aac):
        assert file_aac.metadata.Length == 2159

    def test_anime(self, file_aac):
        assert file_aac.metadata.Anime == 'Spam'
        assert file_aac.metadata.Role == 'main theme'
        assert file_aac.metadata.Rolequalifier == ''

    def test_artist(self, file_aac):
        assert file_aac.metadata.Artist == 'Tachibana Kanade'

    def test_composer(self, file_aac):
        assert file_aac.metadata.Composer == '107.9FM'

    def test_label(self, file_aac):
        assert file_aac.metadata.Label == ''

    def test_inmyriad(self, file_aac):
        assert file_aac.metadata.InMyriad == 'NO'

    def test_time(self, file_aac):
        time_read = datetime.strptime(
            file_aac.metadata.Dateadded,
            "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        assert file_aac.time_before_start < time_read + timedelta(minutes=1)
        assert time_read < file_aac.time_after_end
