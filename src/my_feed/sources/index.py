import time
from typing import Iterator, Callable

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
    """My Personal Media Feed"""


BLUE = (83, 158, 206)


def _games() -> Iterator[Callable[[], Iterator[FeedItem]]]:
    from .games import steam, osrs, game_center, grouvee, chess

    yield steam
    yield osrs
    yield game_center
    yield grouvee
    yield chess


def _sources() -> Iterator[Callable[[], Iterator[FeedItem]]]:
    yield from _games()
    yield tr_history
    yield sc_history
    yield al_history
    yield mal_history
    yield mpv_history


def data(echo: bool) -> Iterator[FeedItem]:
    for producer in _sources():
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
            if echo:
                print(item)
            yield item
        took = time.time() - start_time
        click.echo(
            f"{ext}: {click.style(len(emitted), fg=BLUE)} items (took {click.style(round(took, 2), fg=BLUE)} seconds)",
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
    items = list(data(echo=echo))
    click.echo(f"Total: {click.style(len(items), BLUE)}; writing to <filename>")


if __name__ == "__main__":
    main(prog="my_feed")
