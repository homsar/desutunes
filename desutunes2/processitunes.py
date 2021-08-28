import plistlib
import pathlib
from PyQt5.QtCore import QFileInfo
from .db import ensure_session, Track, role_spellings, Spelling
from .processfile import metadata, part, canonicalFileName, processFile
from urllib.parse import urlparse, unquote
from datetime import datetime, timezone
from sqlalchemy import select


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

        title, roles = part(track['Name'])
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

        if (year := track.get('Year')) is not None:
            year = int(year)

        track_metadata = metadata(
            ID=id,
            OriginalFileName=originalFileName,
            Filename=newFileName,
            Tracktitle=title,
            Album=track.get('Album', ''),
            Length=track['Total Time'],
            Roles=roles,
            Artist=artist,
            Composer=composer,
            Label=label,
            Year=year,
            InMyriad=inMyriad,
            Dateadded=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        )
        tracks.append(track_metadata)
    print(f'Got metadata for {len(tracks)} tracks, out of '
          f'{len(plist["Tracks"])} in the iTunes XML.')
    return tracks


@ensure_session
def exportXML(model, libraryPath, fileName, session):
    tracks = {}
    episode_map = {'NO': 'NOT IN MYRIAD', 'Yes': ''}
    for i, track in enumerate(session.execute(select(Track)).scalars.all()):
        tracks[str(i)] = {
            'Track ID':
            str(i + 1),
            'Persistent ID': track.itunes_id,
            'Location': (libraryPath / track.filename).as_uri(),
            'Name': '{} ({})'.format(
                track.tracktitle.get_text(Spelling.romaji),
                '|'.join(
                    role.get_text(Spelling.romaji) for role in track.roles
                )
            ),
            'Artist': track.artist.get_text(Spelling.romaji),
            'Album': track.album.get_text(Spelling.romaji),
            'Total Time': track.length / 1000,
            'Description': track.label.get_text(Spelling.romaji),
            'Composer': track.composer.get_text(Spelling.romaji),
            'Episode': episode_map.get(track.inmyriad, track.inmyriad),
            'Date Added': datetime.strptime(track.dateadded, "%Y-%m-%d %H:%M"),
            'Year': track.year
        }
    try:
        with open(fileName, 'wb') as f:
            plistlib.dump({'Tracks': tracks}, f)
    except Exception:
        pass
