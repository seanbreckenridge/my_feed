import time
from typing import Iterator

import click

from ..log import logger
from ..model import FeedItem
from .trakt import history as tr_history
from .scrobbles import history as sc_history
from .albums import history as al_history
from .mal import history as mal_history
from .mpv import history as mpv_history


@click.group()
def main():
    pass


def data() -> Iterator[FeedItem]:
    for producer in (sc_history, al_history, mpv_history, mal_history, tr_history):
        emitted: set[str] = set()
        start_time = time.time()
        func = f"{producer.__module__}.{producer.__qualname__}"
        ext = f"Extracting {click.style(func, fg='green')}"
        click.echo(f"{ext}...")
        for item in producer():
            item.check()
            if item.id in emitted:
                logger.warning(f"Duplicate id: {item.id}")
            emitted.add(item.id)
            yield item
        took = time.time() - start_time
        click.echo(
            f"{ext}: {click.style(str(len(emitted)), fg='blue')} items (took {click.style(round(took, 2), fg='blue')} seconds)",
            err=True,
        )


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
