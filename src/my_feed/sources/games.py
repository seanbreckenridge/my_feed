import os
import string
import warnings
from typing import Iterator, Optional, Dict, Any, cast
from datetime import datetime, timezone, date
from functools import cache

import requests
from url_cache.core import URLCache, Summary

from .model import FeedItem
from ..log import logger


def game_center() -> Iterator[FeedItem]:
    from my.apple.privacy_export import events, GameAchievement

    for e in events():
        if isinstance(e, GameAchievement):
            yield FeedItem(
                id=f"game_center_{int(e.dt.timestamp())}_{_slugify(e.title)}_{e.percentage}",
                ftype="game_achievement",
                title=e.title,
                subtitle=e.game_name,
                when=e.dt,
                data={
                    "percentage": e.percentage,
                },
            )


def _slugify(st: str) -> str:
    ss = "".join(s for s in st.casefold() if s in string.ascii_lowercase + " ")
    return ss.replace(" ", "_")


def steam() -> Iterator[FeedItem]:
    from my.steam.scraper import achievements

    for ac in achievements():
        if isinstance(ac, Exception):
            logger.debug(f"Ignoring exception: {ac}")
            continue
        if ac.achieved_on is None:
            logger.debug(f"steam, no datetime on achievement: {ac}")
            continue
        yield FeedItem(
            id=f"steam_{str(ac.achieved_on.date())}_{_slugify(ac.title)}",
            ftype="game_achievement",
            when=ac.achieved_on,
            title=ac.title,
            subtitle=ac.game_name,
            data={"description": ac.description},
            image_url=ac.icon,
        )


class GiantBombCache(URLCache):
    def request_data(self, url: str) -> Summary:  # type: ignore[override]
        uurl = self.preprocess_url(url)
        logger.info(f"Caching info for grouvee: {url}")
        self.sleep()
        r = requests.get(
            uurl,
            params={"api_key": os.environ["GIANTBOMB_API_KEY"], "format": "json"},
            headers={"User-Agent": f"{os.environ['USER']}_my_feed"},
        )
        r.raise_for_status()
        return Summary(url=uurl, data={}, metadata=r.json(), timestamp=datetime.now())


@cache
def gb_cache() -> GiantBombCache:
    default_local = os.path.join(os.environ["HOME"], ".local", "share")
    cache_dir = os.path.join(default_local, "giantbomb_cache")
    return GiantBombCache(cache_dir=cache_dir, sleep_time=5)


def fetch_giantbomb_data(giantbomb_id: int) -> Optional[Summary]:
    url = f"http://www.giantbomb.com/api/game/{giantbomb_id}/"
    try:
        return gb_cache().get(url)
    except requests.RequestException as r:
        warnings.warn(f"Could not cache {url}: {str(r)}")
        return None


def _grouvee_img(res: dict[str, Any]) -> Optional[str]:
    """traverse API resp and grab the thumbnail/medium iamge"""
    if img := res.get("image"):
        assert isinstance(img, dict)
        for key in ("medium_url", "thumb_url"):
            if img_url := img.get(key):
                return cast(str, img_url)
    return None


def grouvee() -> Iterator[FeedItem]:
    from my.grouvee.export import played

    for g in played():
        assert g.giantbomb_id is not None
        gb_data: Optional[Summary] = fetch_giantbomb_data(g.giantbomb_id)
        assert gb_data is not None, f"No summary returned for {g.giantbomb_id}"

        # handle error
        res: dict[str, Any]
        if gb_data.metadata["error"] == "OK":
            res = gb_data.metadata["results"]
            assert isinstance(res, dict), str(gb_data.metadata)
        else:
            res = {}

        rel: Optional[date] = g.release_date

        # update with more accurate date, if possible
        if rel_str := res.get("original_release_date"):
            try:
                rel = date.fromisoformat(rel_str.strip())
            except:
                pass

        dt: datetime
        for s in g.shelves:
            dt = s.added
            break
        score = None
        if g.rating is not None:
            score = g.rating * 2
        assert dt is not None
        yield FeedItem(
            id=f"grouvee_{g.grouvee_id}",
            ftype="game",
            title=g.name,
            url=g.url,
            release_date=rel,
            image_url=_grouvee_img(res),
            when=dt,
            score=score,
            tags=list(g.genres.keys())
            + list(g.developers.keys())
            + list(g.publishers.keys()),
        )


def osrs() -> Iterator[FeedItem]:
    from my.runelite.screenshots import screenshots, Level

    # TODO: use HPI location provider to determine my tz

    for sc in screenshots():
        # ignore clue scrolls/other stuff
        if sc.screenshot_type not in {"Quest", "Level"}:
            continue
        id_: str
        desc: str
        data = {"path": sc.path}
        img: Optional[str] = None
        if "HPIDATA" in os.environ:
            if prefix := os.getenv("RUNELITE_PHOTOS_PREFIX"):
                img = os.path.join(prefix, str(sc.path).lstrip(os.environ["HPIDATA"]))
        if isinstance(sc.description, Level):
            id_ = f"osrs_level_{sc.description.skill.casefold()}_{sc.description.level}_{int(sc.dt.timestamp())}"
            data.update(sc.description._asdict())
            desc = f"{sc.description.skill} Level {sc.description.level}"
        else:
            assert sc.screenshot_type == "Quest"
            id_ = f"osrs_quest_{int(sc.dt.timestamp())}"
            assert isinstance(sc.description, str)
            desc = sc.description
        # convert naive (assumed local) to UTC, use HPI to improve this
        dt = datetime.fromtimestamp(sc.dt.timestamp(), tz=timezone.utc)
        yield FeedItem(
            id=id_,
            ftype="game_achievement",
            title=desc,
            data=data,
            image_url=img,
            subtitle=sc.screenshot_type,
            when=dt,
        )


# TODO: make configurable
CHESS_USERNAME = "seanbreckenridge"


def chess() -> Iterator[FeedItem]:
    from my.chess.export import history
    from chess_export.chessdotcom.model import ChessDotComGame
    from chess_export.lichess.model import LichessGame
    import chess.pgn, chess.svg
    from io import StringIO

    for game in history():
        if game.pgn is None:
            logger.debug(f"Ignoring chess game with no PGN: {game}")
            continue
        dt: datetime
        won: bool = False
        url: Optional[str] = None
        pgn_str: str
        data: Dict[str, Any] = {}
        if isinstance(game, ChessDotComGame):
            dt = game.end_time
            if game.white.username == CHESS_USERNAME and game.white.result == "win":
                won = True
            elif game.black.username == CHESS_USERNAME and game.black.result == "win":
                won = True
            data["time_control"] = str(game.time_control)
            url = game.url
        elif isinstance(game, LichessGame):
            dt = game.end_time
            if game.white.username == CHESS_USERNAME and game.winner == "white":
                won = True
            elif game.black.username == CHESS_USERNAME and game.winner == "black":
                won = True
            data["variant"] = str(game.variant)
            # 9999 skips to the last move of the match
            url = f"https://lichess.org/{game.game_id}#9999"
        else:
            raise RuntimeError(f"Unexpected game {type(game)} {game}")
        if game.white.username == CHESS_USERNAME:
            me = "white"
        else:
            me = "black"
        pgn_str = game.pgn
        assert me.strip()
        pgn = chess.pgn.read_game(StringIO(pgn_str))
        assert pgn is not None
        # iterate through mainline moves
        board = pgn.board()
        for move in pgn.mainline_moves():
            board.push(move)
        data["svg"] = str(chess.svg.board(board))
        data["won"] = won
        yield FeedItem(
            id=f"chess_{int(dt.timestamp())}",
            title=f"Chess ({me})",
            ftype="chess",
            when=dt,
            data=data,
            url=url,
        )
