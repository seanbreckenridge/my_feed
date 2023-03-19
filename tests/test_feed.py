from my_feed.sources.trakt.tmdb import BASE_URL, _matches_trakt


def test_matches() -> None:
    assert _matches_trakt(BASE_URL + "/movie/145")
    assert _matches_trakt(BASE_URL + "/tv/523/season/2/episode/5")
    assert _matches_trakt(BASE_URL + "/tv/19481239/season/4912")
    assert _matches_trakt(BASE_URL + "/tv/423849")
    assert not _matches_trakt("https://something.org/tv/423849")
    assert not _matches_trakt(BASE_URL)


from my_feed.blur import Blurred, Attr, Blur


def test_parse_blob() -> None:
    from io import StringIO

    buf = StringIO(
        """
id:*up_2009_*
title: *up_2009_*
image_url: *up_2009_*
id_regex: .*up_2009_.*
title_regex: .*up_2009_.*
image_url_regex: .*up_2009_.*
    """
    )

    assert Blurred.parse_blob(buf) == Blurred(
        {
            Blur(Attr.ID_FNMATCH, r"*up_2009_*"),
            Blur(Attr.TITLE_FNMATCH, r"*up_2009_*"),
            Blur(Attr.IMAGE_FNMATCH, r"*up_2009_*"),
            Blur(Attr.ID_REGEX, r".*up_2009_.*"),
            Blur(Attr.TITLE_REGEX, r".*up_2009_.*"),
            Blur(Attr.IMAGE_REGEX, r".*up_2009_.*"),
        }
    )
