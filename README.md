# url-analyzer

**Version 2** on [`main`](https://github.com/getneerajk/url-analyzer/tree/main). What changed is in [CHANGELOG.md](CHANGELOG.md). The original Bash release is on [`v1`](https://github.com/getneerajk/url-analyzer/tree/v1).

A command-line tool that checks a website’s **speed, caching, and Core Web Vitals**. It fetches HTTP headers, measures network timing, runs Google PageSpeed Insights (Lighthouse) for mobile and desktop, and writes a dated report you (or an AI agent) can read.

You do not need to read the source to use it. Install Python 3, clone, add an API key, run `lookup` (or `./lookup` on Linux/macOS).

## What you get

One command produces:

- A terminal summary: Lighthouse scores, Core Web Vitals, and speed flags
- A run folder: `log/lookup_log_<domain>_<timestamp>/`
  - `lookup_log_<domain>_<timestamp>.log` — full report (headers, timing, flags, load test)
  - `pagespeed_mobile.json` — Lighthouse mobile (LCP breakdown, audits)
  - `pagespeed_desktop.json` — Lighthouse desktop

Typical flags cover cache HIT/MISS, TTFB, compression, Cloudflare/LiteSpeed, render-blocking resources, and LCP causes.

## Requirements

`lookup` is a **Python 3** program (3.8 or newer). It uses only the standard library — no pip, Node, or Composer packages.

| Tool | Required? | Why |
| --- | --- | --- |
| Python 3.8+ | Yes | Runs `lookup` and PageSpeed analysis |
| Git | Yes to clone | Download the repo |
| Google PageSpeed API key | Yes for Lighthouse | See [API key](#api-key) |
| `nslookup` or `host` | Optional | Nameserver lookup (Windows includes `nslookup`) |
| `mtr` | Optional | Route / packet-loss check |

Headers, timing, load test, and Lighthouse all run in Python. If `mtr` is missing, that section is skipped.

Follow **one** of the install guides below, then add an [API key](#api-key).

## How to install

---

### Linux / Ubuntu

1. Open a terminal.

2. Install Git and Python 3:

   ```bash
   sudo apt update
   sudo apt install -y git python3
   ```

   Fedora / RHEL:

   ```bash
   sudo dnf install -y git python3
   ```

3. Optional — route analysis:

   ```bash
   sudo apt install -y mtr-tiny
   ```

4. Confirm Python works:

   ```bash
   python3 --version
   ```

   You need 3.8 or newer.

5. Clone the repo:

   ```bash
   git clone https://github.com/getneerajk/url-analyzer.git
   cd url-analyzer
   chmod +x lookup
   ```

6. Continue at [API key](#api-key).

---

### macOS

1. Open **Terminal**.

2. Install Apple’s command-line tools if Git is missing:

   ```bash
   xcode-select --install
   ```

   Click **Install** and wait until it finishes.

3. Check Python:

   ```bash
   python3 --version
   ```

   If that fails or the version is older than 3.8, install Python from [python.org](https://www.python.org/downloads/) or Homebrew:

   ```bash
   brew install python3
   ```

   (Install [Homebrew](https://brew.sh) first if you do not have `brew`.)

4. Optional — route analysis:

   ```bash
   brew install mtr
   ```

5. Clone the repo:

   ```bash
   git clone https://github.com/getneerajk/url-analyzer.git
   cd url-analyzer
   chmod +x lookup
   ```

6. Continue at [API key](#api-key).

---

### Windows

You do **not** need Ubuntu or WSL. Install Python, then run `lookup` in Command Prompt or PowerShell.

1. Install **Python 3.8+** from [https://www.python.org/downloads/](https://www.python.org/downloads/).

   On the first installer screen, check **Add python.exe to PATH**, then click **Install Now**.

2. Install **Git** from [https://git-scm.com/download/win](https://git-scm.com/download/win) if you do not have it. Default options are fine.

3. Close and reopen Command Prompt or PowerShell so PATH updates apply.

4. Confirm Python:

   ```powershell
   py -3 --version
   ```

   If `py` is not found, try `python --version`. You need 3.8 or newer.

5. Clone the repo:

   ```powershell
   git clone https://github.com/getneerajk/url-analyzer.git
   cd url-analyzer
   ```

6. Continue at [API key](#api-key). On Windows, copy the key file with:

   ```powershell
   copy .pagespeed_api_key.example .pagespeed_api_key
   notepad .pagespeed_api_key
   ```

   Paste the key on one line, save, and close Notepad.

`mtr` is uncommon on Windows. Lookup still runs; the route section is skipped.

## API key

Lighthouse data comes from the [PageSpeed Insights API](https://developers.google.com/speed/docs/insights/v5/get-started). Without a key, lookup still checks headers and timing, but skips Lighthouse.

1. Enable the API: [PageSpeed Insights API](https://console.cloud.google.com/apis/library/pagespeedonline.googleapis.com)
2. Create an API key: [Credentials](https://console.cloud.google.com/apis/credentials)
3. For CLI use, set **Application restrictions** to **None** (not HTTP referrers).
4. Under API restrictions, allow **PageSpeed Insights API** or leave unrestricted.

Put the key in **one** of these places (never commit the real key):

**Linux / macOS:**

```bash
# Option A — project file (gitignored)
cp .pagespeed_api_key.example .pagespeed_api_key
# edit .pagespeed_api_key and paste the key on one line, no quotes

# Option B — environment variable
export PAGESPEED_API_KEY='your-key-here'
```

**Windows (PowerShell):**

```powershell
copy .pagespeed_api_key.example .pagespeed_api_key
notepad .pagespeed_api_key
# or: $env:PAGESPEED_API_KEY='your-key-here'
```

Test the key:

```bash
python3 lib/pagespeed.py --test-key
```

On Windows:

```powershell
py -3 lib/pagespeed.py --test-key
```

If Google says the key is invalid or “expired”, the usual causes are: the API is not enabled on the **same** GCP project as the key, the key is restricted to HTTP referrers, or you regenerated the key and the old one is dead.

## Usage

From the project root.

**Linux / macOS:**

```bash
./lookup https://example.com/
```

**Windows (Command Prompt or PowerShell):**

```powershell
lookup https://example.com/
```

If that fails, call Python directly:

```powershell
py -3 lookup https://example.com/
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
| Network timing | DNS, TCP, TLS, TTFB from **your** machine |
| mtr | Loss / latency on the path to the origin (skipped if `mtr` is not installed) |
| Load test | How the origin behaves under a small concurrent load (built in; no `ab`) |
| Raw headers | Cache-Control, LiteSpeed, Cloudflare, HSTS, etc. |

For LCP detail (element, image URL, opportunities), open `pagespeed_mobile.json` or `pagespeed_desktop.json` in the same folder. Those files are large; search for `largest-contentful-paint` or `audits`.

Do not reuse an old `log/` folder unless you mean to compare history. Each run is timestamped.

## Use with AI agents

Ask in plain language, for example: `run lookup for https://example.com` or `why is mobile LCP slow on example.com?`

The agent should **run** `./lookup <url>` on Linux/macOS, or `lookup <url>` / `py -3 lookup <url>` on Windows, then analyze **that** run. It should not search old logs or read the source first.

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
lookup                 # main program (Python)
lookup.cmd             # Windows launcher
lib/pagespeed.py       # PageSpeed Insights helper
.pagespeed_api_key.example
AGENTS.md              # shared agent instructions
```

You only need those files to run lookups. Everything else is optional editor wiring.
