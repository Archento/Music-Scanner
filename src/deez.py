"""
Deezer API interaction module for Music Scanner.

This module provides functions to search for artists and their albums using the
Deezer API. It includes error handling and logging for better debugging and
maintenance.
"""

from logging import getLogger

import requests

from src.models import Album, Artist

logger = getLogger(__name__)

BASEURL_EXAMPLE = "https://api.deezer.com/"


def _make_request(url, method="GET", params=None) -> dict | None:
    try:
        response = requests.request(
            method,
            url,
            params=params,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error("An error occurred: %s", e)
        return None


def search_artist(artist_name, strict=False) -> tuple[list[Artist], int]:
    """
    Search for an artist by name.

    :param artist_name: Name of the artist to search for.
    :return: JSON response from the Deezer API.
    """
    strict_query = " strict=on" if strict else ""
    url = f"{BASEURL_EXAMPLE}search/artist?q={artist_name}{strict_query}"
    response = _make_request(url)
    if response:
        data = response.get("data") or []
        if not data:
            logger.warning("No data found for artist: %s", artist_name)
            return [], 0
        artists = []
        for entry in data:
            artists.append(Artist(**entry))
        return artists, response.get("total", 0)
    logger.error("Failed to retrieve data for artist: %s", artist_name)
    return [], 0


def search_artist_albums(artist: Artist) -> tuple[list[Album], int]:
    """
    Search for an artist's albums by artist ID.

    :param artist_id: ID of the artist to search for.
    :return: JSON response from the Deezer API.
    """
    artist_id = artist.id
    url = f"{BASEURL_EXAMPLE}artist/{artist_id}/albums"
    response = _make_request(url)
    if not response:
        logger.error("Failed to retrieve albums for artist ID: %s", artist_id)
        return [], 0
    total = response.get("total")
    if not total:
        logger.warning("No albums found for artist ID: %s", artist_id)
        return [], 0

    data = response.get("data") or []
    albums = []
    for entry in data:
        albums.append(Album(**entry))
    if "next" in response:
        logger.debug("Fetching additional pages of albums...")
        while total > len(albums):
            url = response.get("next")
            if not url:
                logger.debug("No more pages to fetch.")
                break
            response = _make_request(url)
            if not response:
                logger.error("Failed to retrieve albums.")
                break
            data = response.get("data") or []
            if not data:
                logger.warning(
                    "No albums found for artist ID: %s (%s)",
                    artist_id,
                    artist.name,
                )
                break
            for entry in data:
                albums.append(Album(**entry))
    return albums, total
