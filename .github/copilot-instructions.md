# GitHub Copilot instructions

This repository is a **CLI URL analyzer**. You already have enough context in this file and in `AGENTS.md`.

**Do not** explore or read `lookup`, `lib/pagespeed.py`, or the rest of the tree to “understand the project.” Only open source files if the user asks you to change the tool itself.

Never print, commit, or upload `.pagespeed_api_key`, environment secrets, or files under `log/`.

## Lookup workflow

When the user asks to **run lookup**, **analyze a URL**, **check a site**, or similar:

1. **Run** lookup from the project root (do not skip this step):
   - Linux/macOS: `./lookup <url>`
   - Windows: `lookup <url>` or `py -3 lookup <url>`
   If `./lookup` is not executable, use `python3 lookup <url>`.
2. **Analyze the fresh output** from that run — terminal summary, files under `log/lookup_log_<domain>_<timestamp>/`, including the `.log` file and PageSpeed JSON.
3. **Do not** substitute prior logs, grep stale `log/pagespeed_*.json` files, or infer results without running lookup unless the user explicitly says to use existing data.

## What lookup produces

- Terminal: Lighthouse scores, Core Web Vitals, speed flags, run directory path
- `log/lookup_log_<domain>_<timestamp>/` — all artifacts for the run:
  - `lookup_log_<domain>_<timestamp>.log` — full report
  - `pagespeed_mobile.json` and `pagespeed_desktop.json` — LCP breakdown, audits, deep dives

## Analysis expectations

After the run completes, report findings the user cares about (performance, LCP, TTFB, caching, flags, fixes) based on **that run's data**, not older artifacts.

## Examples

User: "run lookup for https://example.com"  
→ `./lookup https://example.com/` then analyze output.

User: "why is mobile LCP slow on example.com?"  
→ `./lookup https://example.com/` then explain LCP from the new PageSpeed JSON and log.
