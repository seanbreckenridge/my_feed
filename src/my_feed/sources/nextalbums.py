"""
Gets albums I've listened to from my spreadsheet
https://sean.fish/s/albums
"""

import warnings
import string
from datetime import datetime, time
from typing import Iterator, Dict, Any

from my.nextalbums import history as album_history, Album
from my.time.tz.via_location import _get_tz

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


def _img_url(al: Album) -> str:
    for data in al.datas():
        if imgs := data.get("images"):
            assert isinstance(imgs, list)
            primary = [
                img for img in imgs if "type" in img and img["type"] == "primary"
            ]
            if len(primary) > 0:
                uri = primary[0]["uri"]
                assert isinstance(uri, str)
                assert uri.strip(), str(primary)
                return uri.strip()
    return al.album_artwork_url


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

        # combine datetime with ~2:00 PM, average time I listen to an
        # album. Use HPI locations to determine timezone
        dt_naive = datetime.combine(al.listened_on, time(hour=2))
        tz = _get_tz(dt_naive)
        assert tz is not None
        dt = dt_naive.replace(tzinfo=tz)

        data: Dict[str, Any] = {}
        image_url = _img_url(al)
        if al.album_artwork_url != image_url:
            # if we pulled data from the discogs cache, which
            # has additional main iamges past the default
            # al.album_artwork_url, which is typically a thumbnail
            #
            # supply the thumbnail as well, can be used when images
            # are small/don't care about final resolution
            data["thumbnail"] = al.album_artwork_url

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
