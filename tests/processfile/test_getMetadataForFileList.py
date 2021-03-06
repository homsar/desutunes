# Tests the getMetadataForFileList function from processfile.py

import os
import pathlib
from desutunes.processfile import getMetadataForFileList


def test_getMetadataForFileList_files(audio_path):
    metadata_list = getMetadataForFileList(
        [str(audio_path / "test_audio.m4a"),
         str(audio_path / "test_audio.mp3"),
         str(audio_path / "test_audio.aac"),
         str(audio_path / "test_audio.flac")])
    assert len(metadata_list) == 4
    assert ({metadata.Artist for metadata in metadata_list} ==
            {'Tachibana Kanade'})


def test_getMetadataForFileList_folder(audio_path):
    metadata_list = getMetadataForFileList([str(audio_path)])
    assert len(metadata_list) == 4
    assert ({metadata.Artist for metadata in metadata_list} ==
            {'Tachibana Kanade'})
