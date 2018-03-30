import plistlib
import pathlib
from PyQt5.QtCore import QFileInfo
from .processfile import metadata, part, canonicalFileName, processFile
from urllib.parse import urlparse, unquote
from datetime import datetime, timezone

_itunes_headers = {
    -1: 'Track ID',
    0: 'Persistent ID',
    1: 'Location',
    2: 'Track title',
    3: 'Artist',
    4: 'Album',
    5: 'Total Time',
    9: 'Description',
    10: 'Composer',
    11: 'Episode',
    12: 'Date Added'
}


def handleXML(fileName):
    try:
        with open(fileName, 'rb') as f:
            plist = plistlib.load(f)
    except Exception as e:
        return []

    tracks = []

    for idx, (tid, track) in enumerate(plist['Tracks'].items()):
        if not track['Location'].startswith('file'):
            continue
        inMyriad = track.get('Episode', 'Yes')

        # The library has some typos, but the first 10 characters are reliable
        if inMyriad.lower().startswith('not in myr'):
            inMyriad = "NO"

        title, anime, role, rolequal = part(track['Name'])
        id = track['Persistent ID']
        artist = track['Artist']
        originalFileName = unquote(urlparse(track['Location']).path)
        suffix = pathlib.Path(originalFileName).suffix[1:]
        newFileName = canonicalFileName(id, artist, title, suffix)

        # Latest versions of iTunes don't export Description in XML dumps
        # We have to examine the file directly
        # Composer should be in the XML, but check the file just in case
        # since we've probably grabbed its metadata anyway
        label = track.get('Description', '')
        composer = track.get('Composer', '')
        if not label or not composer:
            try:
                file_metadata = processFile(originalFileName,
                                            QFileInfo(originalFileName))[0]
                if not label:
                    label = file_metadata.Label
                if not composer:
                    composer = file_metadata.Composer
            except Exception as ex:
                print("Unable to get extra metadata for", originalFileName)

        track_metadata = metadata(
            ID=id,
            OriginalFileName=originalFileName,
            Filename=newFileName,
            Tracktitle=title,
            Album=track.get('Album', ''),
            Length=track['Total Time'],
            Anime=anime,
            Role=role,
            Rolequalifier=rolequal,
            Artist=artist,
            Composer=composer,
            Label=label,
            InMyriad=inMyriad,
            Dateadded=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"))
        tracks.append(track_metadata)
    print(f'Got metadata for {len(tracks)} tracks, out of '
          f'{len(plist["Tracks"])} in the iTunes XML.')
    return tracks


def exportXML(model, libraryPath, fileName):
    tracks = {}
    episode_map = {'NO': 'NOT IN MYRIAD', 'Yes': ''}
    for i in range(model.rowCount()):
        r = model.record(i)
        tracks[str(i)] = {
            'Track ID':
            str(i + 1),
            'Persistent ID':
            r.value('ID'),
            'Location': (libraryPath / r.value('Filename')).as_uri(),
            'Name':
            '{} ({} {}{}{})'.format(
                r.value('Tracktitle'), r.value('Anime'), r.value('Role'), ''
                if r.value('Rolequant') == '' else ' ', r.value('Rolequant')),
            'Artist':
            r.value('Artist'),
            'Album':
            r.value('Album'),
            'Total Time':
            r.value('Length') / 1000,
            'Description':
            r.value('Label'),
            'Composer':
            r.value('Composer'),
            'Episode':
            episode_map.get(r.value('InMyriad'), r.value('InMyriad')),
            'Date Added':
            datetime.strptime(r.value('DateAdded'), "%Y-%m-%d %H:%M")
        }
    try:
        with open(fileName, 'wb') as f:
            plistlib.dump({'Tracks': tracks}, f)
    except Exception:
        pass
