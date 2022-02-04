A personal feed/website using my [HPI](https://github.com/seanbreckenridge/HPI)

`src/my_feed/` is installed into my global environment in case I ever want to use media_feed as a sort of 'normalized' version of history; installed as `pip install -e .`

I periodically index all my data in the background:

```
$ my_feed index ./server/data/$(epoch).pickle
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
Writing to 'server/data/1643954180.pickle'
```

... which then gets synced up and combined into the `sqlite` database on the [`server`](./server/)

That has a front-end so I can view/filter/sort stuff
