A personal feed/website using [`HPI`](https://github.com/seanbreckenridge/HPI)

Live at <https://sean.fish/feed/>

TODOs:

- more filters
- grab params from URL
- activity graphs
- better color scheme?
- cache images?

`src/my_feed/` is installed into my global environment in case I ever want to use media_feed as a sort of 'normalized' version of history; installed as `pip install -e .`

This uses HPI as the data source, and then handles cleaning up the data some/enriching it by using local data/cached API requests

Data Sources:

- Scrobbles
  - [listenbrainz_export](https://github.com/seanbreckenridge/listenbrainz_export) for scrobbles
  - [mpv_history_daemon](https://github.com/seanbreckenridge/mpv-history-daemon) for mpv history
- Movies/TV Shows
  - [traktexport](https://github.com/seanbreckenridge/traktexport), grabbing data from Trakt. Trakt provides [TMDB](http://themoviedb.org/) IDs, so I can fetch images for each episode
- Games
  - [grouvee_export](https://github.com/seanbreckenridge/grouvee_export) to parse the CSV export from Grouvee
  - [steamscraper](https://github.com/seanbreckenridge/steamscraper) to scrape my steam achievements
  - [chess_export](https://github.com/seanbreckenridge/chess_export) for chess games, the [python-chess.svg](https://python-chess.readthedocs.io/en/latest/) package to parse the PGNs into SVGs
- Albums
  - [albums](https://github.com/seanbreckenridge/albums) which requests out to [discogs](https://www.discogs.com/)
- Anime/Manga
  - [malexport](https://github.com/seanbreckenridge/malexport/), saving my data from [MAL](https://myanimelist.net/)

If not mentioned its likely a module in [HPI](https://github.com/seanbreckenridge/HPI)

I periodically index all my data [in the background](https://sean.fish/d/my_feed_index.job?dark):

```
$ my_feed index ./backend/data/$(epoch).pickle
Extracting my_feed.sources.scrobbles.history...
Extracting my_feed.sources.scrobbles.history: 5342 items (took 0.2 seconds)
Extracting my_feed.sources.games.steam...
Extracting my_feed.sources.games.steam: 285 items (took 0.01 seconds)
Extracting my_feed.sources.games.osrs...
Extracting my_feed.sources.games.osrs: 924 items (took 0.02 seconds)
Extracting my_feed.sources.games.game_center...
Extracting my_feed.sources.games.game_center: 141 items (took 0.02 seconds)
Extracting my_feed.sources.games.grouvee...
Extracting my_feed.sources.games.grouvee: 242 items (took 0.05 seconds)
Extracting my_feed.sources.games.chess...
Extracting my_feed.sources.games.chess: 676 items (took 2.61 seconds)
Extracting my_feed.sources.trakt.history...
Extracting my_feed.sources.trakt.history: 16355 items (took 23.43 seconds)
Extracting my_feed.sources.mpv.history...
Extracting my_feed.sources.mpv.history: 13654 items (took 19.3 seconds)
Extracting my_feed.sources.nextalbums.history...
Extracting my_feed.sources.nextalbums.history: 1938 items (took 2.41 seconds)
Extracting my_feed.sources.mal.history...
Extracting my_feed.sources.mal.history: 16638 items (took 3.68 seconds)
Total: 56195 items
Writing to 'backend/data/1643954180.pickle'
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
