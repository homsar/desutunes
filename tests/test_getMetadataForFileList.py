# Tests the getMetadataForFileList function from processfile.py

import os
import pathlib
from desutunes.processfile import getMetadataForFileList
path = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))


def test_getMetadataForFileList_files():
    metadata_list = getMetadataForFileList(
        [str(path / "test_audio.m4a"),
         str(path / "test_audio.mp3"),
         str(path / "test_audio.aac"),
         str(path / "test_audio.flac")])
    assert len(metadata_list) == 4
    assert ({metadata.Artist for metadata in metadata_list} ==
            {'Tachibana Kanade'})


def test_getMetadataForFileList_folder():
    metadata_list = getMetadataForFileList([str(path)])
    assert len(metadata_list) == 4
    assert ({metadata.Artist for metadata in metadata_list} ==
            {'Tachibana Kanade'})
