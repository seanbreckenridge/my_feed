import string
from typing import Iterator, Optional, Dict, Any
from datetime import datetime, timezone

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


def grouvee() -> Iterator[FeedItem]:
    from my.grouvee.export import played

    for g in played():
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
            release_date=g.release_date,
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
        data = {}
        if isinstance(sc.description, Level):
            id_ = f"osrs_level_{sc.description.skill.casefold()}_{sc.description.level}_{int(sc.dt.timestamp())}"
            data = sc.description._asdict()
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
        else:
            raise RuntimeError(f"Unexpected game {type(game)} {game}")
        pgn_str = game.pgn
        data["won"] = won
        data["pgn"] = pgn_str
        pgn = chess.pgn.read_game(StringIO(pgn_str))
        assert pgn is not None
        data["svg"] = str(chess.svg.board(pgn.board()))
        title = str(pgn.headers.get("Event", "Chess Game"))
        yield FeedItem(
            id=f"chess_{int(dt.timestamp())}",
            title=title,
            ftype="chess",
            when=dt,
            data=data,
            url=url,
        )
