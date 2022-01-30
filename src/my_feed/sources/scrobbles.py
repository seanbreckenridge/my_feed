#!/usr/bin/env python3

"""
Scrobbles, with some manual fixes because of lacking metadata

All of the metadata *should* be correct now because of
https://sean.fish/d/id3stuff?dark, but some older scrobbles
have bad metadata
"""

import os
import json
from pathlib import Path
from typing import Iterator, List, Tuple, Dict, cast, Optional

import click
from my.listenbrainz import history as lb_history, Listen

from .model import FeedItem
from ..log import logger

# defaults from listenbrainz/media player, when the artist was unknown
BROKEN_ARTISTS = {"unknown artist", "<unknown>"}

try:
    from seanb.feed_conf import broken_artists

    BROKEN_ARTISTS.update(broken_artists)
except ImportError:
    pass


def _manual_scrobble_datafile() -> Path:
    return Path(os.path.join(os.environ["HPIDATA"], "feed_scrobble_manual_fixes.json"))


Metadata = Tuple[str, str, List[str]]


def _manually_fix_scrobble(l: Listen) -> Tuple[str, str, List[str]]:
    """Fix broken metadata on scrobbles, and save my responses to a cache file"""

    # load data
    datafile = _manual_scrobble_datafile()
    data: Dict[str, Metadata] = {}
    if datafile.exists():
        data = cast(Dict[str, Metadata], json.loads(datafile.read_text()))

    # use timestamp to uniquely identify scrobbles to fix
    assert l.listened_at is not None
    ts = str(int(l.listened_at.timestamp()))
    if ts in data:
        logger.debug(f"Replacing manual scrobble fix {data[ts]}")
        return data[ts]

    # prompt me to manually type in the correct data
    click.echo(f"broken: {l}", err=True)
    title = click.prompt("title").strip()
    subtitle = click.prompt("album name").strip()
    creator = [click.prompt("artist name").strip()]

    new_data = (
        title,
        subtitle,
        creator,
    )
    # write data
    data[ts] = new_data
    datafile.write_text(json.dumps(data, indent=4))
    return new_data


def history() -> Iterator[FeedItem]:
    for listen in lb_history():
        if listen.listened_at is None:
            logger.debug(f"ignoring listen with no datetime {listen}")
            continue

        title: str = listen.track_name
        subtitle: Optional[str] = listen.release_name
        creator: List[str] = [listen.artist_name]
        if listen.artist_name.lower() in BROKEN_ARTISTS:
            title, subtitle, creator = _manually_fix_scrobble(listen)

        ts: int = int(listen.listened_at.timestamp())
        # TODO: attach to album somehow (parent_id/collection)?
        yield FeedItem(
            id=f"scrobble_{ts}",
            ftype="scrobble",
            title=title,
            subtitle=subtitle,
            creator=creator,
            when=listen.listened_at,
        )
