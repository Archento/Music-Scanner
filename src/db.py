import sys
from typing import Literal

import mariadb
from pydantic import BaseModel

from src.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
from src.models import Album, Artist

try:
    database = mariadb.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
    )
except mariadb.Error as e:
    print(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)


def db_close() -> None:
    """
    Close the database connection.
    :return: None
    """
    try:
        database.close()
    except mariadb.Error as e:
        print(f"Error closing database connection: {e}")
        sys.exit(1)
    print("Database connection closed.")


def db_test() -> bool:
    """
    Test the database connection.
    :return: None
    """
    result = False
    cursor = database.cursor()
    try:
        cursor.execute("SELECT 1")
        result = True
    except mariadb.Error as e:
        print(f"Error testing database connection: {e}")
    finally:
        cursor.close()
    return result


def _db_get(
    query: str, model: type[BaseModel] | None = None
) -> list[BaseModel | dict]:
    """
    Get data from the database.
    :param query: SQL query to execute.
    :param model: Pydantic model to convert the result to.
    :return: List of results or None.
    """
    cursor = database.cursor()
    try:
        cursor.execute(query)
        result = [
            dict(zip(cursor.metadata["field"], row))
            for row in cursor.fetchall()
        ]
        if model:
            return [model(**data) for data in result]
        return result  # type: ignore
    except mariadb.Error as e:
        print(f"Error executing query: {e}")
    finally:
        cursor.close()
    return []


def _db_set(query: str, params: tuple | None = None) -> bool:
    """
    Set data in the database.
    :param query: SQL query to execute.
    :param params: Parameters to pass to the query.
    :return: None
    """
    if params is None:
        raise ValueError("params cannot be None")
    cursor = database.cursor()
    try:
        cursor.execute(query, params)
        return True
    except mariadb.Error as e:
        print(f"Error executing query: {e}")
    finally:
        cursor.close()
        database.commit()
    return False


def db_get_artist(name: str) -> Artist | None:
    """
    Get artist from the database.
    :param name: Name of the artist.
    :return: Artist data.
    """
    query = f'SELECT * FROM artists WHERE name = "{name}"'

    result = _db_get(query, Artist)
    return result[0] if result else None  # type: ignore


def db_set_artist(data: Artist) -> bool:
    """
    Set artist in the database.
    :param data: Artist data.
    :return: None
    """
    query = """
        INSERT INTO artists (id, name, link, picture, picture_small,
            picture_medium, picture_big, picture_xl, nb_album,
            nb_fan, radio, tracklist, type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            id = VALUES(id),
            name = VALUES(name),
            link = VALUES(link),
            picture = VALUES(picture),
            picture_small = VALUES(picture_small),
            picture_medium = VALUES(picture_medium),
            picture_big = VALUES(picture_big),
            picture_xl = VALUES(picture_xl),
            nb_album = VALUES(nb_album),
            nb_fan = VALUES(nb_fan),
            radio = VALUES(radio),
            tracklist = VALUES(tracklist),
            type = VALUES(type)
    """
    params = [*data.model_dump().values()]
    return _db_set(query, params)


def db_get_albums_by_artist_id(
    artist_id: int, album_type: Literal["album", "single", "ep"] | None = None
) -> list[Album | dict]:
    """
    Get album from the database.
    :param artist_id: ID of the artist.
    :return: Album data.
    """
    query = f"SELECT * FROM albums WHERE artist_id = '{artist_id}'"
    if album_type:
        query += f" AND record_type = '{album_type}'"
    query += " ORDER BY release_date ASC"

    return _db_get(query, Album)


def db_set_album(artist_id: int, data: Album) -> bool:
    """
    Set album in the database.
    :param data: Album data.
    :return: None
    """
    query = """
        INSERT INTO albums (id, title, link, cover, cover_small,
            cover_medium, cover_big, cover_xl, genre_id,
            fans, release_date, record_type, explicit_lyrics, artist_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            id = VALUES(id),
            title = VALUES(title),
            link = VALUES(link),
            cover = VALUES(cover),
            cover_small = VALUES(cover_small),
            cover_medium = VALUES(cover_medium),
            cover_big = VALUES(cover_big),
            cover_xl = VALUES(cover_xl),
            genre_id = VALUES(genre_id),
            fans = VALUES(fans),
            release_date = VALUES(release_date),
            record_type = VALUES(record_type),
            explicit_lyrics = VALUES(explicit_lyrics),
            artist_id = VALUES(artist_id)
    """
    params = [*data.model_dump().values(), artist_id]
    return _db_set(query, params)
