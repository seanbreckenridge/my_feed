"""
Gets albums I've listened to from my spreadsheet
https://sean.fish/s/albums
"""

import warnings
import string
from typing import Iterator

from nextalbums.export import Album
from my.albums import history as album_history

from ..common import _remove_tz
from ..model import FeedItem
from ..log import logger

ALLOWED = string.ascii_letters + string.digits + " "


def _album_id(album: Album) -> str:
    """Create a unique hash for this album"""
    dicsogs = ""
    if album.discogs_url is not None:
        discogs = album.discogs_url.strip("/").split("/")[-1]
    album_id_raw = f"{album.album_name} {album.cover_artists} {album.year} {discogs}"
    return (
        "".join(s for s in album_id_raw.strip() if s in ALLOWED)
        .replace(" ", "_")
        .casefold()
    )


def history() -> Iterator[FeedItem]:
    hashes: set[str] = set()
    for al in album_history():

        # make sure no duplicate hashes
        album_hash = _album_id(al)
        if album_hash in hashes:
            raise ValueError(f"Duplicate album id {album_hash}")
        hashes.add(album_hash)

        # some sanity checks
        if al.score is None:
            warnings.warn(f"score is None: {al}")
            continue
        if al.listened_on is None:
            warnings.warn(f"listened_on is None: {al}")
            continue

        yield FeedItem(
            id=f"album_{album_hash}",
            score=float(al.score),
            title=al.album_name,
            ftype="album",
            when=al.listened_on,
            tags=al.genres + al.styles + al.reasons,
            creator=[
                ar.artist_name for ar in al.main_artists if ar.artist_name is not None
            ],
            subtitle=al.cover_artists,
            url=al.discogs_url,
            image_url=al.album_artwork_url,
            release_date=al.year,
        )
