from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class Artist(BaseModel):
    id: int
    name: str
    link: str
    picture: str
    picture_small: str
    picture_medium: str
    picture_big: str
    picture_xl: str
    nb_album: int
    nb_fan: int
    radio: bool
    tracklist: str
    type: str


class Album(BaseModel):
    id: int
    title: str
    link: str
    cover: str
    cover_small: str | None = None
    cover_medium: str | None = None
    cover_big: str | None = None
    cover_xl: str | None = None
    genre_id: int
    fans: int
    release_date: datetime
    record_type: Literal["album", "single", "ep", "compile"]
    explicit_lyrics: bool
