"""
Gets anime/manga from using
https://github.com/seanbreckenridge/malexport
"""

import os
import warnings
from typing import Iterator, Optional, Union

import my.mal as mal

from ..common import _remove_tz
from ..model import FeedItem
from ..log import logger


def _image_url(data: Union[mal.AnimeData, mal.MangaData]) -> Optional[str]:
    api_images = data.APIList.main_picture
    for k in (
        "large",
        "medium",
    ):
        if img_url := api_images.get(k):
            return img_url
    return None


def _anime() -> Iterator[FeedItem]:
    for an in mal.anime():

        if an.username != os.environ["MAL_USERNAME"]:
            continue

        tags = [genre.name for genre in an.APIList.genres]
        if an.JSONList:
            tags.extend([demo.name for demo in an.JSONList.demographics])

        url = f"https://myanimelist.net/anime/{an.id}"
        score = float(an.XMLData.score) if an.XMLData.score is not None else None

        for hist in an.history:
            yield FeedItem(
                id=f"anime_episode_{an.id}_{hist.number}_{int(hist.at.timestamp())}",
                ftype="anime_episode",
                tags=tags,
                when=hist.at,
                url=url,
                data={
                    "status": an.XMLData.status.casefold(),
                    "media_type": an.APIList.media_type.casefold(),
                    "episode_count": an.APIList.episode_count,
                    "average_episode_duration": an.APIList.episode_count,
                },
                image_url=_image_url(an),
                title=f"Episode {hist.number}",
                collection=str(an.id),
                part=hist.number,  # no reliable season data for anime data
                release_date=an.APIList.start_date,
                subtitle=an.APIList.title,
                score=score,
            )


def _manga() -> Iterator[FeedItem]:
    for mn in mal.manga():

        if mn.username != os.environ["MAL_USERNAME"]:
            continue

        tags = [genre.name for genre in mn.APIList.genres]
        if mn.JSONList:
            tags.extend([demo.name for demo in mn.JSONList.demographics])

        url = f"https://myanimelist.net/manga/{mn.id}"
        score = float(mn.XMLData.score) if mn.XMLData.score is not None else None

        for hist in mn.history:
            yield FeedItem(
                id=f"manga_chapter_{mn.id}_{hist.number}_{int(hist.at.timestamp())}",
                ftype="manga_chapter",
                tags=tags,
                when=hist.at,
                url=url,
                collection=str(mn.id),
                data={
                    "status": mn.XMLData.status.casefold(),
                    "media_type": mn.APIList.media_type.casefold(),
                },
                image_url=_image_url(mn),
                title=f"Episode {hist.number}",
                part=hist.number,  # no reliable volume data for manga data
                release_date=mn.APIList.start_date,
                subtitle=mn.APIList.title,
                score=score,
            )


def history() -> Iterator[FeedItem]:
    yield from _anime()
    yield from _manga()
