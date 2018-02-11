from PyQt5.QtCore import QFileInfo, QDir
from collections import namedtuple
from tablemodel import headers
from mutagen import easyid3, id3, easymp4, mp4, flac
from random import choice
from datetime import datetime, timezone
import re

metadata = namedtuple("metadata", 
                      [header.replace(' ', '') for header in headers])
_blank = [""]

def random_id():
    '''Generate a random string that looks like an iTunes track identifier.
    16 digits, 16 values, so 16^16 possible combinations.
    For a 2500-song library, chance of collision is about 1e-16.'''

    hex_digits = "0123456789ABCDEF"
    return "".join([choice(hex_digits) for _ in range(16)])

def split_id3_title(id3_title):
    """
    Take a 'Title (role)'-style ID3 title and return (title, role)
    from https://github.com/colons/nkd.su/blob/230a68e2f7231a3b8e80dea9f2a628d637b0792e/nkdsu/apps/vote/utils.py
    """
    role = None

    bracket_depth = 0
    for i in range(1, len(id3_title)+1):
        char = id3_title[-i]
        if char == ')':
            bracket_depth += 1
        elif char == '(':
            bracket_depth -= 1

        if bracket_depth == 0:
            if i != 1:
                role = id3_title[len(id3_title)-i:]
            break

    if role:
        title = id3_title.replace(role, '').strip()
        role = role[1:-1]  # strip brackets
    else:
        title = id3_title

    return title, role

def role_detail(role):
    '''Split up a role into constituent components.
    Based loosely on https://github.com/colons/nkd.su/blob/19680bbe243aabdb8049f43cdad096362cc8c4dc/nkdsu/apps/vote/models.py'''

    if role is None:
        return {}
    
    return re.match(
        r'^(?P<anime>.*?) ?\b'
        r'(?P<rolepre>(rebroadcast)?) ?'
        r'\b(?P<role>'
        
        r'(ED|OP|(character|image) song\b|'
        r'(insert (track|song)\b)|ins|'
        r'(main )?theme|bgm|ost))'
        r' ?'
        r'(?P<rolepost>.*)$',
        role,
        flags=re.IGNORECASE,
    ).groupdict()


def part(trackTitle):
    '''Take a trackTitle and return its component parts: 
     - the track title proper
     - the anime from which it comes
     - the role in said anime
     - any qualifier on that role (e.g. if role is ED, then which number/season/episode'''
    
    title, full_role = split_id3_title(trackTitle)
    role_components = role_detail(full_role)
    if role_components['rolepre'] == '' or role_components['rolepost'] == '':
        rolequal = role_components['rolepre'] + role_components['rolepost']
    else:
        rolequal = ', '.join(role_components['rolepre'], 
                             role_components['rolepost'])
    if len(role_components['role']) == 2:
        role = role_components['role'].upper()
    else:
        role = role_components['role'].lower()
    return title, role_components['anime'], role, rolequal

def getMetadataForFileList(filenames):
    '''Takes a list of filenames, returns a list of metadata associated with
    all files in that list that are readable tracks'''

    metadata = []
    for filename in filenames:
        info = QFileInfo(filename)
        if info.isDir() and info.isExecutable():
            dir = QDir(filename)
            metadata.extend(processFileList(dir.entryList(
                        QDir.NoDotAndDotDot
                        )))
        elif info.isFile() and info.isReadable():
            metadata.extend(processFile(filename, info))
    return metadata

def processid3(filename):
    '''Reads metadata from tracks that use the ID3 format - MP3, AAC'''

    f = easyid3.EasyID3(filename)
    title, anime, role, rolequal = part(f.get('title', _blank)[0])
    label = f.get('label', _blank)[0]
    if not label:
        f_complex = id3.ID3(filename)
        case_map = {name.lower(): name
                    for name in f_complex}
        to_try = ['tit3', 'txxx:subtitle', 'txxx:label', 'txxx:description']
        for field in to_try:
            if field in case_map:
                label = f_complex[case_map[field]].text[0]
                break
        else:
            return []
    
    return [metadata(
        ID=random_id(),
        Filename=filename,
        Tracktitle=title,
        Anime=anime,
        Role=role,
        Rolequalifier=rolequal,
        Artist=f.get('artist', _blank)[0],
        Composer=f.get('composer', _blank)[0],
        Label=label,
        InCatsystem=False,
        Dateadded=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        )]

def processm4a(filename):
    '''Reads metadata from MPEG-4 audio files'''

    f = easymp4.EasyMP4(filename)
    title, anime, role, rolequal = part(f.get('title', _blank)[0])
    artist = f.get('artist', _blank)[0]
    label = f.get('description', _blank)[0]

    f = mp4.MP4(filename)
    composer = f.get('©wrt', _blank)
    return [metadata(
        ID=random_id(),
        Filename=filename,
        Tracktitle=title,
        Anime=anime,
        Role=role,
        Rolequalifier=rolequal,
        Artist=artist,
        Composer=composer,
        Label=label,
        InCatsystem=False,
        Dateadded=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        )]


def processflac(filename):
    '''Reads metadata from FLAC files'''

    f = flac.FLAC(filename)
    title, anime, role, rolequal = part(f.get('title', _blank)[0])
    label = f.get('description', _blank)[0]
    if not label:
        label = f.get('subtitle', _blank)[0]

    return [metadata(
        ID=random_id(),
        Filename=filename,
        Tracktitle=title,
        Anime=anime,
        Role=role,
        Rolequalifier=rolequal,
        Artist=artist,
        Composer=composer,
        Label=label,
        InCatsystem=False,
        Dateadded=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        )]

def processFile(filename, info):
    suffix = info.suffix().lower()
    processors = {
        'mp3': processid3, 
        'aac': processid3,
        'm4a': processm4a, 
        'flac': processflac
        }
    if suffix not in processors:
        return []
    else:
        return processors[suffix](filename)
    
