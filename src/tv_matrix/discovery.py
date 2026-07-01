"""Candidate discovery from configured pages and public GitHub code search."""

from __future__ import annotations

import os
from typing import Any
from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

from .models import SourceCandidate
from .parser import discover_urls_from_text
from .robots import USER_AGENT, RobotsCache


async def discover_candidates(config: dict, robots: RobotsCache) -> list[SourceCandidate]:
    """Discover additional candidates from public directory pages and GitHub code search.

    Args:
        config: The discovery section of sources.yml.
        robots: Shared robots policy cache.

    Returns:
        Deduplicated candidate list.
    """

    if not config.get("enabled"):
        return []

    max_candidates = int(config.get("max_candidates_per_run", 50))
    timeout = aiohttp.ClientTimeout(total=15)
    headers = {"User-Agent": USER_AGENT, "Accept": "text/html,text/plain,application/json,*/*"}
    found: dict[str, SourceCandidate] = {}
    async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
        await _discover_from_seed_urls(config, session, found, max_candidates)
        await _discover_from_pages(config, robots, session, found, max_candidates)
        if len(found) < max_candidates:
            await _discover_from_github(config, session, found, max_candidates)
    return list(found.values())


async def _discover_from_seed_urls(
    config: dict,
    session: aiohttp.ClientSession,
    found: dict[str, SourceCandidate],
    max_candidates: int,
) -> None:
    """Discover candidates from curated automatic seed URLs.

    Seed URLs are not manual user input. They are maintained as an automatic
    discovery bootstrap list gathered from public TVBox/影视仓 projects.
    """

    max_urls_per_seed = int(config.get("max_urls_per_seed", 80))
    normalized_seeds = []
    for item in config.get("seed_urls", []):
        if isinstance(item, str):
            url, name, priority = item, urlparse(item).netloc, 7
        else:
            url = str(item.get("url"))
            name = str(item.get("name") or urlparse(url).netloc)
            priority = int(item.get("priority", 7))
        if not url.startswith(("http://", "https://")):
            continue
        normalized_seeds.append((url, name, priority))
        found.setdefault(
            url,
            SourceCandidate(
                name=name,
                url=url,
                origin="seed",
                priority=priority,
                tags=["auto-seed"],
            ),
        )
        if len(found) >= max_candidates:
            return

    for url, name, priority in normalized_seeds:
        if len(found) >= max_candidates:
            return
        try:
            async with session.get(url) as response:
                text = await response.text(errors="ignore")
        except Exception:
            continue
        _add_urls(found, discover_urls_from_text(text)[:max_urls_per_seed], f"seed-nested:{name}", priority - 1)


async def _discover_from_pages(
    config: dict,
    robots: RobotsCache,
    session: aiohttp.ClientSession,
    found: dict[str, SourceCandidate],
    max_candidates: int,
) -> None:
    """Discover URLs from user-configured public pages."""

    for page in config.get("pages", []):
        url = str(page.get("url"))
        if not await robots.allowed(session, url):
            continue
        await robots.wait_for_delay(session, url)
        try:
            async with session.get(url) as response:
                text = await response.text(errors="ignore")
        except Exception:
            continue
        urls = discover_urls_from_text(text)
        if "<a" in text.lower():
            soup = BeautifulSoup(text, "html.parser")
            urls.extend(a.get("href") for a in soup.find_all("a", href=True))
        _add_urls(found, urls, f"discovery:{page.get('name', url)}", int(page.get("priority", 2)))
        if len(found) >= max_candidates:
            return


async def _discover_from_github(
    config: dict,
    session: aiohttp.ClientSession,
    found: dict[str, SourceCandidate],
    max_candidates: int,
) -> None:
    """Discover likely TVBox/M3U endpoints from public GitHub code search.

    Extension point:
        Add other search providers here, keeping provider-specific rate limiting
        and result caps inside the provider function.
    """

    search_config = config.get("github_code_search", {}) or {}
    if not search_config.get("enabled"):
        return

    token = os.getenv("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    max_files = int(search_config.get("max_files_per_query", 8))
    max_urls_per_file = int(search_config.get("max_urls_per_file", 30))
    for query in search_config.get("queries", []):
        if len(found) >= max_candidates:
            return
        params = {"q": str(query), "per_page": str(max_files)}
        try:
            async with session.get("https://api.github.com/search/code", headers=headers, params=params) as response:
                if response.status in {401, 403, 422}:
                    continue
                payload: dict[str, Any] = await response.json(content_type=None)
        except Exception:
            continue
        for item in payload.get("items", [])[:max_files]:
            raw_url = _github_raw_url(str(item.get("html_url", "")))
            if not raw_url:
                continue
            found.setdefault(
                raw_url,
                SourceCandidate(
                    name=f"GitHub {item.get('name', 'source')}",
                    url=raw_url,
                    origin=f"github-search:{query}",
                    priority=4,
                    tags=["auto-discovered", "github"],
                ),
            )
            try:
                async with session.get(raw_url) as raw_response:
                    text = await raw_response.text(errors="ignore")
            except Exception:
                continue
            _add_urls(
                found,
                discover_urls_from_text(text)[:max_urls_per_file],
                f"github-file:{item.get('repository', {}).get('full_name', '')}",
                5,
            )
            if len(found) >= max_candidates:
                return


def _add_urls(
    found: dict[str, SourceCandidate],
    urls: list[str],
    origin: str,
    priority: int,
) -> None:
    """Add normalized HTTP URLs to the discovery set."""

    for candidate_url in urls:
        if not isinstance(candidate_url, str) or not candidate_url.startswith(("http://", "https://")):
            continue
        found.setdefault(
            candidate_url.rstrip(").,;]"),
            SourceCandidate(
                name=urlparse(candidate_url).netloc,
                url=candidate_url.rstrip(").,;]"),
                origin=origin,
                priority=priority,
                tags=["auto-discovered"],
            ),
        )


def _github_raw_url(html_url: str) -> str | None:
    """Convert a GitHub blob URL to a raw.githubusercontent.com URL."""

    marker = "github.com/"
    if marker not in html_url or "/blob/" not in html_url:
        return None
    path = html_url.split(marker, 1)[1]
    owner_repo, rest = path.split("/blob/", 1)
    return f"https://raw.githubusercontent.com/{owner_repo}/{rest}"
