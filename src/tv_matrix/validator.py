"""Asynchronous multi-dimensional source validation."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from time import perf_counter
from urllib.parse import urlparse

import aiohttp

from .models import SourceCandidate, SourceFormat, ValidationResult
from .parser import parse_content
from .robots import USER_AGENT, RobotsCache


class SourceValidator:
    """Validate URL reachability, content usefulness, and optional TCP connectivity."""

    def __init__(self, config: dict, robots: RobotsCache) -> None:
        self.config = config
        self.robots = robots
        self.retries = int(config.get("retries", 2))
        self.backoff_base = float(config.get("backoff_base_seconds", 0.8))
        self.tcp_threshold = int(config.get("tcp_probe_priority_threshold", 7))
        self.tcp_ports = [int(p) for p in config.get("tcp_ports", [80, 443, 8080])]

    async def validate_many(self, candidates: list[SourceCandidate]) -> list[ValidationResult]:
        """Validate candidates concurrently."""

        concurrency = int(self.config.get("concurrency", 24))
        timeout = aiohttp.ClientTimeout(total=float(self.config.get("max_timeout_seconds", 20)))
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "application/json,text/plain,application/x-mpegURL,text/html,*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        }
        semaphore = asyncio.Semaphore(concurrency)
        async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
            tasks = [self._guarded_validate(semaphore, session, candidate) for candidate in candidates]
            return await asyncio.gather(*tasks)

    async def _guarded_validate(
        self,
        semaphore: asyncio.Semaphore,
        session: aiohttp.ClientSession,
        candidate: SourceCandidate,
    ) -> ValidationResult:
        async with semaphore:
            return await self.validate_one(session, candidate)

    async def validate_one(
        self, session: aiohttp.ClientSession, candidate: SourceCandidate
    ) -> ValidationResult:
        """Validate one source with retry and exponential backoff."""

        last_error = "unknown"
        for attempt in range(self.retries + 1):
            try:
                if not await self.robots.allowed(session, candidate.url):
                    return ValidationResult.failure(candidate, "blocked_by_robots_txt")
                await self.robots.wait_for_delay(session, candidate.url)
                return await self._attempt(session, candidate)
            except Exception as exc:
                last_error = exc.__class__.__name__
                if attempt < self.retries:
                    await asyncio.sleep(self.backoff_base * (2**attempt))
        return ValidationResult.failure(candidate, last_error)

    async def _attempt(
        self, session: aiohttp.ClientSession, candidate: SourceCandidate
    ) -> ValidationResult:
        started = perf_counter()
        async with session.get(candidate.url, allow_redirects=True) as response:
            text = await response.text(errors="ignore")
            elapsed_ms = int((perf_counter() - started) * 1000)
            parsed = parse_content(text, response.headers.get("content-type", ""), str(response.url))
            tcp_ok = None
            if candidate.priority >= self.tcp_threshold:
                tcp_ok = await self._tcp_probe(candidate.url)
            ok = 200 <= response.status < 400 and parsed.valid_items
            return ValidationResult(
                candidate=candidate,
                checked_at=datetime.now(UTC).isoformat(),
                ok=bool(ok),
                http_status=response.status,
                elapsed_ms=elapsed_ms,
                content_format=parsed.format if parsed.valid_items else SourceFormat.UNKNOWN,
                content_quality=parsed.quality_ratio,
                valid_item_count=len(parsed.valid_items),
                tcp_ok=tcp_ok,
                error=None if ok else "no_valid_content",
                adult=parsed.adult,
            )

    async def _tcp_probe(self, url: str) -> bool:
        parsed = urlparse(url)
        host = parsed.hostname
        if not host:
            return False
        ports = [parsed.port] if parsed.port else self.tcp_ports
        for port in ports:
            try:
                reader, writer = await asyncio.wait_for(asyncio.open_connection(host, port), timeout=3)
                writer.close()
                await writer.wait_closed()
                del reader
                return True
            except Exception:
                continue
        return False
