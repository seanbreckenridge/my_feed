from typing import Iterator

import click

from ..model import FeedItem
from .trakt import history as tr_history
from .scrobbles import history as sc_history
from .albums import history as al_history
from .mal import history as mal_history


@click.group()
def main():
    pass


def _histories() -> Iterator[FeedItem]:
    yield from al_history()
    yield from sc_history()
    yield from mal_history()
    yield from tr_history()


def data() -> Iterator[FeedItem]:
    emitted: set[str] = set()
    for item in _histories():
        # do some error/bounds checking
        # and check for duplicates
        item.check()
        if item.id in emitted:
            click.echo(f"Duplicate id: {item.id}")
        emitted.add(item.id)
        yield item


@main.command(name="index", short_help="recompute feed data")
@click.option(
    "--echo/--no-echo",
    default=False,
    is_flag=True,
    help="Print feed items as they're computed",
)
def index(echo: bool):
    for h in data():
        if echo:
            click.echo(h)


if __name__ == "__main__":
    main(prog="my_feed")
