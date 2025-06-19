import requests

from src.models import Album, Artist

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
        print(f"An error occurred: {e}")
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
            print(f"No data found for artist: {artist_name}")
            return [], 0
        artists = []
        for entry in data:
            artists.append(Artist(**entry))
        return artists, response.get("total")
    print(f"Failed to retrieve data for artist: {artist_name}")
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
    total = response.get("total")  # 52
    albums = []
    if not response or not total:
        print(f"No albums found for artist ID: {artist_id}")
        return [], 0

    data = response.get("data") or []
    for entry in data:
        albums.append(Album(**entry))
    if "next" in response:
        print("Fetching additional pages of albums...")
        while total > len(albums):
            url = response.get("next")
            if not url:
                print("No more pages to fetch.")
                break
            response = _make_request(url)
            if not response:
                print("Failed to retrieve albums.")
                break
            data = response.get("data") or []
            if not data:
                print(f"No albums found for artist ID: {artist_id}")
                break
            for entry in data:
                albums.append(Album(**entry))
    return albums, total
