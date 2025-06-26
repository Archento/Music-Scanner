"""
Main script to crawl a music library and retrieve artist and album information.
"""

import json
import os
import sys
from logging import getLogger

from src.db import (
    db_close,
    db_get_albums_by_artist_id,
    db_get_artist,
    db_set_album,
    db_set_artist,
    db_set_scan_dump,
    db_test,
)
from src.deez import search_artist, search_artist_albums
from src.models import Album, Artist
from src.utils import fast_scandir, write_markdown_file

logger = getLogger(__name__)


def retrieve_artist(artist_name: str) -> Artist | None:
    """
    Retrieve artist information from the database or Deezer API.

    :param artist_name: Name of the artist to retrieve.
    :return: Artist object or None if not found.
    """
    logger.info("Retrieving artist: %s", artist_name)
    artist = None
    artist = db_get_artist(artist_name)
    if not artist:
        logger.info("Artist not found in the database. Querying Deezer API...")
        artists, hits = search_artist(artist_name)
        logger.debug("Found %s artists.", hits)
        for artist in artists:
            db_set_artist(artist)
        if hits:
            artist = db_get_artist(artist_name)
            logger.debug("Artist added to the database.")

    if not artist:
        logger.warning("Artist '%s' not available.", artist_name)

    return artist


# this needs to be refactored since new albums need to be added
# to the database if they are not already present
def retrieve_albums(artist: Artist) -> list[Album]:
    """
    Retrieve albums for a given artist from the database or Deezer API.

    :param artist: Artist object for which to retrieve albums.
    :return: List of Album objects.
    """
    logger.info("Retrieving albums for artist: %s", artist.name)
    albums = []
    albums = db_get_albums_by_artist_id(artist.id, album_type="album")
    if not albums:
        logger.info("Albums not found in the database. Querying Deezer API...")
        albums, hits = search_artist_albums(artist)
        logger.debug("Found %s albums.", hits)
        for album in albums:
            db_set_album(artist.id, album)
        return [a for a in albums if a.record_type == "album"]
    return albums


def crawl_music_library(folder_path: str = ".") -> dict[str, list[str]]:
    """Crawl the music library to retrieve artist and album information"""
    all_folders = fast_scandir(folder_path)
    prefix = os.path.commonprefix(all_folders)
    cleaned_folders = [folder.replace(prefix, "") for folder in all_folders]

    artists = {}
    for folder in cleaned_folders:
        if "/" in folder:
            artist_name = folder.split("/")[0]
            if artist_name not in artists:
                artists[artist_name] = []
            if folder.count("/") == 1:
                # only add album if it is a subfolder of the artist and
                # not a nested folder
                album_name = folder.split("/")[-1]
                if album_name not in artists[artist_name]:
                    artists[artist_name].append(album_name)
        else:
            artists[folder] = []
    logger.debug("Found %s artists in the music library.", len(artists))
    for albums in artists.values():
        albums.sort()
    return artists


def main(path: str = ".") -> None:
    """Main function to run the script"""
    library = crawl_music_library(path)

    with open("library.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(library, indent=4, sort_keys=True))

    missing_artists: list[str] = []
    db_artists: list[Artist] = []
    for artist, _ in library.items():
        db_artist = retrieve_artist(artist)
        if db_artist:
            db_artists.append(db_artist)
        else:
            missing_artists.append(artist)

    logger.debug(
        "Found %s of %s artists in the database.", len(db_artists), len(library)
    )
    if missing_artists:
        logger.info("Missing artists: %s", ", ".join(missing_artists))

    artist_album_map: dict[str, list[str]] = {}

    for artist in db_artists:
        albums: list[Album] = retrieve_albums(artist)
        if albums:
            sorted(albums, key=lambda x: x.release_date, reverse=True)
            artist_album_map[artist.name] = [
                f"{album.release_date.year} - {album.title}" for album in albums
            ]
        else:
            artist_album_map[artist.name] = []
    sorted_artist_album_map = dict(sorted(artist_album_map.items()))

    with open("artist_albums.json", "w", encoding="utf-8") as f:
        f.write(json.dumps(sorted_artist_album_map, indent=4, sort_keys=True))

    # save json to database for later comparison
    db_set_scan_dump(path, sorted_artist_album_map)

    # write markdown file with comparison of artists and albums
    write_markdown_file(
        "result.md", sorted_artist_album_map, library, overwrite=True
    )


if __name__ == "__main__":
    if not db_test():
        logger.error("Database connection failed.")
        sys.exit(1)
    # main("music")
    main("/Volumes/media/music/Music")
    db_close()
