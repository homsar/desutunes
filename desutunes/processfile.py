from PyQt5.QtCore import QFileInfo, QDir
from collections import namedtuple
from functools import partial
from .tablemodel import headers
from mutagen import easyid3, id3, mp3, easymp4, mp4, aac, flac
from random import choice
from datetime import datetime, timezone
from pathlib import Path
import re

metadata = namedtuple("metadata",
                      [header.replace(' ', '')
                       for header in headers + ['OriginalFileName']])
_blank = [""]
_unknown = ["Unknown Artist"]
_nullroledetail = {'anime': '', 'role': '', 'rolepre': '', 'rolepost': ''}


def random_id():
    '''Generate a random string that looks like an iTunes track identifier.
    16 digits, 16 values, so 16^16 possible combinations.
    For a 2500-song library, chance of collision is about 1e-16.'''

    hex_digits = "0123456789ABCDEF"
    return "".join([choice(hex_digits) for _ in range(16)])


def split_id3_title(id3_title):
    '''Take a 'Title (role)'-style ID3 title and return (title, role)
    from https://git.io/vxJtU'''

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
    Based loosely on https://git.io/vxJtt'''

    if role is None or role == '':
        return _nullroledetail

    try:
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
    except Exception as ex:
        return {**_nullroledetail, **{'rolepost': role}}


def part(trackTitle):
    '''Take a trackTitle and return its component parts:
     - the track title proper
     - the anime from which it comes
     - the role in said anime
     - any qualifier on that role (e.g. if role is ED,
       then which number/season/episode'''

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


def sanitize(text):
    return text.replace('/', '').replace('\\', '').replace('\n', '')


def canonicalFileName(id, artist, title, extension):
    return Path(sanitize(artist)) / f'{sanitize(title)} ({id}).{extension}'


def getMetadataForFileList(filenames):
    '''Takes a list of filenames, returns a list of metadata associated with
    all files in that list that are readable tracks'''

    metadata = []
    for filename in filenames:
        info = QFileInfo(filename)
        if info.isDir() and info.isExecutable():
            print(filename)
            dir = QDir(filename)
            print(dir.entryList(QDir.AllEntries | QDir.NoDotAndDotDot))
            metadata.extend(getMetadataForFileList(
                    [i.filePath()
                     for i in dir.entryInfoList(
                             QDir.AllEntries | QDir.NoDotAndDotDot
                     )]))
        elif info.isFile() and info.isReadable():
            print(filename)
            metadata.extend(processFile(filename))
    return metadata


def processid3(filename, audioengine=mp3.MP3):
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

    artist = f.get('artist', _unknown)[0]
    af = audioengine(filename)
    id = random_id()

    return [metadata(
        ID=id,
        OriginalFileName=filename,
        Filename=canonicalFileName(id, artist, title, filename[-3:]),
        Tracktitle=title,
        Album=f.get('album', _blank)[0],
        Length=int(af.info.length * 1000),
        Anime=anime,
        Role=role,
        Rolequalifier=rolequal,
        Artist=f.get('artist', _blank)[0],
        Composer=f.get('composer', _blank)[0],
        Label=label,
        InMyriad="NO",
        Dateadded=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        )]


def processm4a(filename):
    '''Reads metadata from MPEG-4 audio files'''

    f = easymp4.EasyMP4(filename)
    title, anime, role, rolequal = part(f.get('title', _blank)[0])
    artist = f.get('artist', _blank)[0]
    fn_artist = artist if artist else 'Unknown Artist'
    label = f.get('description', _blank)[0]
    album = f.get('album', _blank)[0]
    id = random_id()

    f = mp4.MP4(filename)
    composer = f.get('©wrt', _blank)[0]
    return [metadata(
        ID=id,
        OriginalFileName=filename,
        Filename=canonicalFileName(id, fn_artist, title, 'm4a'),
        Tracktitle=title,
        Album=album,
        Length=int(f.info.length * 1000),
        Anime=anime,
        Role=role,
        Rolequalifier=rolequal,
        Artist=artist,
        Composer=composer,
        Label=label,
        InMyriad="NO",
        Dateadded=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        )]


def processflac(filename):
    '''Reads metadata from FLAC files'''

    f = flac.FLAC(filename)
    title, anime, role, rolequal = part(f.get('title', _blank)[0])
    label = f.get('description', _blank)[0]
    if not label:
        label = f.get('subtitle', _blank)[0]
    album = f.get('album', _blank)[0]
    artist = f.get('artist', _blank)[0]
    fn_artist = artist if artist else 'Unknown Artist'
    id = random_id()

    return [metadata(
        ID=id,
        OriginalFileName=filename,
        Filename=canonicalFileName(id, artist, title, 'flac'),
        Tracktitle=title,
        Album=album,
        Length=int(f.info.length * 1000),
        Anime=anime,
        Role=role,
        Rolequalifier=rolequal,
        Artist=artist,
        Composer=f.get('composer', _blank)[0],
        Label=label,
        InMyriad="NO",
        Dateadded=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        )]


def processFile(filename):
    suffix = Path(filename).suffix.lower()
    processors = {
        '.mp3': processid3,
        '.aac': partial(processid3, audioengine=aac.AAC),
        '.m4a': processm4a,
        '.flac': processflac
        }
    if suffix not in processors:
        return []
    else:
        return processors[suffix](filename)
