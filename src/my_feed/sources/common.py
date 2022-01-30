import os

from typing import Any
from functools import cache


class FeedError(RuntimeError):
    pass


class FeedBackgroundError(FeedError):
    pass


@cache
def _click() -> Any:
    """
    Wrapper for the click module when using it to prompt me
    so I can prevent the calls while running in the background
    """
    import click

    if "MY_FEED_BG" in os.environ:
        raise FeedBackgroundError("Running in the background, cant prompt")
    return click