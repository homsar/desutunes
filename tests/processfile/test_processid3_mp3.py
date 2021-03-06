# Tests the processid3 function from processfile.py for mp3s

from datetime import datetime, timedelta, timezone
import pytest
from desutunes.processfile import processid3


class File_mp3():
    def __init__(self, audio_path):
        self.file = str(audio_path / "test_audio.mp3")
        self.time_before_start = datetime.now(timezone.utc)
        self.result = processid3(self.file)
        self.time_after_end = datetime.now(timezone.utc)
        assert len(self.result) == 1
        self.metadata = self.result[0]


@pytest.fixture
def file_mp3(audio_path):
    return File_mp3(audio_path)


class Test_processid3_MP3:
    def test_original_file_name(self, file_mp3):
        assert file_mp3.metadata.OriginalFileName == file_mp3.file

    def test_new_file_name(self, file_mp3):
        assert str(file_mp3.metadata.Filename)[:-21] == (
            'Tachibana Kanade/Test MP3 file (')
        assert str(file_mp3.metadata.Filename)[-5:] == ').mp3'

    def test_title(self, file_mp3):
        assert file_mp3.metadata.Tracktitle == 'Test MP3 file'

    def test_album(self, file_mp3):
        assert file_mp3.metadata.Album == 'Sounds of the desutunes'

    def test_length(self, file_mp3):
        assert file_mp3.metadata.Length == 2168

    def test_anime(self, file_mp3):
        assert file_mp3.metadata.Anime == 'Spam'
        assert file_mp3.metadata.Role == 'OP'
        assert file_mp3.metadata.Rolequalifier == '1'

    def test_artist(self, file_mp3):
        assert file_mp3.metadata.Artist == 'Tachibana Kanade'

    def test_composer(self, file_mp3):
        assert file_mp3.metadata.Composer == '🐱'

    def test_label(self, file_mp3):
        assert file_mp3.metadata.Label == 'h0m54r records'

    def test_inmyriad(self, file_mp3):
        assert file_mp3.metadata.InMyriad == 'NO'

    def test_time(self, file_mp3):
        time_read = datetime.strptime(
            file_mp3.metadata.Dateadded,
            "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        assert file_mp3.time_before_start < time_read + timedelta(minutes=1)
        assert time_read < file_mp3.time_after_end
