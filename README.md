# url-analyzer

A command-line tool that checks a website’s **speed, caching, and Core Web Vitals**. It fetches HTTP headers, measures network timing, runs Google PageSpeed Insights (Lighthouse) for mobile and desktop, and writes a dated report you (or an AI agent) can read.

You do not need to read the source to use it. Clone, add an API key, run `./lookup <url>`.

## What you get

One command produces:

- A terminal summary: Lighthouse scores, Core Web Vitals, and speed flags
- A run folder: `log/lookup_log_<domain>_<timestamp>/`
  - `lookup_log_<domain>_<timestamp>.log` — full report (headers, timing, flags, load test)
  - `pagespeed_mobile.json` — Lighthouse mobile (LCP breakdown, audits)
  - `pagespeed_desktop.json` — Lighthouse desktop

Typical flags cover cache HIT/MISS, TTFB, compression, Cloudflare/LiteSpeed, render-blocking resources, and LCP causes.

## Requirements

No Node, pip, or Composer packages. `lib/pagespeed.py` uses Python’s standard library only.

| Tool | Required? | Why | Debian/Ubuntu package |
| --- | --- | --- | --- |
| `bash` | Yes | Runs `./lookup` | (already installed) |
| `curl` | Yes | Headers and timing | `curl` |
| `python3` | Yes | PageSpeed / Lighthouse | `python3` |
| Google PageSpeed API key | Yes for Lighthouse | See [API key](#api-key) | — |
| `host` | Optional | Nameserver lookup | `dnsutils` or `bind9-dnsutils` |
| `mtr` | Optional | Route / packet-loss check | `mtr-tiny` |
| `ab` | Optional | Light origin load test | `apache2-utils` |

If an optional tool is missing, lookup still runs and marks that section as skipped.

### Install packages

**Required** (do this first):

```bash
# Debian / Ubuntu
sudo apt update
sudo apt install -y curl python3

# Fedora / RHEL
sudo dnf install -y curl python3

# macOS (Homebrew)
brew install curl python3
```

**Optional** (nameservers, route, load test):

```bash
# Debian / Ubuntu
sudo apt install -y dnsutils mtr-tiny apache2-utils

# Fedora / RHEL
sudo dnf install -y bind-utils mtr httpd-tools

# macOS (Homebrew) — `ab` comes from httpd; `host` comes from bind
brew install bind mtr httpd
```

On newer Ubuntu, if `dnsutils` is not found, use `bind9-dnsutils` instead.

**Everything on Debian/Ubuntu in one line:**

```bash
sudo apt update && sudo apt install -y curl python3 dnsutils mtr-tiny apache2-utils
```

Check what you have:

```bash
command -v bash curl python3 host mtr ab
```

`curl` and `python3` must print a path. The others can be missing.

## Setup

```bash
git clone https://github.com/getneerajk/url-analyzer.git
cd url-analyzer
chmod +x lookup lib/pagespeed.py
```

### API key

Lighthouse data comes from the [PageSpeed Insights API](https://developers.google.com/speed/docs/insights/v5/get-started). Without a key, lookup still checks headers and timing, but skips Lighthouse.

1. Enable the API: [PageSpeed Insights API](https://console.cloud.google.com/apis/library/pagespeedonline.googleapis.com)
2. Create an API key: [Credentials](https://console.cloud.google.com/apis/credentials)
3. For CLI use, set **Application restrictions** to **None** (not HTTP referrers).
4. Under API restrictions, allow **PageSpeed Insights API** or leave unrestricted.

Put the key in **one** of these places (never commit the real key):

```bash
# Option A — project file (gitignored)
cp .pagespeed_api_key.example .pagespeed_api_key
# edit .pagespeed_api_key and paste the key on one line, no quotes

# Option B — environment variable
export PAGESPEED_API_KEY='your-key-here'
```

Test the key:

```bash
python3 lib/pagespeed.py --test-key
```

If Google says the key is invalid or “expired”, the usual causes are: the API is not enabled on the **same** GCP project as the key, the key is restricted to HTTP referrers, or you regenerated the key and the old one is dead.

## Usage

From the project root:

```bash
./lookup https://example.com/
```

A domain without a scheme is treated as HTTPS:

```bash
./lookup example.com
```

A run can take 30–90 seconds because PageSpeed runs twice (mobile, then desktop). When it finishes, the terminal prints scores and flags, then:

```text
Data saved to: ./log/lookup_log_example_com_20260923_103000/
```

## Reading a report

Start with the terminal output, then open the `.log` file in that run folder.

| Section | What it tells you |
| --- | --- |
| Lighthouse scores | Mobile/desktop performance 0–100 |
| Core Web Vitals | LCP, FCP, TBT, CLS, TTFB, Speed Index, TTI |
| Chrome UX Report | Real-user (field) data when Google has enough traffic |
| Speed flags | Cache, TTFB, compression, LCP causes |
| curl timing | DNS, TCP, TLS, TTFB from **your** machine |
| mtr | Loss / latency on the path to the origin |
| ab | How the origin behaves under a small concurrent load |
| Raw headers | Cache-Control, LiteSpeed, Cloudflare, HSTS, etc. |

For LCP detail (element, image URL, opportunities), open `pagespeed_mobile.json` or `pagespeed_desktop.json` in the same folder. Those files are large; search for `largest-contentful-paint` or `audits`.

Do not reuse an old `log/` folder unless you mean to compare history. Each run is timestamped.

## Use with AI agents

Ask in plain language, for example: `run lookup for https://example.com` or `why is mobile LCP slow on example.com?`

The agent should **run** `./lookup` and analyze **that** run. It should not search old logs or read the source first.

Instruction files are already in the repo so common agents pick this up without scanning the project:

| Tool | File it reads |
| --- | --- |
| Cursor | `.cursor/rules/lookup-workflow.mdc` and `AGENTS.md` |
| OpenAI Codex | `AGENTS.md` |
| Google Antigravity | `.agents/rules/lookup-workflow.md`, `GEMINI.md`, `AGENTS.md` |
| Gemini CLI | `GEMINI.md` |
| Claude Code | `CLAUDE.md` (imports `AGENTS.md`) |
| GitHub Copilot | `.github/copilot-instructions.md` and `AGENTS.md` |
| Other agents that support [AGENTS.md](https://agents.md) | `AGENTS.md` |

`AGENTS.md` is the shared source. You do not need to copy rules into your editor settings.

## What is not in this repository

These stay on your machine (see `.gitignore`):

- `.pagespeed_api_key` — your Google API key
- `log/` — reports and PageSpeed JSON (often include client URLs)
- `snippets/` — local notes or site-specific patches
- `.env` and other credential files

The committed example key file is only a placeholder: `.pagespeed_api_key.example`.

## Project layout

```text
lookup                 # main script
lib/pagespeed.py       # PageSpeed Insights helper
.pagespeed_api_key.example
AGENTS.md              # shared agent instructions
```

You only need those files to run lookups. Everything else is optional editor wiring.
