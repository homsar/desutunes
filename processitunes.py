import plistlib
import pathlib
from processfile import metadata, part
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

    for tid, track in plist['Tracks'].items():
        if not track['Location'].startswith('file'):
            continue
        inMyriad = track.get('Episode', 'Yes')
        if inMyriad.lower() == 'not in myriad':
            inMyriad = "NO"
            
        title, anime, role, rolequal = part(track['Name'])
        
        track_metadata = metadata(
            ID=track['Persistent ID'],
            Filename=unquote(urlparse(track['Location']).path),
            Tracktitle=title,
            Album=track.get('Album', ''),
            Length=track['Total Time'],
            Anime=anime,
            Role=role,
            Rolequalifier=rolequal,
            Artist=track['Artist'],
            Composer=track.get('Composer', ''),
            Label=track.get('Description', ''),
            InMyriad=inMyriad,
            Dateadded=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
            )
        tracks.append(track_metadata)
    return tracks

def exportXML(model, fileName):
    tracks = {}
    episode_map = {
        'NO': 'NOT IN MYRIAD',
        'Yes': ''
        }
    for i in range(model.rowCount()):
        r = model.record(i)
        tracks[str(i)] = {
                'Track ID': str(i+1),
                'Persistent ID': r.value('ID'),
                'Location': pathlib.Path(r.value('Filename')).as_uri(),
                'Name': '{} ({} {}{}{})'.format(
                    r.value('Tracktitle'),
                    r.value('Anime'),
                    r.value('Role'),
                    '' if r.value('Rolequant') == '' else ' ',
                    r.value('Rolequant')
                    ),
                'Artist': r.value('Artist'),
                'Album': r.value('Album'),
                'Total Time': r.value('Length') / 1000,
                'Description': r.value('Label'),
                'Composer': r.value('Composer'),
                'Episode': episode_map.get(
                    r.value('InMyriad'),
                    r.value('InMyriad')
                    ),
                'Date Added': datetime.strptime(
                    r.value('DateAdded'),
                    "%Y-%m-%d %H:%M"
                    )
                }
    try:
        with open(fileName, 'wb') as f:
            plistlib.dump({'Tracks': tracks}, f)
    except Exception:
        pass
