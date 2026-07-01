"""Candidate discovery from configured pages."""

from __future__ import annotations

from urllib.parse import urlparse

import aiohttp
from bs4 import BeautifulSoup

from .models import SourceCandidate
from .parser import discover_urls_from_text
from .robots import USER_AGENT, RobotsCache


async def discover_candidates(config: dict, robots: RobotsCache) -> list[SourceCandidate]:
    """Discover additional candidates from public directory pages.

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
            for candidate_url in urls:
                if not isinstance(candidate_url, str) or not candidate_url.startswith(("http://", "https://")):
                    continue
                found.setdefault(
                    candidate_url,
                    SourceCandidate(
                        name=urlparse(candidate_url).netloc,
                        url=candidate_url,
                        origin=f"discovery:{page.get('name', url)}",
                        priority=int(page.get("priority", 1)),
                    ),
                )
                if len(found) >= max_candidates:
                    return list(found.values())
    return list(found.values())
