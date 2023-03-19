A personal feed/website using [`HPI`](https://github.com/seanbreckenridge/HPI)

Live at <https://sean.fish/feed/>

<img src="https://github.com/seanbreckenridge/my_feed/blob/master/.github/my_feed.png" width=500/>

This uses HPI as the data source, and then handles cleaning up the data some/enriching it by using local data/cached API requests

`src/my_feed/` is installed into my global environment so I can use the data this generates as a sort of 'normalized' version of history.

To install:

```bash
git clone https://github.com/seanbreckenridge/my_feed
pip install -e ./my_feed
```

- [`listens`](https://github.com/seanbreckenridge/HPI-personal/blob/master/scripts/listens)

### Data Sources:

- Music
  - [listenbrainz_export](https://github.com/seanbreckenridge/listenbrainz_export) for scrobbles, from [listenbrainz](https://listenbrainz.org/) (similar to last.fm)
  - [mpv_history_daemon](https://github.com/seanbreckenridge/mpv-history-daemon) for [mpv](https://github.com/mpv-player/mpv) history
- Movies/TV Shows
  - [traktexport](https://github.com/seanbreckenridge/traktexport), grabbing data from [Trakt](https://trakt.tv/). Trakt provides [TMDB](http://themoviedb.org/) IDs, so I can fetch images for each episode
- Games
  - [grouvee_export](https://github.com/seanbreckenridge/grouvee_export) to parse the CSV export from [Grouvee](https://www.grouvee.com/) with images from [GiantBomb](https://www.giantbomb.com/)
  - [steamscraper](https://github.com/seanbreckenridge/steamscraper) to scrape my [steam](https://steamcommunity.com/) achievements
  - [chess_export](https://github.com/seanbreckenridge/chess_export) for chess games, the [python-chess.svg](https://python-chess.readthedocs.io/en/latest/) package to parse the PGNs into SVGs
- Albums
  - [albums](https://github.com/seanbreckenridge/albums) which requests out to [discogs](https://www.discogs.com/)
- Anime/Manga
  - [malexport](https://github.com/seanbreckenridge/malexport/), saving my data from [MAL](https://myanimelist.net/)

If not mentioned its likely a module in [HPI](https://github.com/seanbreckenridge/HPI)

I periodically index all my data [in the background](https://sean.fish/d/my_feed_index.job?dark):

```
Extracting my_feed.sources.listens.history...
Extracting my_feed.sources.listens.history: 5388 items (took 0.14 seconds)
Extracting my_feed.sources.games.steam...
Extracting my_feed.sources.games.steam: 285 items (took 0.01 seconds)
Extracting my_feed.sources.games.osrs...
Extracting my_feed.sources.games.osrs: 924 items (took 0.03 seconds)
Extracting my_feed.sources.games.game_center...
Extracting my_feed.sources.games.game_center: 141 items (took 0.02 seconds)
Extracting my_feed.sources.games.grouvee...
Extracting my_feed.sources.games.grouvee: 243 items (took 0.15 seconds)
Extracting my_feed.sources.games.chess...
Extracting my_feed.sources.games.chess: 681 items (took 2.98 seconds)
Extracting my_feed.sources.trakt.history...
Extracting my_feed.sources.trakt.history: 15327 items (took 11.51 seconds)
Extracting my_feed.sources.mpv.history...
Extracting my_feed.sources.mpv.history: 13807 items (took 13.67 seconds)
Extracting my_feed.sources.nextalbums.history...
Extracting my_feed.sources.nextalbums.history: 1938 items (took 2.36 seconds)
Extracting my_feed.sources.mal.history...
Extracting my_feed.sources.mal.history: 20865 items (took 3.58 seconds)
Total: 59599 items
Writing to 'backend/data/1644267551.pickle'
```

... which then gets synced up and combined into the `sqlite` database on the [`backend`](./backend/); all handled by [`index`](./index)

That has a [front-end](https://sean.fish/feed/) so I can view/filter/sort stuff and view the data as an infinite scrollable list

Served with `nginx` in prod, like:

```
location /feed/ {
  proxy_pass http://127.0.0.1:4500/feed;
}

location /feed/_next/ {
  # required since the above proxy pass doesnt end with '/'
  proxy_pass http://127.0.0.1:4500/feed/_next/;
}

location /feed_api/ {
  proxy_pass http://127.0.0.1:5100/;
}
```

### Config:

This uses the `HPI` config structure (which you'd probably already have setup if you're using this)

So, in `~/.config/my/my/config/feed.py`, create a top-level `sources` function, which returns each _function_:

```python
from typing import Iterator, Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from my_feed.sources.model import FeedItem


def sources() -> Iterator[Callable[[], Iterator["FeedItem"]]]:
    from my_feed.sources import games

    yield games.steam
    yield games.osrs
    yield games.game_center
    yield games.grouvee
    yield games.chess

    from my_feed.sources import (
        trakt,
        listens,
        nextalbums,
        mal,
        mpv,
        facebook_spotify_listens,
    )

    yield trakt.history
    yield listens.history
    yield nextalbums.history
    yield mal.history
    yield mpv.history
    yield facebook_spotify_listens.history
```

The [`index`](./index) script in this repo first warms the `my.time.tz.via_location` cache, so that timezones can be estimated for some of the data sources here, does an `rsync` for some images hosted here, and then runs an `my_feed index` to save pickled objects to a local file. Thats then synced up to my server with `scp`, and then the server is pinged (at `/check`), which makes the server process the pickle files, updating the local sqlite database

To blur images, `my_feed index` accepts a `-B` flag, which lets you match against the `id`, `title`, or `image_url` with an [`fnmatch`](https://docs.python.org/3/library/fnmatch.html#module-fnmatch) or a `regex`. Those are placed in a file, one per line, for example:

```
id:*up_2009_*
title:*up_2009_*
image_url:*up_2009_*
id_regex:.*up_2009_.*
title_regex:.*up_2009_.*
image_url_regex:.*up_2009_.*
```

If I make a breaking change, I run a `re-index` instead, like `FEED_REINDEX=1 my_feed index` which just `ssh`s into the server and deletes the database before hitting the `/check` endpoint to force a rebuild of the whole database
