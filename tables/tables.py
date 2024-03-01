from sqlalchemy import CheckConstraint
from sqlalchemy import Column, BigInteger, Date, String, TIME, Boolean, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship

from .M2Ms import *


__all__ = ['Person', 'Album', 'Artist', 'Playlist', 'Genre', 'Song']


class Person(Base):
    __tablename__ = 'Person'

    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)

    playlists = relationship('Playlist', secondary="Person2Playlist", back_populates='persons')
    albums = relationship('Album', secondary="Person2Album", back_populates='persons')


class Playlist(Base):
    __tablename__ = 'Playlist'
    playlist_name = Column(String, nullable=False)
    creation_date = Column(Date, nullable=False)
    image = Column(LargeBinary, nullable=False)

    persons = relationship('Person', secondary="Person2Playlist", back_populates='playlists')
    songs = relationship('Song', secondary="Song2Playlist", back_populates='playlists')


class Genre(Base):
    __tablename__ = 'Genre'

    genre_name = Column(String, nullable=False)
    songs = relationship("Song", back_populates="genre")


class Album(Base):
    __tablename__ = 'Album'
    album_name = Column(String, nullable=False)
    drop_date = Column(Date, nullable=False)
    image = Column(LargeBinary, nullable=False)

    persons = relationship('Person', secondary="Person2Album", back_populates='albums')
    artists = relationship('Artist', secondary="Album2Artist", back_populates='albums')
    songs = relationship("Song", back_populates="album")


class Song(Base):
    __tablename__ = 'Song'
    song_name = Column(String, nullable=False)
    duration = Column(TIME, nullable=False)
    lyrics = Column(String)
    is_podcast = Column(Boolean, nullable=False)
    image = Column(LargeBinary, nullable=False)
    audio = Column(LargeBinary, nullable=False)
    # genre_id = Column('genre_id', BigInteger, ForeignKey(Genre.id), backref='songs')

    #one2many
    genre_id = Column(BigInteger, ForeignKey("Genre.id"))
    genre = relationship("Genre", back_populates="songs")

    album_id = Column(BigInteger, ForeignKey("Album.id"))
    album = relationship("Album", back_populates="songs")

    #many2many
    playlists = relationship('Playlist', secondary="Song2Playlist", back_populates='songs')
    artists = relationship('Artist', secondary="Song2Artist", back_populates='songs')


class Artist(Base):
    __tablename__ = 'Artist'
    __table_args__ = (
        CheckConstraint('number_of_auditions > 0'),
    )

    artist_name = Column(String, nullable=False)
    number_of_auditions = Column(BigInteger, nullable=False)
    image = Column(LargeBinary, nullable=False)

    songs = relationship('Song', secondary="Song2Artist", back_populates='artists')
    albums = relationship('Album', secondary="Album2Artist", back_populates='artists')

