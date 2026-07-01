from tv_matrix.models import SourceFormat
from tv_matrix.parser import parse_content


def test_parse_m3u_streams():
    parsed = parse_content("#EXTM3U\n#EXTINF:-1,CCTV\nhttps://example.com/a.m3u8\n")
    assert parsed.format == SourceFormat.M3U
    assert parsed.valid_items[0]["name"] == "CCTV"


def test_parse_tvbox_json_sites():
    parsed = parse_content('{"sites":[{"name":"A","api":"https://example.com/api.php"}]}')
    assert parsed.format == SourceFormat.TVBOX_JSON
    assert parsed.valid_items


def test_parse_txt_urls():
    parsed = parse_content("线路 https://example.com/tvbox.json")
    assert parsed.format == SourceFormat.TXT
    assert parsed.valid_items[0]["url"] == "https://example.com/tvbox.json"
