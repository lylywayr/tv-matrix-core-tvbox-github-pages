"""robots.txt compliance helpers."""

from __future__ import annotations

import asyncio
import urllib.robotparser
from dataclasses import dataclass
from time import monotonic
from urllib.parse import urljoin, urlparse

import aiohttp


USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36 TV-Matrix-Core/0.1"
)


@dataclass(slots=True)
class RobotsPolicy:
    """Parsed robots policy plus crawl-delay metadata."""

    parser: urllib.robotparser.RobotFileParser
    crawl_delay: float
    last_access: float = 0.0


class RobotsCache:
    """Fetch and cache robots.txt policies per host."""

    def __init__(self) -> None:
        self._cache: dict[str, RobotsPolicy] = {}
        self._lock = asyncio.Lock()

    async def allowed(self, session: aiohttp.ClientSession, url: str) -> bool:
        """Return whether USER_AGENT may fetch the URL."""

        policy = await self._policy_for(session, url)
        return policy.parser.can_fetch(USER_AGENT, url)

    async def wait_for_delay(self, session: aiohttp.ClientSession, url: str) -> None:
        """Respect Crawl-delay for a host before issuing a request."""

        policy = await self._policy_for(session, url)
        async with self._lock:
            wait = max(0.0, policy.crawl_delay - (monotonic() - policy.last_access))
            if wait:
                await asyncio.sleep(wait)
            policy.last_access = monotonic()

    async def _policy_for(self, session: aiohttp.ClientSession, url: str) -> RobotsPolicy:
        parsed = urlparse(url)
        root = f"{parsed.scheme}://{parsed.netloc}"
        if root in self._cache:
            return self._cache[root]
        robots_url = urljoin(root, "/robots.txt")
        parser = urllib.robotparser.RobotFileParser()
        parser.set_url(robots_url)
        crawl_delay = 0.0
        try:
            async with session.get(robots_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                text = await response.text(errors="ignore")
                parser.parse(text.splitlines())
                delay = parser.crawl_delay(USER_AGENT) or parser.crawl_delay("*")
                crawl_delay = float(delay or 0)
        except Exception:
            parser.parse([])
        policy = RobotsPolicy(parser=parser, crawl_delay=crawl_delay)
        self._cache[root] = policy
        return policy
