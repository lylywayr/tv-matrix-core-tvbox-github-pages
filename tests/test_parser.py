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
    parsed = parse_content("线路 https://example.com/tvbox.json\n备用 https://example.com/live.m3u")
    assert parsed.format == SourceFormat.TXT
    assert parsed.valid_items[0]["url"] == "https://example.com/tvbox.json"


def test_detect_adult_source():
    parsed = parse_content('{"sites":[{"name":"18+福利","api":"https://example.com/api.php"}]}')
    assert parsed.adult is True


def test_parse_multi_warehouse_urls():
    parsed = parse_content('{"urls":[{"name":"A","url":"https://example.com/tvbox.json"}]}')
    assert parsed.format == SourceFormat.TVBOX_JSON
    assert parsed.valid_items


def test_parse_jsonc_tvbox_config():
    parsed = parse_content(
        '{// comment\n"sites":[{"name":"A","api":"csp_A",},],}',
        url="https://example.com/config.json",
    )
    assert parsed.valid_items


def test_mixed_config_with_one_adult_entry_stays_normal():
    parsed = parse_content(
        '{"sites":[{"name":"A","api":"csp_A"},{"name":"福利","api":"csp_B"},{"name":"C","api":"csp_C"},{"name":"D","api":"csp_D"},{"name":"E","api":"csp_E"}]}'
    )
    assert parsed.adult is False
