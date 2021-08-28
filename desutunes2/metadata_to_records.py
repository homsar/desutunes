#!/usr/bin/env python

from sqlalchemy import select

from .db import ensure_session, Artist, MetaArtist, MetaArtistComponent, PronouncableThing, Session
from .processfile import roledata


@ensure_session
def metaartist_from_artist_string(metaartist_text: str,
                                  session: Session) -> MetaArtist:
    metaartist = MetaArtist()
    for index, (is_artist, component_text) in enumerate(
            parse_artist(metaartist_text)
    ):
        if is_artist:
            if (artist := session.execute(
                    select(Artist)
                    .join(PronouncableThing)
                    .where(romaji=component_text)
            ).one_or_none()) is None:
                artist = Artist(
                    name=PronouncableThing(romaji=component_text)
                )
            component = MetaArtistComponent(
                metaartist=metaartist,
                artist=artist,
                ordering=index)
        else:
            component = MetaArtistComponent(
                metaartist=metaartist,
                text=PronouncableThing(romaji=component_text),
                ordering=index
            )
    return metaartist


@ensure_session
def get_or_create_by_romaji(cls, romaji: str, *, session: Session):
    return session.execute(
        select(cls)
        .join(PronouncableThing)
        .where(PronouncableThing.romaji == romaji)
    ).scalars().one_or_none()


@ensure_session
def add_records_from_metadata(records: list[roledata], *,
                              session: Session) -> None:
    all_metaartists = {
        metaartist.get_text(Spelling.romaji): metaartist
        for metaartist in session.execute(select(MetaArtist)).scalars().all()
    }
    for record in records:
        if (metaartist := all_metaartists.get(record.Artist)) is None:
            metaartist = metaartist_from_artist_string(record.Artist)
            all_metaartists[record.Arist] = metaartist

        if (composer := all_metaartists.get(record.Composer)) is None:
            composer = metaartist_from_artist_string(record.Composer)
            all_metaartists[record.Composer] = composer

        if (album := get_by_romaji(Album,
                                   record.Album,
                                   session=session)) is None:
            album = Album(title=PronouncableThing(romaji=record.Album))

        if (label := get_by_romaji(Label,
                                   record.Label,
                                   session=session)) is None:
            label = Label(name=PronouncableThing(romaji=record.Label))

        track = Track(
            itunes_id=record.ID,
            filename=record.Filename,
            tracktitle=PronouncableThing(romaji=record.Tracktitle),
            artist=metaartist,
            album=album,
            length=record.Length,
            composer=composer,
            inmyriad=record.InMyriad,
            dateadded=record.Dateadded,
            label=label,
            year=record.Year
        )

        for role_data in record.Roles:
            if (anime := get_by_romaji(Anime,
                                       role_data.anime,
                                       session=session)) is None:
                anime = Anime(title=PronouncableThing(romaji=role_data.anime))

            session.add(Role(
                anime=anime,
                track=track,
                kind=role_data.kind,
                specifics=PronouncableThing(romaji=role_data.specifics)
            ))
    session.commit()
