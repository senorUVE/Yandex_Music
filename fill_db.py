import random
import names as fio_names
import datetime
import sqlalchemy as sa
import faker
import string

from tables.tables import *
from pg import make_connector

db = make_connector()
en_faker = faker.Faker('en-US')
ru_faker = faker.Faker('ru-RU')

ARTIST_COUNT = 40
MAX_ALBUM_COUNT = 10  # minimum is 5
MAX_SONGS_IN_ALBUM = 15  # minimum is 1

PERSON_COUNT = 1000
MAX_PLAYLISTS_COUNT = 10  # minimum is 1
MAX_SONGS_IN_PLAYLIST = 10  # minimum is 1

GENRES = ['Блюз', 'Вокальная музыка', 'Джаз', 'Джангл', 'Инструментальная музыка', 'Кантри',
          'Классическая музыка', 'Блэк-метал', 'Брутальный дэт-метал', 'Грайндкор', 'Дэт-метал',
          'Дэтграйнд', 'Дэткор', 'Мелодичный дэт-метал', 'Металкор', 'Прогрессив-метал',
          'Хеви-метал', 'Этническая музыка', 'Регги', 'Рок', 'Альтернативный рок', 'Гранж', 'Панк',
          'Рок-н-Ролл', 'Ска', 'Фолк', 'Хип-хоп', 'Шансон', 'Электронная музыка', 'Драм-н-Бэйс',
          'Транс', 'Техно', 'Хаус', 'Хард-кор', 'Электро', 'Прикладная музыка', 'Салунная музыка',
          'Аутентичная музыка', 'Функциональная музыка', 'Ритм-н-Блюз', 'Рэп']


def get_binary_sequence():
    return random.randbytes(random.randrange(100, 150))


def get_duration(is_podcast):
    if is_podcast:
        return datetime.timedelta(seconds=random.randrange(100, 400))
    return datetime.timedelta(seconds=random.randrange(1000, 4000))


def get_random_date(first_year=1900):
    year = random.randint(first_year, 2022)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return datetime.date(year, month, day)


def get_song_names():
    for row in open('utils/gpt-created_names.txt', 'r'):
        yield row.replace('\n', '').strip('"')


def create_genres():
    genre_instances = [Genre(genre_name=genre) for genre in GENRES]
    with db.get_master_session() as session:
        if session.query(sa.func.count(Genre.id)).scalar() == 0:
            session.add_all(genre_instances)
    return genre_instances


def create_artists():
    artists = [Artist(
        artist_name=fio_names.get_full_name(),
        number_of_auditions=random.randrange(10 ** 7),
        image=get_binary_sequence()
    ) for _ in range(ARTIST_COUNT)]

    with db.get_master_session() as session:
        session.add_all(artists)

    return artists


def create_albums_with_songs(genre_instances, artists):
    song_names = get_song_names()
    all_songs, all_albums = [], []
    is_podcast = random.randrange(10) == 0
    for main_artist in artists:
        for _ in range(random.randrange(5, MAX_ALBUM_COUNT + 1)):
            # create album
            album = Album(
                album_name=next(song_names),
                drop_date=get_random_date(),
                image=get_binary_sequence()
            )
            main_genre = random.choice(genre_instances)
            album_artists = {main_artist}
            # create songs
            songs = []
            for _ in range(random.randrange(1, MAX_SONGS_IN_ALBUM + 1)):
                song_name = next(song_names)
                song = Song(
                    song_name=song_name, duration=get_duration(is_podcast),
                    lyrics=en_faker.text(), is_podcast=is_podcast,
                    image=get_binary_sequence(), audio=get_binary_sequence(),
                    genre=(main_genre if random.randrange(5) != 0 else random.choice(
                        genre_instances)) if is_podcast else None,
                    album=album
                )
                if random.randrange(5) == 0:
                    feat_artist = random.choice(artists)
                    album_artists.add(feat_artist)
                    song.artists = list({feat_artist, main_artist})
                else:
                    song.artists = [main_artist]
                songs.append(song)
            album.artists = list(album_artists)
            # fill_db
            with db.get_master_session() as session:
                session.add_all(songs + [album])
            all_songs.extend(songs)
            all_albums.append(album)
    return all_songs, all_albums


def create_persons():
    persons = [Person(
        full_name=ru_faker.unique.name(),
        phone_number=ru_faker.unique.phone_number(),
        password=''.join(random.choices(string.printable, k=random.randrange(8, 30))),
        email=en_faker.unique.email(),
    ) for _ in range(PERSON_COUNT)]

    return persons


def create_playlists(persons, albums, songs):
    for person in persons:
        person_playlists = []  # у каждого человека будет просто плейлист любимых песен

        # добавим парочку любимых альбомов
        if favourite_albums_count := random.randrange(4):
            person.albums = random.sample(albums, favourite_albums_count)

        # а теперь и плейлистов накидаем чувачку
        for person_playlist_number in range(random.randrange(1, MAX_PLAYLISTS_COUNT)):
            playlist = Playlist(
                playlist_name='favourite songs' if person_playlist_number == 0 else ru_faker.word(),
                creation_date=get_random_date(first_year=2020),
                image=get_binary_sequence(),
            )
            playlist.songs = random.sample(songs, random.randrange(1, MAX_SONGS_IN_PLAYLIST))
            person_playlists.append(playlist)

        person.playlists = person_playlists

        with db.get_master_session() as session:
            session.add_all([person] + person_playlists)


def fill_db():
    genre_instances = create_genres()
    artists = create_artists()
    songs, albums = create_albums_with_songs(genre_instances, artists)
    persons = create_persons()
    create_playlists(persons, albums, songs)
