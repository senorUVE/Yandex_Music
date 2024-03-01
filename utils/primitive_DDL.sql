CREATE TABLE "Person"(
    Id serial NOT NULL PRIMARY KEY,
    Full_name VARCHAR NOT NULL,
    phone_number VARCHAR NOT NULL,
    password VARCHAR NOT NULL,
    email VARCHAR NOT NULL,
    unique (phone_number,email)
);

create table "Playlist"(
    Id bigserial NOT NULL PRIMARY KEY,
    playlist_name VARCHAR NOT NULL,
    creation_date date NOT NULL,
    image bytea NOT NULL
);

create table "Genre"(
    Id serial NOT NULL PRIMARY KEY,
    genre_name VARCHAR NOT NULL
);

create table "Album"(
    Id bigserial NOT NULL PRIMARY KEY,
    album_name VARCHAR NOT NULL,
    drop_date date NOT NULL,
    image bytea NOT NULL
);

create table "Song"(
    Id bigserial NOT NULL PRIMARY KEY,
    song_name VARCHAR NOT NULL,
    duration time NOT NULL,
    lyrics VARCHAR,
    is_podcast bool NOT NULL,
    image bytea NOT NULL,
    audio bytea NOT NULL,
    Album_id int references "Album"(Id) on delete cascade on update cascade,
    Genre_id int references "Genre"(Id) on delete set null on update cascade
);

create table "Artist"(
    Id serial NOT NULL PRIMARY KEY,
    artist_name VARCHAR NOT NULL,
    number_of_auditions int NOT NULL check ( number_of_auditions > 0 ),
    image bytea NOT NULL
);

create table "Person2Playlist"(
    Id bigserial NOT NULL PRIMARY KEY,
    Person_id int references "Person"(Id) on delete cascade,
    Playlist_id int references "Playlist"(Id) on delete cascade
);

create table "Person2Album"(
    Id bigserial NOT NULL PRIMARY KEY,
    Person_id int references "Person"(Id) on delete cascade,
    Album_id int references "Album"(Id) on delete cascade
    );

create table "Song2Playlist"(
    Id bigserial NOT NULL PRIMARY KEY,
    Song_id int references "Song"(Id) on delete cascade,
    Playlist_id int references "Playlist"(Id) on delete cascade
);

create table "Song2Artist"(
    -- cuz song can have multiple authors
    Id bigserial NOT NULL PRIMARY KEY,
    Song_id int references "Song"(Id) on delete cascade,
    Artist_id int references "Artist"(Id) on delete cascade
);

create table "Album2Artist"(
    Id bigserial NOT NULL PRIMARY KEY,
    Artist_id int references "Artist"(Id) on delete cascade,
    Album_id int references "Album"(Id) on delete cascade
);