#!/usr/bin/env python3

"""
Listens from my local mpv history

This tries to use some path matching/ID3/heuristics
to improve the metadata here
"""

import os
import json
from pathlib import Path
from functools import cache
from math import isclose
from typing import Iterator, Tuple, Optional, Dict, TypeGuard

from mutagen.mp3 import MP3, MutagenError  # type: ignore[import]
from mutagen.easyid3 import EasyID3  # type: ignore[import]
from my.mpv.history_daemon import history as mpv_history, Media
from my.utils.input_source import InputSource

from .model import FeedItem
from ..log import logger
from .common import click, FeedBackgroundError


def _path_keys(p: Path | str) -> Iterator[Tuple[str, ...]]:
    pp = Path(p)

    *_rest, artist, album, song_full = pp.parts
    song, ext = os.path.splitext(song_full)

    yield tuple([artist, album, song])
    yield tuple([album, song])
    # if I removed something like '(Explicit)' from the file name
    yield tuple([album, song.split("(")[0].strip()])
    yield tuple([song])


@cache
def _music_dir_matches() -> Dict[Tuple[str, ...], Path]:
    """
    Scan my current music directory, creating lookups for possible path matches. For example:

    Trying to match:
        /home/sean/Music/Artist/Album/Song.mp3

    So to the result dict we should add:
        Artist/Album/Song (the last 3 paths, without extension)
        [Album|Arist]/Song (the last 2 paths, without extension)
        Song (last path)
    """
    music_dir = Path(os.environ["XDG_MUSIC_DIR"])
    assert music_dir.exists(), f"{music_dir} doesnt exist"
    results: dict[Tuple[str, ...], Path] = {}

    for f in music_dir.rglob("*.mp3"):
        for pkey in _path_keys(f):
            if pkey not in results:
                results[pkey] = f

    return results


def _manual_mpv_datafile() -> Path:
    return Path(os.path.join(os.environ["HPIDATA"], "feed_mpv_fixes.json"))


def _has_id3_data(id3: EasyID3, key: str) -> bool:
    if key in id3:
        return len(id3[key]) > 0
    return False


BASIC_ID3_TAGS = {
    "title",
    "artist",
    "album",
}


def _valid_daemon_data(daemon_data: Dict[str, str]) -> bool:
    return all(bool(daemon_data.get(tag)) for tag in BASIC_ID3_TAGS)


Metadata = Tuple[str, str, str]


def _daemon_to_metadata(daemon_data: Dict[str, str]) -> Metadata:
    return (
        daemon_data["title"],
        daemon_data["album"],
        daemon_data["artist"],
    )


class JSONCache:
    def __init__(self):
        self.load_data()

    def load_data(self) -> Dict[str, Metadata]:
        self.datafile = _manual_mpv_datafile()
        self.data: Dict[str, Metadata] = {}
        if self.datafile.exists():
            self.data = json.loads(self.datafile.read_text())
        return self.data

    def _save_data(self, daemon_data: Dict[str, str], for_path: str) -> Metadata:
        metadata = _daemon_to_metadata(daemon_data)
        self.data[for_path] = metadata
        return metadata

    def _write(self):
        logger.debug(f"Writing to {self.datafile}...")
        encoded = json.dumps(self.data, separators=(",", ":"))
        self.datafile.write_text(encoded)


JSONData = JSONCache()


def _fix_media(
    m: Media, *, daemon_data: Dict[str, str], is_broken: bool = False
) -> Metadata:
    """Fix broken metadata on scrobbles, and save my responses to a cache file"""

    # if we can find the file locally still, use that to extract data from fixed (I've
    # since ran https://github.com/seanbreckenridge/plaintext_playlist_py/blob/master/bin/id3stuff on all my music, so it has correct tags)
    # mp3 file

    # if we've fixed this in the past
    if m.path in JSONData.data:
        logger.debug(f"Using cached data for {m.path}: {JSONData.data[m.path]}")
        return JSONData.data[m.path]

    album, artist, title = None, None, None
    if m.media_duration is None:
        logger.debug(f"No media duration on {m}, cant compare to local files")
    else:
        for pkey in _path_keys(m.path):
            if match := _music_dir_matches().get(pkey):
                assert match.suffix == ".mp3", str(match)
                mp3_f = MP3(str(match))
                # media duration is within 1%
                if mp3_f.info and isclose(m.media_duration, mp3_f.info.length, rel_tol=0.01):
                    # if this has id3 data to pull from
                    try:
                        id3 = EasyID3(str(match))
                    except MutagenError:
                        continue
                    if all(_has_id3_data(id3, tag) for tag in BASIC_ID3_TAGS):
                        title = id3["title"][0]
                        artist = id3["artist"][0]
                        album = id3["album"][0]
                        # we matched a filename with a very close duration and path name
                        # and the data is all the same, so the data was correct to begin with
                        if (
                            _valid_daemon_data(daemon_data)
                            and title == daemon_data.get("title")
                            and artist == daemon_data.get("artist")
                            and album == daemon_data.get("album")
                        ):
                            # dont write any changes to cachefile, data was already good
                            return _daemon_to_metadata(daemon_data)
                        print(
                            f"""Resolving {m}

Matched {match}

title: '{daemon_data.get('title')}' -> '{title}'
artist: '{daemon_data.get('artist')}' -> '{artist}'
album: '{daemon_data.get('album')}' -> '{album}'
"""
                        )
                    if click().confirm("Use metadata?", default=True):
                        assert title and artist and album
                        return JSONData._save_data(
                            {"title": title, "artist": artist, "album": album}, m.path
                        )

    # we could've still tried to improve using the heuristics above
    # even if the data wasnt broken
    #
    # if we couldn't, but this had decent data to begin with, dont prompt me
    # (else we'd be prompting all the thousands of mpv history entries)
    if not is_broken:
        return _daemon_to_metadata(daemon_data)

    # use path as a key
    click().echo(f"Missing data: {m}", err=True)
    title = click().prompt("title").strip()
    subtitle = click().prompt("album name").strip()
    creator = click().prompt("artist name").strip()

    # write data
    return JSONData._save_data(
        {"title": title, "artist": creator, "album": subtitle}, for_path=m.path
    )


def _is_some(x: Optional[str]) -> TypeGuard[str]:
    if x is None:
        return False
    return bool(x.strip())


def _has_metadata(m: Media) -> Optional[Metadata]:
    if data := m.metadata:
        title = data.get("title")
        album = data.get("album")
        artist = data.get("artist")
        if _is_some(title) and _is_some(album) and _is_some(artist):
            return (
                title.strip(),
                album.strip(),
                artist.strip(),
            )
    return None


IGNORE_EXTS = {
    ".mp4",
    ".mkv",
    ".m4v",
    ".jpg",
    ".avi",
    ".png",
    ".gif",
    ".jpeg",
    ".mov",
    ".wav",
    ".webm",
    ".aiff",
    ".iso",
    ".flv",
    ".unknown_video",
}


ALLOW_EXT = {".flac", ".mp3", ".ogg", ".m4a", ".opus"}


ALLOW_PREFIXES: set[str] = set()
if "XDG_MUSIC_DIR" in os.environ:
    ALLOW_PREFIXES.add(os.environ["XDG_MUSIC_DIR"])
IGNORE_PREFIXES: set[str] = set()
try:
    from my.config.feed import ignore_mpv_prefixes, allow_mpv_prefixes  # type: ignore[import]

    ALLOW_PREFIXES.update(allow_mpv_prefixes)
    IGNORE_PREFIXES.update(ignore_mpv_prefixes)
except ImportError as e:
    logger.warning("Could not import feed configuration", exc_info=e)


def _media_is_allowed(media: Media) -> bool:
    if (
        media.is_stream
        or media.path.startswith("/tmp")
        or media.path.startswith("/dev")
    ):
        return False

    # ignore/allow based on extensions
    _, ext = os.path.splitext(media.path)
    if ext.lower() in IGNORE_EXTS:
        return False

    if ext.lower() not in ALLOW_EXT:
        logger.warning(f"Ignoring, unknown extension: {media}")
        return False

    # ignore/allow based on absolute path

    if ALLOW_PREFIXES:
        if any(media.path.startswith(prefix) for prefix in ALLOW_PREFIXES):
            return True
    if IGNORE_PREFIXES:
        if any(media.path.startswith(prefix) for prefix in IGNORE_PREFIXES):
            logger.debug(f"Ignoring, matches ignore prefix list: {media.path}")
            return False

    # i.e., if we have no allow/ignore prefixes, then we allow everything
    # so, this lets user know that their allow/ignore prefixes arent exhaustive
    if len(ALLOW_PREFIXES) > 0 or len(IGNORE_PREFIXES) > 0:
        logger.warning(
            f"Ignoring, didn't match either allow/ignore filters, add a prefix to match: {media.path}"
        )
        return False
    return True


def history(from_paths: Optional[InputSource] = None) -> Iterator[FeedItem]:
    kwargs = {}
    if from_paths is not None:
        kwargs["from_paths"] = from_paths

    for media in mpv_history(**kwargs):
        if not _media_is_allowed(media):
            continue

        # placeholder metadata
        title: Optional[str] = None
        subtitle: Optional[str] = None
        creator: Optional[str] = None

        # TODO: have a dict for artist/album names that were broken at one point, to improve them?

        try:
            if metadata := _has_metadata(media):
                title, subtitle, creator = metadata
                title, subtitle, creator = _fix_media(
                    media,
                    daemon_data={
                        "title": title,
                        "album": subtitle,
                        "artist": creator,
                    },
                    is_broken=False,
                )
            else:
                title, subtitle, creator = _fix_media(
                    media, daemon_data={}, is_broken=True
                )
        except FeedBackgroundError as e:
            logger.warning(
                f"Running in the background, cannot prompt for {media}", exc_info=e
            )
            continue

        dt = media.end_time

        # TODO: attach to album somehow (parent_id/collection)?
        yield FeedItem(
            id=f"mpv_{dt.timestamp()}",
            ftype="listen",
            title=title,
            subtitle=subtitle,
            creator=creator,
            when=dt,
        )
    JSONData._write()
