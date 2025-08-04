from ..src.utilities.utils import parse_url


class TestParseUrl:
    def test_parse_url_nrl():
        url = "https://www.nrl.com/draw/?competition=111&round=23&season=2025"
        competition_code, year, round_num = parse_url(url)
        assert competition_code == 116
        assert round == 23
        assert year == 2025

    def test_parse_url_noparams():
        url = "https://www.google.com"
        competition_code, year, round_num = parse_url(url)
        assert competition_code == None
        assert round == None
        assert year == None
