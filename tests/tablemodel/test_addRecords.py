'''Tests adding records to a desutunes db'''

from desutunes.processfile import metadata


def test_addRecords(database_model, audio_path):
    tracks_to_add = [
        metadata(
            ID=id,
            Filename=database_model.libraryPath / "h0m54r" / filename,
            Tracktitle=title,
            Artist='h0m54r',
            Album='Sounds of the desutunes',
            Length=1234,
            Anime='Neko Desu',
            Role='OP',
            Rolequalifier='',
            Label='h0m54r records',
            Composer='h0m54r',
            InMyriad=False,
            Dateadded='2018-04-01 12:00',
            OriginalFileName=audio_path / 'test_audio.mp3'
        ) for (id, filename, title) in [
            ('123456789ABCDEF0', 'test_1.mp3', 'Test 1'),
            ('0123456789ABCDEF', 'test_2.mp3', 'Test 2')
        ]
    ]
    result = database_model.addRecords(tracks_to_add)
    assert result
    assert ((database_model.libraryPath / "h0m54r/test_1.mp3").stat().st_size
            == 36057)
    assert ((database_model.libraryPath / "h0m54r/test_2.mp3").stat().st_size
            == 36057)
    assert database_model.rowCount() == 2
    assert database_model.data(database_model.index(0, 2)) == 'Test 1'
    assert database_model.data(database_model.index(1, 0)) == '0123456789ABCDEF'
    
