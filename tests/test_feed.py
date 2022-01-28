from my_feed.sources.trakt.tmdb import BASE_URL, _matches_trakt


def test_matches() -> None:
    assert _matches_trakt(BASE_URL + "/movie/145")
    assert _matches_trakt(BASE_URL + "/tv/523/season/2/episode/5")
    assert _matches_trakt(BASE_URL + "/tv/19481239/season/4912")
    assert _matches_trakt(BASE_URL + "/tv/423849")
    assert not _matches_trakt("https://something.org/tv/423849")
    assert not _matches_trakt(BASE_URL)
