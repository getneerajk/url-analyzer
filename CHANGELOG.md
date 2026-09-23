# Changelog

All notable changes to this project are documented here.

## [2.0.0] — 2026-09-23

Default branch: `main`. The previous Bash-based tool is on `v1`.

### Changed

- Rewrote `lookup` from a Bash script to a **Python 3.8+** program (standard library only).
- Windows now runs natively in Command Prompt or PowerShell. **WSL / Ubuntu is no longer required.**
- Install docs are split by OS around Python, not curl/bash/`ab`.
- Agent instructions (`AGENTS.md` and editor rule files) tell agents how to run lookup on Windows as well as Linux/macOS.

### Added

- `lookup.cmd` — Windows launcher (`lookup https://example.com/` or `py -3 lookup https://example.com/`).
- Built-in load test (50 requests, 5 concurrent). Apache `ab` is no longer needed.
- Built-in HTTP header fetch and DNS/TCP/TLS/TTFB timing. `curl` is no longer required.
- Nameserver lookup via `host` or Windows `nslookup`.

### Removed (as required tools)

- Bash, `curl`, and `ab` are no longer required.
- Optional extras are only `mtr` (route analysis) and `host`/`nslookup` (nameservers).

### Unchanged

- Same command shape: `lookup <url>` from the project root.
- Same report folders: `log/lookup_log_<domain>_<timestamp>/`.
- Same PageSpeed / Lighthouse flow via `lib/pagespeed.py` and `.pagespeed_api_key`.
- API keys and `log/` are still gitignored.

## [1.0.0] — 2026-09-23

Initial public release (branch `v1`): Bash `lookup`, curl timing, optional `mtr`/`ab`, Cursor/Codex/Antigravity agent rules, and OS install notes that used WSL on Windows.
