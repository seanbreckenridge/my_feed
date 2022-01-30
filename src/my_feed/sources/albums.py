"""
Gets albums I've listened to from my spreadsheet
https://sean.fish/s/albums
"""

import warnings
import string
from datetime import date, datetime, timezone
from typing import Iterator, Optional

from my.albums import history as album_history, Album

from .model import FeedItem

ALLOWED = string.ascii_letters + string.digits + " "


def _album_id(album: Album) -> str:
    """Create a unique hash for this album"""
    album_id_raw = f"{album.album_name} {album.cover_artists} {album.year}"
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

        rel_date: Optional[date] = None
        if al.year:
            rel_date = date(year=al.year, month=1, day=1)

        dt = datetime.combine(al.listened_on, datetime.min.time(), tzinfo=timezone.utc)

        yield FeedItem(
            id=f"album_{album_hash}",
            score=float(al.score),
            title=al.album_name,
            ftype="album",
            when=dt,
            data={
                "artists": [
                    ar.artist_name
                    for ar in al.main_artists
                    if ar.artist_name is not None
                ]
            },
            tags=al.genres + al.styles + al.reasons,
            subtitle=al.cover_artists,
            url=al.discogs_url,
            image_url=al.album_artwork_url,
            release_date=rel_date,
        )
