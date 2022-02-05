"""
Gets anime/manga from using
https://github.com/seanbreckenridge/malexport
"""

import os
from datetime import datetime, timezone
from typing import Iterator, Optional, Union

import my.mal.export as mal

from .model import FeedItem


def _image_url(data: Union[mal.AnimeData, mal.MangaData]) -> Optional[str]:
    assert data.APIList is not None
    api_images = data.APIList.main_picture
    for k in (
        "medium",
        "large",
    ):
        if img_url := api_images.get(k):
            return img_url
    return None


WHILE_UPDATING_ERR = "Could be failing while malexport is updating"


def _anime() -> Iterator[FeedItem]:
    for an in mal.anime():

        if an.username != os.environ["MAL_USERNAME"]:
            continue

        assert an.APIList is not None, WHILE_UPDATING_ERR
        assert an.JSONList is not None, WHILE_UPDATING_ERR

        tags = [genre.name for genre in an.APIList.genres]
        if an.JSONList:
            tags.extend([demo.name for demo in an.JSONList.demographics])

        url = f"https://myanimelist.net/anime/{an.id}"
        score = float(an.XMLData.score) if an.XMLData.score is not None else None

        # if theres only one item here, and I've only watched it once,
        # don't include an episode -- it gets included in the completed block
        # if an.XMLData.status.casefold() == "completed" and len(an.history) == 1 and an.APIList.episode_count == 1:
        #    continue

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
                subtitle=f"Episode {hist.number}",
                collection=str(an.id),
                part=hist.number,  # no reliable season data for anime data
                release_date=an.APIList.start_date,
                title=an.APIList.title,
                score=score,
            )
        if an.XMLData.status.casefold() == "completed":
            dt: Optional[datetime] = None
            # if theres only one episode, find the first time I watched this
            if an.APIList.episode_count is not None and len(an.history) > 0:
                # its sorted from newest to oldest, so iterate from the beginning
                # this is the datetime when I completed the last epsisode the first
                # time (could be multiple times because of rewatches)
                completed_last_ep_at = [
                    ep
                    for ep in reversed(an.history)
                    if ep.number == an.APIList.episode_count
                ]
                if completed_last_ep_at:
                    dt = completed_last_ep_at[0].at
            if dt is None:
                # use finish date
                if an.XMLData.finish_date is not None:
                    dt = datetime.combine(
                        an.XMLData.finish_date, datetime.min.time(), tzinfo=timezone.utc
                    )
                elif len(an.history) > 0:
                    # use history entry
                    dt = an.history[0].at
                else:
                    continue
            yield FeedItem(
                id=f"anime_entry_{an.id}",
                ftype="anime",
                tags=tags,
                when=dt,
                url=url,
                data={
                    "status": an.XMLData.status.casefold(),
                    "media_type": an.APIList.media_type.casefold(),
                    "episode_count": an.APIList.episode_count,
                    "average_episode_duration": an.APIList.episode_count,
                },
                image_url=_image_url(an),
                title=an.APIList.title,
                release_date=an.APIList.start_date,
                score=score,
            )


def _manga() -> Iterator[FeedItem]:
    for mn in mal.manga():

        if mn.username != os.environ["MAL_USERNAME"]:
            continue

        assert mn.APIList is not None, WHILE_UPDATING_ERR
        assert mn.JSONList is not None, WHILE_UPDATING_ERR

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
                    "chapters": mn.XMLData.chapters,
                },
                image_url=_image_url(mn),
                subtitle=f"Chapter {hist.number}",
                part=hist.number,  # no reliable volume data for manga data
                release_date=mn.APIList.start_date,
                title=mn.APIList.title,
                score=score,
            )
        if mn.XMLData.status.casefold() == "completed":
            dt: datetime
            # TODO: use chapter count == last episode in history to figure out when I first finished this
            if mn.XMLData.finish_date is not None:
                dt = datetime.combine(
                    mn.XMLData.finish_date, datetime.min.time(), tzinfo=timezone.utc
                )
            elif len(mn.history) > 0:
                dt = mn.history[0].at
            else:
                continue
            yield FeedItem(
                id=f"manga_entry_{mn.id}",
                ftype="manga",
                tags=tags,
                when=dt,
                url=url,
                data={
                    "status": mn.XMLData.status.casefold(),
                    "media_type": mn.APIList.media_type.casefold(),
                    "chapters": mn.XMLData.chapters,
                },
                image_url=_image_url(mn),
                title=mn.APIList.title,
                release_date=mn.APIList.start_date,
                score=score,
            )


def history() -> Iterator[FeedItem]:
    yield from _anime()
    yield from _manga()
