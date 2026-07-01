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
    r"18\+|tvbox18|(?:^|[\W_])s?18(?:[\W_]|$)|成人|福利|情色|伦理|午夜|AV|里番|国产自拍|日本无码|国产自拍|写真|擦边|成人视频|adult|porn|sex|xxx",
    re.IGNORECASE,
)


def sniff_format(text: str, content_type: str = "", url: str = "") -> SourceFormat:
    """Infer source format from response body, content type, and URL."""

    lowered = f"{content_type} {url}".lower()
    sample = text.lstrip()[:200].lower()
    if url.lower().split("?", 1)[0].endswith((".js", ".css", ".html", ".htm")):
        return SourceFormat.UNKNOWN
    if any(kind in lowered for kind in ("javascript", "text/css")):
        return SourceFormat.UNKNOWN
    if "text/html" in lowered and not url.lower().endswith((".json", ".txt", ".m3u", ".m3u8")):
        return SourceFormat.UNKNOWN
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
        return _parse_tvbox_json(text, url)
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


def _parse_tvbox_json(text: str, url: str = "") -> ParsedContent:
    try:
        data: Any = json.loads(text)
    except json.JSONDecodeError:
        try:
            data = json.loads(_strip_jsonc(text))
        except json.JSONDecodeError:
            return ParsedContent(format=SourceFormat.TVBOX_JSON, valid_items=[])

    items: list[dict[str, Any]] = []
    adult_hits = 0
    total_named_entries = 0
    adult = looks_adult(url, _title_from_json(data))
    if isinstance(data, dict):
        for key in ("urls", "sites", "lives", "parses", "spider", "rules"):
            value = data.get(key)
            if isinstance(value, list):
                for entry in value:
                    if isinstance(entry, dict):
                        api = str(entry.get("api") or entry.get("url") or entry.get("ext") or "")
                        name = str(entry.get("name") or "")
                        if name or api:
                            total_named_entries += 1
                        if looks_adult(name, api):
                            adult_hits += 1
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
    if total_named_entries:
        adult = adult or (adult_hits / total_named_entries) >= 0.25
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


def _strip_jsonc(text: str) -> str:
    """Remove common JSONC comments and trailing commas without touching string literals."""

    output = []
    in_string = False
    escape = False
    i = 0
    while i < len(text):
        char = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""
        if in_string:
            output.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            i += 1
            continue
        if char == '"':
            in_string = True
            output.append(char)
            i += 1
            continue
        if char == "/" and nxt == "/":
            i += 2
            while i < len(text) and text[i] not in "\r\n":
                i += 1
            continue
        if char == "/" and nxt == "*":
            i += 2
            while i + 1 < len(text) and not (text[i] == "*" and text[i + 1] == "/"):
                i += 1
            i += 2
            continue
        output.append(char)
        i += 1
    cleaned = "".join(output)
    return re.sub(r",\s*([}\]])", r"\1", cleaned)
