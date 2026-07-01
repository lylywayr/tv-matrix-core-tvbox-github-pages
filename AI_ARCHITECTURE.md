# AI Architecture Guide

This guide is written for Codex and other AI coding assistants that need to change TV-Matrix-Core safely.

## Data Flow

1. `config/sources.yml` defines fixed sources, discovery pages, validation behavior, scoring weights, and output settings.
2. `tv_matrix.runner.run_pipeline` loads config, opens `state/history.json`, discovers extra candidates, filters sleeping sources, validates active candidates, scores them, writes artifacts, updates docs, and renders the static site.
3. `tv_matrix.discovery` reads configured public pages, respects robots rules, and extracts candidate URLs.
4. `tv_matrix.validator` performs concurrent HTTP validation, retries with exponential backoff, runs parser checks, and optionally probes TCP ports for high-priority sources.
5. `tv_matrix.parser` sniffs and parses TXT, M3U, and TVBox JSON content into a normalized `ParsedContent` object.
6. `tv_matrix.scoring` combines recent success, lifetime success, latency, and content quality into a 0-100 health score.
7. `tv_matrix.output` validates and atomically writes `output/tvbox.json`, `output/live.m3u`, and `output/summary.json`, then keeps rotating backups.
8. `tv_matrix.readme` and `tv_matrix.site` render `README.md` and `public/` for GitHub Pages.

## Key Modules

- `src/tv_matrix/models.py`: shared dataclasses and enums. Change these first when adding a new pipeline field.
- `src/tv_matrix/config.py`: YAML loading and defaults. Add new config keys here only when the pipeline needs user control.
- `src/tv_matrix/parser.py`: content format sniffing and extraction.
- `src/tv_matrix/validator.py`: network behavior and validation dimensions.
- `src/tv_matrix/state.py`: persistent history, sleeping pool, and revival checks.
- `src/tv_matrix/scoring.py`: adaptive health score math.
- `src/tv_matrix/output.py`: artifact schemas, backups, and rollback.

## Extension Points

### Add a new source format

1. Add a value to `SourceFormat` in `models.py`.
2. Add detection logic in `parser.sniff_format`.
3. Add a parser branch in `parser.parse_content`.
4. Return `ParsedContent` with `valid_items` populated only when the content is genuinely useful.
5. Add parser tests in `tests/test_parser.py`.

### Add a validation dimension

1. Extend `ValidationResult` in `models.py` with the new field.
2. Fill the field in `validator.SourceValidator._attempt`.
3. Persist it in `state.HistoryStore.record_result` if it should affect history.
4. Update `scoring.score_result` if it should affect health score.
5. Surface it in `site.py` or `readme.py` only if users need to see it.

### Tune scoring

Most tuning should happen in `config/sources.yml` under `scoring.weights`. If the formula itself changes, edit `scoring.score_result` and keep the return range at 0-100.

### Change output schemas

Edit `output.generate_artifacts` and `_validate_tvbox` together. Keep atomic writes and backups intact. Do not write directly to final paths without `atomic_write`.

### Change crawl behavior

Edit `robots.py`, `discovery.py`, or `validator.py`. Keep `RobotsCache.allowed` and `wait_for_delay` in the request path so robots.txt and Crawl-delay remain enforced.

## Safety Rules

- Do not hard-code third-party source lists in code.
- Do not bypass robots.txt for discovery or validation.
- Do not remove artifact validation, atomic writes, or backup rotation.
- Prefer adding fields in a backward-compatible way because `state/history.json` is committed and long-lived.
