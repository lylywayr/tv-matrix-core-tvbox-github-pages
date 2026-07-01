"""Content sniffing and parser implementations for TVBox, M3U, and TXT."""

from __future__ import annotations

import json
import re
from typing import Any

from .models import ParsedContent, SourceFormat

URL_RE = re.compile(r"(?:https?:)?//[^\s\"'<>]+", re.IGNORECASE)
STREAM_RE = re.compile(r"https?://[^\s\"'<>]+\.(?:m3u8|mp4|flv|ts)(?:\?[^\s\"'<>]+)?", re.IGNORECASE)
CONFIG_URL_RE = re.compile(
    r"https?://[^\s\"'<>]+(?:\.json|\.m3u|\.m3u8|\.txt|/tv|/TVBox|/box|/mao|/api)(?:\?[^\s\"'<>]+)?",
    re.IGNORECASE,
)
ADULT_RE = re.compile(
    r"18\+|成人|福利|情色|伦理|午夜|AV|里番|国产自拍|日本无码|国产自拍|写真|擦边|成人视频|adult|porn|sex|xxx",
    re.IGNORECASE,
)


def sniff_format(text: str, content_type: str = "", url: str = "") -> SourceFormat:
    """Infer source format from response body, content type, and URL."""

    lowered = f"{content_type} {url}".lower()
    sample = text.lstrip()[:200].lower()
    if "mpegurl" in lowered or url.lower().endswith((".m3u", ".m3u8")) or sample.startswith("#extm3u"):
        return SourceFormat.M3U
    if "json" in lowered or sample.startswith("{") or sample.startswith("["):
        return SourceFormat.TVBOX_JSON
    if URL_RE.search(text):
        return SourceFormat.TXT
    return SourceFormat.UNKNOWN


def parse_content(text: str, content_type: str = "", url: str = "") -> ParsedContent:
    """Parse response text into normalized candidate items.

    Extension point:
        Add a parser branch here for new public playlist conventions while
        preserving the ParsedContent contract.
    """

    fmt = sniff_format(text, content_type, url)
    if fmt == SourceFormat.TVBOX_JSON:
        return _parse_tvbox_json(text)
    if fmt == SourceFormat.M3U:
        return _parse_m3u(text)
    if fmt == SourceFormat.TXT:
        return _parse_txt(text)
    return ParsedContent(format=SourceFormat.UNKNOWN, valid_items=[])


def discover_urls_from_text(text: str) -> list[str]:
    """Extract likely line URLs from arbitrary HTML or text."""

    urls = []
    for match in URL_RE.findall(text):
        cleaned = match.rstrip(").,;]")
        if cleaned.startswith("//"):
            cleaned = "https:" + cleaned
        if cleaned not in urls:
            urls.append(cleaned)
    return urls


def looks_adult(*values: str | None) -> bool:
    """Return whether text contains adult-source indicators."""

    return any(value and ADULT_RE.search(value) for value in values)


def _parse_tvbox_json(text: str) -> ParsedContent:
    try:
        data: Any = json.loads(text)
    except json.JSONDecodeError:
        return ParsedContent(format=SourceFormat.TVBOX_JSON, valid_items=[])

    items: list[dict[str, Any]] = []
    adult = looks_adult(text)
    if isinstance(data, dict):
        for key in ("urls", "sites", "lives", "parses", "spider", "rules"):
            value = data.get(key)
            if isinstance(value, list):
                for entry in value:
                    if isinstance(entry, dict):
                        api = str(entry.get("api") or entry.get("url") or entry.get("ext") or "")
                        name = str(entry.get("name") or "")
                        adult = adult or looks_adult(name, api)
                        if (api.startswith(("http://", "https://")) or key in {"urls", "sites", "lives"}) and (
                            key in {"urls", "sites", "lives", "parses"} or api
                        ):
                            items.append({"type": key, "name": entry.get("name"), "url": api})
            elif isinstance(value, str) and value.startswith(("http://", "https://")):
                items.append({"type": key, "url": value})
    streams = STREAM_RE.findall(text)
    for stream in streams[:20]:
        items.append({"type": "stream", "url": stream})
    has_tvbox_shape = isinstance(data, dict) and any(
        isinstance(data.get(key), (list, str)) for key in ("urls", "sites", "lives", "parses", "spider")
    )
    return ParsedContent(
        format=SourceFormat.TVBOX_JSON,
        valid_items=items if has_tvbox_shape and items else [],
        raw_title=_title_from_json(data),
        adult=adult,
    )


def _parse_m3u(text: str) -> ParsedContent:
    items = []
    current_name = None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#EXTINF"):
            current_name = line.rsplit(",", 1)[-1] if "," in line else None
        elif line.startswith(("http://", "https://")):
            items.append({"type": "stream", "name": current_name, "url": line})
            current_name = None
    return ParsedContent(format=SourceFormat.M3U, valid_items=items, adult=looks_adult(text))


def _parse_txt(text: str) -> ParsedContent:
    urls = [url for url in discover_urls_from_text(text) if CONFIG_URL_RE.search(url) or STREAM_RE.search(url)]
    items = [{"type": "url", "url": url} for url in urls]
    has_media_shape = len(items) >= 2 or any(STREAM_RE.search(item["url"]) for item in items)
    return ParsedContent(
        format=SourceFormat.TXT,
        valid_items=items if has_media_shape else [],
        adult=looks_adult(text),
    )


def _title_from_json(data: Any) -> str | None:
    if isinstance(data, dict):
        for key in ("name", "title", "spider"):
            value = data.get(key)
            if isinstance(value, str) and value:
                return value[:80]
    return None
