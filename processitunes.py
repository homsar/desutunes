import plistlib
from processfile import metadata, part
from urllib.parse import urlparse, unquote
from datetime import datetime, timezone

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
