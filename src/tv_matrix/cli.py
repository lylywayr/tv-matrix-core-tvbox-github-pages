"""Command line entry point for TV-Matrix-Core."""

from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

import aiohttp

from .config import load_config
from .models import SourceCandidate
from .output import rollback_latest
from .robots import RobotsCache
from .runner import run
from .validator import SourceValidator


def main() -> None:
    """Parse CLI arguments and dispatch local debug commands."""

    parser = argparse.ArgumentParser(prog="tv-matrix")
    parser.add_argument("--root", default=".", help="Repository root")
    sub = parser.add_subparsers(dest="command", required=True)

    run_parser = sub.add_parser("run", help="Run the full pipeline")
    run_parser.add_argument("--config", default="config/sources.yml")

    validate_parser = sub.add_parser("validate", help="Validate one URL")
    validate_parser.add_argument("--url", required=True)
    validate_parser.add_argument("--config", default="config/sources.yml")

    rollback_parser = sub.add_parser("rollback", help="Rollback output artifacts to latest backup")
    rollback_parser.add_argument("--output", default="output")

    args = parser.parse_args()
    root = Path(args.root).resolve()
    if args.command == "run":
        run(root, root / args.config)
    elif args.command == "validate":
        asyncio.run(_validate_one(root / args.config, args.url))
    elif args.command == "rollback":
        restored = rollback_latest(root / args.output)
        print(f"restored {restored}")


async def _validate_one(config_path: Path, url: str) -> None:
    config = load_config(config_path)
    robots = RobotsCache()
    validator = SourceValidator(config.validation, robots)
    async with aiohttp.ClientSession() as session:
        result = await validator.validate_one(session, SourceCandidate(name=url, url=url, priority=10))
    print(result)


if __name__ == "__main__":
    main()
