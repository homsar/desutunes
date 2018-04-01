# Test the processFile function from processfile.py

import pytest
import mutagen
from desutunes.processfile import processFile


def test_processfile_returns(audio_path):
    assert len(processFile(str(audio_path / "test_audio.flac"))) == 1
    assert len(processFile(str(audio_path / "test_audio.m4a"))) == 1
    assert len(processFile(str(audio_path / "test_audio.mp3"))) == 1
    assert len(processFile(str(audio_path / "test_audio.aac"))) == 1


def test_processfile_fails_bad_extension_file_present(audio_path):
    assert len(processFile(str(audio_path / "test_audio.aif"))) == 0


def test_processfile_fails_good_extension_file_missing(audio_path):
    with pytest.raises(mutagen.MutagenError):
        processFile(str(audio_path / "missing.mp3"))
