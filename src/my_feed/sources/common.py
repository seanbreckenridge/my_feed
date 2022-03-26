import os

from typing import Any


class FeedError(RuntimeError):
    pass


class FeedBackgroundError(FeedError):
    pass


def click() -> Any:
    """
    Wrapper for the click module when using it to prompt me
    so I can prevent the calls while running in the background
    """
    import click as click_module

    if "MY_FEED_BG" in os.environ:
        raise FeedBackgroundError("Running in the background, cant prompt")
    return click_module
