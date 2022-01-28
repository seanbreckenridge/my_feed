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
from typing import Iterator, List, Tuple

import click
from my.listenbrainz import history as lb_history, Listen

from ..common import _remove_tz
from ..model import FeedItem
from ..log import logger

BROKEN_ARTISTS = {"unknown artist", "<unknown>", "bill wutrz"}


def _manual_scrobble_datafile() -> Path:
    return Path(os.path.join(os.environ["HPIDATA"], "feed_scrobble_manual_fixes.json"))


def _manually_fix_scrobble(l: Listen) -> Tuple[str, str, List[str]]:
    """Fix broken metadata on scrobbles, and save my responses to a cache file"""

    # load data
    datafile = _manual_scrobble_datafile()
    data = {}
    if datafile.exists():
        data = json.loads(datafile.read_text())

    # use timestamp to uniquely identify scrobbles to fix
    ts = str(int(l.listened_at.timestamp()))
    if ts in data:
        logger.debug(f"Replacing manual scrobble fix {data[ts]}")
        return data[ts]

    # prompt me to manually type in the correct data
    click.echo(f"broken: {l}")
    title = click.prompt("title").strip()
    subtitle = click.prompt("album name").strip()
    creator = [click.prompt("artist name").strip()]

    # write data
    data[ts] = [title, subtitle, creator]
    datafile.write_text(json.dumps(data, indent=4))
    return (
        title,
        subtitle,
        creator,
    )


def history() -> Iterator[FeedItem]:
    for listen in lb_history():
        title: str = listen.track_name
        subtitle: str = listen.release_name
        creator: List[str] = [listen.artist_name]

        if listen.artist_name.lower() in BROKEN_ARTISTS:
            title, subtitle, creator = _manually_fix_scrobble(listen)

        dt = listen.listened_at
        ts: int = int(dt.timestamp())
        # TODO: attach to album somehow (parent_id/collection)?
        yield FeedItem(
            id=f"scrobble_{ts}",
            ftype="scrobble",
            title=title,
            subtitle=subtitle,
            creator=creator,
            when=_remove_tz(dt),
        )

