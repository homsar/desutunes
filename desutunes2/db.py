#!/usr/bin/env python

import enum
from pathlib import Path

from sqlalchemy import Column, String, Integer, Float, DateTime, Enum
from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy import create_engine, select
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property

from .settinsg import DATABASE_LOCATION, LIBRARY_LOCATION

Base = declarative_base()

class Track(Base):
    '''A single track, that has played a role in an anime.'''
    __tablename__ = 'track'
    id = Column(Integer, primary_key=True)
    itunes_id = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    tracktitle_id = Column(Integer, ForeignKey('pronouncable_thing.id'),
                           nullable=True)
    artist_id = Column(Integer, ForeignKey('metaartist.id'), nullable=True)
    album_id = Column(Integer, ForeignKey('album.id'), nullable=True)
    length = Column(Integer, nullable=True)
    composer_id = Column(Integer, ForeignKey('metaartist.id'), nullable=True)
    inmyriad = Column(String, nullable=True)
    dateadded = Column(String, nullable=False)
    year = Column(Integer, nullable=True)
    label_id = Column(Integer, ForeignKey('label.id'), nullable=True)

    tracktitle = relationship("PronouncableThing")
    artist = relationship("MetaArtist",
                          foreign_keys=[artist_id])
    album = relationship("Album", back_populates="tracks")
    composer = relationship("MetaArtist",
                            foreign_keys=[composer_id])
    label = relationship("Label", back_populates="tracks")
    roles = relationship("Role", back_populates="track")

    __table_args__ = (UniqueConstraint('itunes_id', name='_unique_itunesid'),)

    @property
    def file(self):
        return LIBRARY_LOCATION / self.filename

    @property
    def is_in_library(self):
        return self.file.exists()


class Artist(Base):
    '''A single artist - e.g. a composer, band, or person.'''
    __tablename__ = 'artist'
    id = Column(Integer, primary_key=True)
    name_id = Column(Integer, ForeignKey('pronouncable_thing.id'), nullable=True)

    name = relationship("PronouncableThing")


class ValidRole(enum.Enum):
    '''Enumerates roles that tracks can play in shows.'''

    # TODO: Is flattening insert song/track and theme/main_theme OK?
    # This is lossy.

    op = 1
    ed = 2
    character_song = 3
    insert_song = 4
    insert_track = 4
    main_theme = 5
    theme = 5
    bgm = 6
    ost = 7


role_spellings = {
    ValidRole.op: 'OP',
    ValidRole.ed: 'ED',
    ValidRole.character_song: 'Character Song',
    ValidRole.insert_song: 'Insert Song',
    ValidRole.main_theme: 'Main Theme',
    ValidRole.bgm: 'BGM',
    ValidRole.ost: 'OST'
}


class Spelling(enum.Enum):
    '''Enumerates ways of spelling things that are considered in this code.'''
    romaji = 1
    original = 2
    pronunciation = 3


class Role(Base):
    '''A role that has been played by a specific track in a specific anime.'''
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    anime_id = Column(Integer, ForeignKey('anime.id'), nullable=False)
    kind = Column(Enum(ValidRole), nullable=True)
    specifics__id = Column(Integer,
                           ForeignKey('pronouncable_thing.id'),
                           nullable=True)
    track_id = Column(Integer,
                      ForeignKey('track.id', ondelete="CASCADE"),
                      nullable=False)

    anime = relationship("Anime", back_populates="roles")
    specifics = relationship("PronouncableThing")
    track = relationship("Track", back_populates="roles")

    def get_text(self, spelling: Spelling):
        return '{} {}{}'.format(
            self.anime.get_text(spelling),
            role_spellings[self.kind],
            self.specifics.get_text(spelling)
        )


class Label(Base):
    '''A record label.'''
    __tablename__ = 'label'
    id = Column(Integer, primary_key=True)
    name_id = Column(Integer, ForeignKey('pronouncable_thing.id'), nullable=False)

    name = relationship("PronouncableThing")
    tracks = relationship("Track", back_populates="label")


class Album(Base):
    '''An album is a group of songs or other tracks released as a single
    bundle.'''
    __tablename__ = 'album'
    id = Column(Integer, primary_key=True)
    title_id = Column(Integer,
                      ForeignKey('pronouncable_thing.id'),
                      nullable=False)
    year = Column(Integer, nullable=True)

    title = relationship("PronouncableThing")
    tracks = relationship("Track", back_populates="album")


class Anime(Base):
    '''An anime is an animated film, OVA, ONA, or TV show that was produced for
    release in Japan.'''
    __tablename__ = 'anime'
    id = Column(Integer, primary_key=True)
    title_id = Column(Integer,
                      ForeignKey('pronouncable_thing.id'),
                      nullable=False)

    title = relationship("PronouncableThing")
    roles = relationship("Role", back_populates="anime")


class PronouncableThing(Base):
    '''A piece of text that can be read aloud. For example, the name of an
    artist, anime, or record label. Stores the romanisation, the original
    language rendition, and a pronunciation (e.g. in kana).'''
    __tablename__ = 'pronouncable_thing'
    id = Column(Integer, primary_key=True)
    romaji = Column(String)
    original = Column(String)
    pronunciation = Column(String)

    def get_text(self, spelling: Spelling, fallback: bool = True) -> str:
        '''Get the text of the pronouncable thing for the specified spelling.
        If it doesn't exist, then optionally fall back with the priority
        romaji > original > pronunciation.'''
        ret = None
        if self.pronunciation is not None:
            if spelling == Spelling.pronunciation:
                return self.pronunciation
            if fallback:
                ret = self.pronunciation

        if self.original is not None:
            if spelling == Spelling.original:
                return self.original
            if fallback:
                ret = self.original

        if self.romaji is not None:
            if spelling == Spelling.romaji:
                return self.romaji
            if fallback:
                ret = self.romaji

        if ret:
            return ret
        else:
            raise ValueError("No text found for this pronouncable thing.")


class MetaArtist(Base):
    '''A metaartist is the full attribution for a given work, and includes one
    or more artists, and text to join them together. For example,
    "ROUND TABLE featuring NINO" comprises the artists "ROUND TABLE" and
    "NINO", and the text " featuring ".'''
    __tablename__ = 'metaartist'
    id = Column(Integer, primary_key=True)
    components = relationship(
        'MetaArtistComponent',
        order_by='MetaArtistComponent.ordering'
    )

    def get_text(self, spelling: Spelling):
        return ''.join([
            component.get_text(spelling)
            for component in self.components
        ])


class MetaArtistComponent(Base):
    '''A single part of a metaartist. Either an artist (optionally
    with an alternative spelling), or a piece of text.'''
    __tablename__ = 'metaartist_component'
    id = Column(Integer, primary_key=True)
    metaartist_id = Column(Integer,
                           ForeignKey('metaartist.id', ondelete="CASCADE"),
                           nullable=False)
    ordering = Column(Integer, nullable=False)
    artist_id = Column(Integer, ForeignKey('artist.id'), nullable=True)
    text_id = Column(Integer,
                     ForeignKey('pronouncable_thing.id'),
                     nullable=True)

    metaartist = relationship("MetaArtist", back_populates="components")
    artist = relationship("Artist")
    text = relationship("PronouncableThing")

    __table_args__ = (
        CheckConstraint(
            '((artist_id != NULL) OR (text_id != NULL))',
            name='ck_metaartist_component_has_content'),
        UniqueConstraint('metaartist_id', 'ordering',
                         name='_definitive_metaartist_ordering')
    )

    def get_text(self, spelling: Spelling):
        if self.text:
            return self.text
        else:
            return artist.name.get_text(spelling)



engine = create_engine(DATABASE_LOCATION, future=True)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


def ensure_session(func):
    def wrapped_func(*args, session=None, **kwargs):
        if session:
            return func(*args, session=session, **kwargs)
        else:
            session = Session(expire_on_commit=False)
            try:
                result = func(*args, session=session, **kwargs)
                session.commit()
                session.close()
                return result
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

    return wrapped_func
