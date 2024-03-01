from sqlalchemy import Column, ForeignKey, BigInteger, Table
from sqlalchemy.orm import DeclarativeBase

__all__ = [
    'Base',
    'Person2Playlist',
    'Person2Album',
    'Song2Playlist',
    'Album2Artist',
    'Song2Artist'
]


class Base(DeclarativeBase):
    __abstract__ = True
    id = Column(BigInteger, primary_key=True, nullable=False, autoincrement=True)



Person2Playlist = Table('Person2Playlist', Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('person_id', BigInteger, ForeignKey('Person.id')),
    Column('playlist_id', BigInteger, ForeignKey('Playlist.id'))
)

Person2Album = Table('Person2Album', Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('person_id', BigInteger, ForeignKey('Person.id', ondelete='CASCADE')),
    Column('album_id', BigInteger, ForeignKey('Album.id', ondelete='CASCADE'))
)

Song2Playlist = Table('Song2Playlist', Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('song_id', BigInteger, ForeignKey('Song.id', ondelete='CASCADE')),
    Column('playlist_id', BigInteger, ForeignKey('Playlist.id', ondelete='CASCADE'))
)

Song2Artist = Table('Song2Artist', Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('song_id', BigInteger, ForeignKey('Song.id', ondelete='CASCADE')),
    Column('artist_id', BigInteger, ForeignKey('Artist.id', ondelete='CASCADE'))
)

Album2Artist = Table('Album2Artist', Base.metadata,
    Column('id', BigInteger, primary_key=True),
    Column('album_id', BigInteger, ForeignKey('Album.id', ondelete='CASCADE')),
    Column('artist_id', BigInteger, ForeignKey('Artist.id', ondelete='CASCADE'))
)
