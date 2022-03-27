import time
import pickle
from pathlib import Path
from typing import Iterator, Callable, Optional

import click

from .log import logger
from .sources.model import FeedItem


@click.group()
def main():
    """My Personal Media Feed"""


BLUE = (83, 158, 206)


def _games() -> Iterator[Callable[[], Iterator[FeedItem]]]:
    from .sources.games import steam, osrs, game_center, grouvee, chess

    yield steam
    yield osrs
    yield game_center
    yield grouvee
    yield chess


def _sources() -> Iterator[Callable[[], Iterator[FeedItem]]]:
    from .sources.trakt import history as tr_history
    from .sources.listens import history as ls_history
    from .sources.nextalbums import history as al_history
    from .sources.mal import history as mal_history
    from .sources.mpv import history as mpv_history
    from .sources.facebook_spotify_listens import history as old_spotify_listens

    yield old_spotify_listens
    yield ls_history
    yield mpv_history
    yield from _games()
    yield tr_history
    yield al_history
    yield mal_history


def data(echo: bool = False) -> Iterator[FeedItem]:
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
            f"{ext}: {click.style(str(len(emitted)), fg=BLUE)} items (took {click.style(round(took, 2), fg=BLUE)} seconds)",
            err=True,
        )


@main.command(name="index", short_help="recompute feed data")
@click.option(
    "--echo/--no-echo",
    default=False,
    is_flag=True,
    help="Print feed items as they're computed",
)
@click.argument(
    "OUTPUT", type=click.Path(writable=True, path_type=Path), required=False
)
def index(echo: bool, output: Optional[Path]) -> None:
    items = list(data(echo=echo))
    click.echo(f"Total: {click.style(len(items), BLUE)} items")
    if output is not None:
        click.echo(f"Writing to '{output}'")
        dumped_items = pickle.dumps(items)
        with output.open("wb") as f:
            f.write(dumped_items)


if __name__ == "__main__":
    main(prog_name="my_feed")
