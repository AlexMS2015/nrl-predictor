# import pytest
# from scraper.utilities.utils import parse_url


# class TestParseUrl:
#     def test_parse_url_nrl(self):
#         url = "https://www.nrl.com/draw/?competition=111&round=23&season=2025"
#         competition_code, year, round_num = parse_url(url)
#         assert competition_code == "111"
#         assert round_num == 22
#         assert year == 2025

#     def test_parse_url_keyerror(self):
#         url = "https://www.nrl.com/draw/?competition=111&round=23"
#         with pytest.raises(KeyError):
#             competition_code, year, round_num = parse_url(url)

#     def test_parse_url_valueerror(self):
#         url = "https://www.nrl.com/draw/?competition=111&round=abc&season=2025"
#         with pytest.raises(ValueError):
#             competition_code, year, round_num = parse_url(url)
