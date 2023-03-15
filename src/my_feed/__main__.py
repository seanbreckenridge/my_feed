import time
import pickle
from pathlib import Path
from typing import Iterator, Callable, Optional, List, TypeGuard, Any, Set

import click

from .log import logger
from .sources.model import FeedItem


@click.group()
def main():
    """My Personal Media Feed"""


BLUE = (83, 158, 206)


def _check_source(source: Any) -> TypeGuard[Callable[[], Iterator[FeedItem]]]:
    if not callable(source):
        click.echo(f"{source} is not callable, ignoring source", err=True)
        return False
    return True


def _sources() -> Iterator[Callable[[], Iterator[FeedItem]]]:
    try:
        from my.config.feed import sources  # type: ignore[import]
    except Exception:
        click.echo(
            "Could not import sources from my.config.feed, see docs or https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/feed.py as an example",
            err=True,
        )
        return

    assert callable(sources), "sources imported from my.config.feed is not a function"
    for src in iter(sources()):
        if _check_source(src):
            yield src


def data(*, filter_sources: List[str], blur_images: Set[str], echo: bool = False) -> Iterator[FeedItem]:
    for producer in _sources():
        func = f"{producer.__module__}.{producer.__qualname__}"
        if len(filter_sources) > 0:
            if not any([substr in func for substr in filter_sources]):
                continue
        emitted: set[str] = set()
        start_time = time.time()
        func = f"{producer.__module__}.{producer.__qualname__}"
        ext = f"Extracting {click.style(func, fg='green')}"
        click.echo(f"{ext}...")
        for item in producer():
            assert isinstance(item, FeedItem)
            item.check()
            if item.id in emitted:
                logger.warning(f"Duplicate id: {item.id} {item}")
            emitted.add(item.id)
            if echo:
                print(item)
            if item.should_be_blurred(blur_images):
                item.blur()
                click.echo(f"Blurred image: {item.id=} {item.title=} {item.image_url=}")
            yield item
        took = time.time() - start_time
        click.echo(
            f"{ext}: {click.style(str(len(emitted)), fg=BLUE)} items (took {click.style(round(took, 2), fg=BLUE)} seconds)",
            err=True,
        )


# TODO: this could allow either passing the ID or the URL
def _parse_blur_file(
    ctx: click.Context, param: click.Parameter, value: Optional[Path]
) -> Set[str]:
    if value is not None:
        return set(value.read_text().splitlines())
    return set()


@main.command(name="index", short_help="recompute feed data")
@click.option(
    "--echo/--no-echo",
    default=False,
    is_flag=True,
    help="Print feed items as they're computed",
)
@click.option(
    "-f",
    "--filter-sources",
    default=None,
    help="A comma delimited list of substrings of sources. e.g. 'mpv,trakt,listens'",
)
@click.option(
    "-B",
    "--blur-images-file",
    "blur_images_set",
    default=None,
    help="A file containing a list of image URLs to blur, one per line",
    type=click.Path(exists=True, path_type=Path),
    callback=_parse_blur_file,
)
@click.argument(
    "OUTPUT", type=click.Path(writable=True, path_type=Path), required=False
)
def index(
    echo: bool,
    filter_sources: Optional[str],
    output: Optional[Path],
    blur_images_set: Set[str],
) -> None:
    filter_lst: List[str] = []
    if filter_sources:
        filter_lst = [p.strip() for p in filter_sources.strip().split(",")]
    items = list(data(filter_sources=filter_lst, blur_images=blur_images_set, echo=echo))
    click.echo(f"Total: {click.style(len(items), BLUE)} items")
    if output is not None:
        click.echo(f"Writing to '{output}'")
        dumped_items = pickle.dumps(items)
        with output.open("wb") as f:
            f.write(dumped_items)


if __name__ == "__main__":
    main(prog_name="my_feed")
