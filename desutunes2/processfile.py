from PyQt5.QtCore import QFileInfo, QDir
from collections import namedtuple
from functools import partial
from .db import ValidRole
from mutagen import easyid3, id3, mp3, easymp4, mp4, aac, flac
from random import choice
from datetime import datetime, timezone
from pathlib import Path
import re
from sqlalchemy import select

roledata = namedtuple('roledata', ['anime', 'kind', 'specifics'])
metadata = namedtuple('metadata', [
    "ID", "OriginalFileName", "Filename", "Tracktitle", "Album", "Length",
    "Roles", "Artist", "Composer", "Label", "Year", "InMyriad", "Dateadded"
])
_blank = [""]
_unknown = ["Unknown Artist"]


def random_id():
    '''Generate a random string that looks like an iTunes track identifier.
    16 digits, 16 values, so 16^16 possible combinations.
    For a 2500-song library, chance of collision is about 1e-16.'''

    hex_digits = "0123456789ABCDEF"
    return "".join([choice(hex_digits) for _ in range(16)])


def split_id3_title(id3_title):
    '''Take a 'Title (role)'-style ID3 title and return (title_text, role_text)
    from https://git.io/vxJtU'''

    role_text = None

    bracket_depth = 0
    for i in range(1, len(id3_title) + 1):
        char = id3_title[-i]
        if char == ')':
            bracket_depth += 1
        elif char == '(':
            bracket_depth -= 1

        if bracket_depth == 0:
            if i != 1:
                role = id3_title[len(id3_title) - i:]
            break

    if role:
        title_text = id3_title.replace(role, '').strip()
        role_text = role[1:-1]  # strip brackets
    else:
        title_text = id3_title

    return title_text, role_text


def parse_role(role_text):
    '''Split up a role into constituent components.
    Based loosely on https://git.io/vxJtt'''

    if role_text is None or role_text == '':
        return None

    role_components = re.match(
        r'^(?P<anime>.*?) ?\b'
        r'(?P<rolepre>(rebroadcast)?) ?'
        r'\b(?P<role>'
        r'((ED|OP)(?=(\d|\b))|(character|image) song\b|'
        r'(insert (track|song)\b)|ins|'
        r'(main )?theme|bgm|ost))'
        r' ?'
        r'(?P<rolepost>.*)$',
        role_text,
        flags=re.IGNORECASE,
    ).groupdict()

    role = ValidRole[role_components['role'].lower().replace(' ', '_')]

    if role_components['rolepre'] == '' or role_components['rolepost'] == '':
        rolequal = role_components['rolepre'] + role_components['rolepost']
    else:
        rolequal = ', '.join((role_components['rolepre'],
                              role_components['rolepost']))

    return roledata(role_components['anime'], role, rolequal)


def parse_roles(all_roles):
    return tuple(
        parse_role(single_role)
        for single_role in all_roles.split('|')
        if single_role
    )


def part(trackTitle):
    '''Take a trackTitle and return its component parts:
     - the track title proper
     - a list of anime in which it features and what role(s) it plays '''

    title, full_role = split_id3_title(trackTitle)
    return title, parse_roles(full_role)


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
            metadata.extend(
                getMetadataForFileList([
                    i.filePath()
                    for i in dir.entryInfoList(QDir.AllEntries
                                               | QDir.NoDotAndDotDot)
                ]))
        elif info.isFile() and info.isReadable():
            print(filename)
            metadata.extend(processFile(filename))
    return metadata


def year_from_date_string(date_string):
    year_match = re.match(
        '(?:^|.*[^0-9])([0-9][0-9][0-9][0-9])(?:[^0-9]|$)',
        date_string
    )
    if year_match:
        return int(year_match.groups[0])
    else:
        return None


def processid3(filename, audioengine=mp3.MP3):
    '''Reads metadata from tracks that use the ID3 format - MP3, AAC'''

    f = easyid3.EasyID3(filename)
    title, roles = part(f.get('title', _blank)[0])
    if (label := f.get('label', _blank)[0]) is not None:
        f_complex = id3.ID3(filename)
        case_map = {name.lower(): name for name in f_complex}
        to_try = ['tit3', 'txxx:subtitle', 'txxx:label', 'txxx:description']
        for field in to_try:
            if field in case_map:
                label = f_complex[case_map[field]].text[0]
                break

    year = year_from_date_string(f.get('Date', [''])[0])

    artist = f.get('artist', _unknown)[0]
    af = audioengine(filename)
    id = random_id()

    return [
        metadata(
            ID=id,
            OriginalFileName=filename,
            Filename=canonicalFileName(id, artist, title, filename[-3:]),
            Tracktitle=title,
            Album=f.get('album', _blank)[0],
            Length=int(af.info.length * 1000),
            Roles=roles,
            Artist=f.get('artist', _blank)[0],
            Composer=f.get('composer', _blank)[0],
            Label=label,
            Year=year,
            InMyriad="NO",
            Dateadded=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        )
    ]


def processm4a(filename):
    '''Reads metadata from MPEG-4 audio files'''

    f = easymp4.EasyMP4(filename)
    title, roles = part(f.get('title', _blank)[0])
    artist = f.get('artist', _blank)[0]
    fn_artist = artist if artist else 'Unknown Artist'
    label = f.get('description', _blank)[0]
    album = f.get('album', _blank)[0]
    year = year_from_date_string(f.get('date', [''])[0])
    id = random_id()

    f = mp4.MP4(filename)
    composer = f.get('©wrt', _blank)[0]
    return [
        metadata(
            ID=id,
            OriginalFileName=filename,
            Filename=canonicalFileName(id, fn_artist, title, 'm4a'),
            Tracktitle=title,
            Album=album,
            Length=int(f.info.length * 1000),
            Roles=roles,
            Artist=artist,
            Composer=composer,
            Label=label,
            year=year,
            InMyriad="NO",
            Dateadded=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        )
    ]


def processflac(filename):
    '''Reads metadata from FLAC files'''

    f = flac.FLAC(filename)
    title, roles = part(f.get('title', _blank)[0])
    label = f.get('description', _blank)[0]
    if not label:
        label = f.get('subtitle', _blank)[0]
    album = f.get('album', _blank)[0]
    artist = f.get('artist', _blank)[0]
    fn_artist = artist if artist else 'Unknown Artist'
    year = year_from_date_string(f.get('date', [''])[0])
    id = random_id()

    return [
        metadata(
            ID=id,
            OriginalFileName=filename,
            Filename=canonicalFileName(id, artist, title, 'flac'),
            Tracktitle=title,
            Album=album,
            Length=int(f.info.length * 1000),
            Roles=roles,
            Artist=artist,
            Composer=f.get('composer', _blank)[0],
            Label=label,
            year=year,
            InMyriad="NO",
            Dateadded=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
        )
    ]


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
