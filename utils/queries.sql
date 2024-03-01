-- Запросы писал в формате: ну бля нужно как можно больше текста для препода
-- Есть маленькие проблемы: банально в сохранении .mp3 pg не самый лучший вариант

-- EASY
--1 Вывести отсортированные имена артистов, у которых меньше 70 песен

SELECT artist_name,
       count(*) "songs amount"
FROM "Artist"
         JOIN "Song2Artist" S2A ON "Artist".Id = S2A.Artist_id
         JOIN "Song" S ON S.Id = S2A.Song_id
GROUP BY artist_name
HAVING count(*) < 70
ORDER BY artist_name;

--2  5 Самых длинных по средней продолжительности пемен жанров, которые есть в избранном хотя бы у кого-то
WITH additional_table AS
         (SELECT song_name,
                 genre_name,
                 duration
          FROM "Song"
                   JOIN "Genre" ON "Song".Genre_id = "Genre".Id
                   RIGHT JOIN "Song2Playlist" S2P ON "Song".Id = S2P.Song_id
                   JOIN "Playlist" ON S2P.Playlist_id = "Playlist".Id
          WHERE playlist_name = 'favourite songs'
          GROUP BY song_name,
                   genre_name,
                   duration)
SELECT genre_name,
       avg(duration) average_duration
FROM additional_table
GROUP BY genre_name
ORDER BY average_duration desc
LIMIT 5;

-- 3 Поиск всех альбомов, выпущенных после 2010 года drop_date, и имеющих более 10 песен

SELECT "Album".album_name,
       drop_date
FROM "Album"
WHERE "Album".drop_date > '2010-01-01'::date
  AND
        (SELECT COUNT(*)
         FROM "Song"
         WHERE "Song".Album_id = "Album".Id ) > 10;

-- 4  песни, где в тексте встречается слово любовь
SELECT DISTINCT (song_name),
               lyrics
FROM "Song"
         JOIN "Song2Artist" S2A ON "Song".Id = S2A.Song_id
         JOIN "Artist" ON S2A.Artist_id = "Artist".Id
WHERE "Song".lyrics ILIKE '%love%'
   OR "Song".song_name ILIKE '%love%';

-- 5 Найти всех пользователей, у которых электронная почта (email) оканчивается на ".org"
-- и номер начинается на +7 и имеют плейлисты, созданные после лета 2022

SELECT DISTINCT ("Person".Full_name), "Person".email,
                "Person".phone_number
FROM "Person"
         JOIN "Person2Playlist" ON "Person".Id = "Person2Playlist".Person_id
         JOIN "Playlist" ON "Person2Playlist".Playlist_id = "Playlist".Id
WHERE "Person".email LIKE '%.org'
  AND "Person".phone_number LIKE '+7%'
  AND "Playlist".creation_date >= '2022-09-01'::date;

-- MEDIUM
-- 1 Получить информацию о артисте, который выпустил больше всего альбомов в определенном жанре.

SELECT Artist.artist_name best_artist
FROM "Artist" Artist
WHERE Artist.Id IN
      (SELECT Album2Artist.Artist_id
       FROM "Album2Artist" Album2Artist
       WHERE Album2Artist.Album_id IN
             (SELECT Song.Album_id
              FROM "Song" Song
              WHERE Song.Genre_id IN
                    (SELECT Id
                     FROM "Genre"
                     WHERE genre_name = 'Мелодичный дэт-метал' ) )
       GROUP BY Album2Artist.Artist_id
       ORDER BY COUNT(Album2Artist.Album_id) DESC
       LIMIT 1);

-- 2 ищет песню, которые позже 2020 года были добавлены наибольшим числом пользователей в их плейлисты,
-- а также входят в альбомы, выпущенные в 2009 году.

SELECT s.song_name
FROM "Song" s
WHERE s.Id IN
      (SELECT s2p.Song_id
       FROM "Song2Playlist" s2p
       WHERE s2p.Playlist_id IN
             (SELECT p2p.Playlist_id
              FROM "Person2Playlist" p2p
                       JOIN "Playlist" P ON P.Id = p2p.Playlist_id
              WHERE p2p.Person_id IN
                    (SELECT Id
                     FROM "Person"
                     WHERE EXTRACT(YEAR
                                   FROM creation_date) >= 2020 ) )
       GROUP BY s2p.Song_id
       ORDER BY COUNT(s2p.Playlist_id) DESC
       LIMIT 10)
  AND EXTRACT(YEAR
              FROM
              (SELECT al.drop_date
               FROM "Album" al
               WHERE al.Id = s.Album_id )) = 2009
LIMIT 1;

--Подсчитать среднюю длительность песен в плейлистах и кол-во плейлистов для пользователей с именем Сергей
WITH UserPlaylists AS (
    SELECT
        "Person".Full_name AS UserName,
        "Playlist".Id AS PlaylistId,
        "Playlist".playlist_name AS PlaylistName,
        "Song2Playlist".Playlist_id,
        "Song".duration AS SongDuration
    FROM "Person"
             JOIN "Person2Playlist" ON "Person".Id = "Person2Playlist".Person_id
             JOIN "Playlist" ON "Person2Playlist".Playlist_id = "Playlist".Id
             LEFT JOIN "Song2Playlist" ON "Playlist".Id = "Song2Playlist".Playlist_id
             LEFT JOIN "Song" ON "Song2Playlist".Song_id = "Song".Id
    WHERE Full_name ILIKE  '%Сергей %'
),
     AveragePlaylistDuration AS (
         SELECT
             UserName,
             PlaylistId,
             AVG(SongDuration) AS AvgDuration
         FROM UserPlaylists
         GROUP BY UserName, PlaylistId
     )

SELECT
    UserName,
    COUNT(DISTINCT PlaylistId) AS NumPlaylists,
    AVG(AvgDuration)::TIME AS AverageDuration
FROM AveragePlaylistDuration
GROUP BY UserName
ORDER BY AverageDuration DESC;



-- Попробуем найти рейтинг песен по количеству вхождений в плейлисты:


SELECT temp.song_name, temp.count_in_playlists,
       RANK() OVER(ORDER BY temp.count_in_playlists DESC) as song_rank
FROM (
         SELECT song.song_name,
                COUNT(song2playlist.Playlist_id) as count_in_playlists
         FROM "Song" song
                  JOIN "Song2Playlist" song2playlist ON song.Id = song2playlist.Song_id
         GROUP BY song.song_name
     ) as temp;



WITH PopArtists AS (
    SELECT
        art.Id AS ArtistId,
        art.artist_name
    FROM "Artist" art
             JOIN "Album2Artist" a2a ON art.Id = a2a.Artist_id
             JOIN "Album" alb ON a2a.Album_id = alb.Id
             JOIN "Genre" gen ON alb.Id = gen.Id AND gen.genre_name = 'Транс'
),
     LongPopSongs AS (
         SELECT
             s.Id AS SongId,
             s.song_name,
             s.duration,
             s2a.Artist_id
         FROM "Song" s
                  JOIN "Song2Artist" s2a ON s.Id = s2a.Song_id
                  JOIN PopArtists pa ON s2a.Artist_id = pa.ArtistId
         WHERE s.duration > interval '6 min'
     ),
     UserPlaylistsWithLongPopSongs AS (
         SELECT
             p2p.Person_id,
             s2p.Playlist_id,
             SUM(lps.duration) AS TotalDuration
         FROM "Person2Playlist" p2p
                  JOIN "Song2Playlist" s2p ON p2p.Playlist_id = s2p.Playlist_id
                  JOIN LongPopSongs lps ON s2p.Song_id = lps.SongId
         GROUP BY p2p.Person_id, s2p.Playlist_id
     )
SELECT
    p.Full_name AS UserName,
    COUNT(DISTINCT ups.Playlist_id) AS NumPlaylists,
    SUM(ups.TotalDuration)::TIME AS TotalDuration
FROM "Person" p
         JOIN UserPlaylistsWithLongPopSongs ups ON p.Id = ups.Person_id
GROUP BY p.Id
ORDER BY TotalDuration DESC;

SELECT Album.album_name, COUNT(Song.Id) OVER (PARTITION BY Album.Id) AS song_count,
       RANK() OVER (ORDER BY COUNT(Song.Id) OVER (PARTITION BY Album.Id) DESC) AS album_rank
FROM Album
         JOIN Song ON Album.Id = Song.Album_id;
