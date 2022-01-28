"""
A small TMDB API client which caches data in a local directory using
a subclassed https://github.com/seanbreckenridge/url_cache
"""

import os
import re
import warnings
import time
from functools import cache
from typing import Optional
from datetime import datetime

import requests
from url_cache.core import (
    URLCache,
    Summary,
)

from ...log import logger


@cache
def cache_dir() -> str:
    default_local = os.path.join(os.environ["HOME"], ".local", "share")
    return os.path.join(default_local, "feed_tmdb")


MOVIE_REGEX = re.compile(r"/movie/(\d+)")
EPISODE_REGEX = re.compile(r"/tv/(\d+)/season/(\d+)/episode/(\d+)")
SEASON_REGEX = re.compile(r"/tv/(\d+)/season/(\d+)")
SHOW_REGEX = re.compile(r"/tv/(\d+)")


def _matches_trakt(url: str) -> bool:
    if not url.startswith(BASE_URL):
        return False
    part = url[len(BASE_URL) :]
    return any(
        (
            bool(re.match(MOVIE_REGEX, part)),
            bool(re.match(EPISODE_REGEX, part)),
            bool(re.match(SEASON_REGEX, part)),
            bool(re.match(SHOW_REGEX, part)),
        )
    )


BASE_URL = "https://api.themoviedb.org/3"


class TMDBCache(URLCache):
    """
    Subclass URLCache to handle caching the Summary data to a local directory cache
    """

    def request_data(self, url: str) -> Summary:
        """
        Override the request data function to fetch from the TMDB API
        If this fails to get data, the error is saved to cache as the metadata
        """
        uurl = self.preprocess_url(url)
        if not _matches_trakt(uurl):
            raise ValueError(f"{url} doesnt match a tmdb URL")
        logger.info(f"Requesting {uurl}")
        r = requests.get(uurl, params={"api_key": os.environ["TMDB_API_KEY"]})
        # 404 means data couldn't be found -- could periodically invalidate anything
        # which has errors as cached information and retry incase new data has been
        # pushed to TMDB
        if r.status_code > 400 and r.status_code != 404:
            logger.info(f"Failed for {uurl}, writing error to cache")
            r.raise_for_status()
        # raises before it returns summary which would then get saved by 'URLCache.get'
        return Summary(url=uurl, data={}, metadata=r.json(), timestamp=datetime.now())


@cache
def tmdb_urlcache() -> TMDBCache:
    return TMDBCache(cache_dir=cache_dir())


def fetch_tmdb_data(url: str) -> Optional[Summary]:
    """
    Given a TMDB API URL (movie/tv show/season/episode), requests and caches the data locally
    """
    try:
        return tmdb_urlcache().get(url)
    except (requests.RequestException, ValueError) as r:
        warnings.warn(f"Could not cache {url}: {str(r)}")
        return None


def test_matches() -> None:
    assert _matches_trakt(BASE_URL + "/movie/145")
    assert _matches_trakt(BASE_URL + "/tv/523/season/2/episode/5")
    assert _matches_trakt(BASE_URL + "/tv/19481239/season/4912")
    assert _matches_trakt(BASE_URL + "/tv/423849")
    assert not _matches_trakt("https://something.org/tv/423849")
    assert not _matches_trakt(BASE_URL)
