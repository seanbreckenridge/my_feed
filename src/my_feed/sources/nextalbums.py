"""
Gets albums I've listened to from my spreadsheet
https://sean.fish/s/albums
"""

import warnings
from datetime import datetime, time
from typing import Iterator, Dict, Any

from my.nextalbums import history as album_history, Album
from nextalbums.discogs_update import slugify
from my.time.tz.via_location import localize

from .model import FeedItem


def _album_id(album: Album) -> str:
    """Create a unique hash for this album"""
    album_id_raw = f"{album.album_name} {album.cover_artists} {album.year}"
    return slugify(album_id_raw)


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

        # combine datetime with ~noon, as some sort of
        # average time I listen to an album.
        # Use HPI locations module to determine timezone
        dt_naive = datetime.combine(al.listened_on, time(hour=12))
        dt = localize(dt_naive)

        data: Dict[str, Any] = {}
        image_url = al.album_artwork_url
        assert image_url.strip(), f"No image url: {al}"

        yield FeedItem(
            id=f"album_{album_hash}",
            score=float(al.score),
            title=al.album_name,
            ftype="album",
            when=dt,
            tags=al.genres + al.styles + al.reasons,
            subtitle=al.cover_artists,
            url=al.discogs_url,
            image_url=image_url,
            data=data,
            release_date=al.release_date(),
        )
