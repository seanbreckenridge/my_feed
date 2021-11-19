#!/usr/bin/env python3

"""
Uses HPI to create a normalized feed of items
"""

from typing import Iterator, Callable, TYPE_CHECKING
from .model import FeedItem

if TYPE_CHECKING:
    from listenbrainz_export.parse import Listen

# global to allow overriding
scrobble_filter_func: Callable[["Listen"], bool] = lambda l: True
try:
    from seanb.scrobbles_secret import filter_scrobbles
except ImportError:
    pass


def scrobbles() -> Iterator[FeedItem]:
    # probably need to create a personal function to filter/rename stuff
    # using my local music dir, and/or just remove incorrect youtube video scrobbles
    from my.listenbrainz import history

    for listen in filter(scrobble_filter_func, history()):
        dt = listen.listened_at
        ts: int = int(dt.timestamp())
        # TODO: attach to album somehow (parent_id)?
        yield FeedItem(
            id=f"scrobble_{ts}",
            media_type="scrobble",
            title=listen.track_name,
            subtitle=listen.release_name,
            creators=listen.artist_name,
            when=dt,
        )
