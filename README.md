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

Follow **one** of the install guides below, then add an [API key](#api-key).

## How to install

`./lookup` is a Bash script. Use a real Unix shell: Linux terminal, macOS Terminal, or **Windows Subsystem for Linux (WSL)**. It will not run in PowerShell or `cmd.exe`.

---

### Linux / Ubuntu

These commands are for Ubuntu and Debian. Fedora/RHEL notes are at the end of this section.

1. Open a terminal.

2. Install Git (needed to clone the repo):

   ```bash
   sudo apt update
   sudo apt install -y git
   ```

3. Install **required** packages:

   ```bash
   sudo apt install -y curl python3
   ```

4. Install **optional** packages (recommended for a full report):

   ```bash
   sudo apt install -y dnsutils mtr-tiny apache2-utils
   ```

   On newer Ubuntu, if `dnsutils` is not found:

   ```bash
   sudo apt install -y bind9-dnsutils mtr-tiny apache2-utils
   ```

   What those packages provide: `host` (nameservers), `mtr` (route / packet loss), `ab` (small load test).

5. Confirm the required tools exist. Each of `bash`, `curl`, and `python3` must print a path:

   ```bash
   command -v bash curl python3 host mtr ab
   ```

6. Clone the repo and make the scripts executable:

   ```bash
   git clone https://github.com/getneerajk/url-analyzer.git
   cd url-analyzer
   chmod +x lookup lib/pagespeed.py
   ```

7. Continue at [API key](#api-key).

**One-line package install (Ubuntu/Debian):**

```bash
sudo apt update && sudo apt install -y git curl python3 dnsutils mtr-tiny apache2-utils
```

**Fedora / RHEL:**

```bash
sudo dnf install -y git curl python3
sudo dnf install -y bind-utils mtr httpd-tools   # optional: host, mtr, ab
```

Then clone as in step 6.

---

### macOS

Use Terminal (or iTerm). Homebrew is the easiest way to get the optional tools.

1. Open **Terminal**.

2. Install Apple’s command-line tools if you do not have them yet (needed for Git and compilers):

   ```bash
   xcode-select --install
   ```

   Click **Install** in the dialog and wait until it finishes.

3. Install [Homebrew](https://brew.sh) if `brew` is not already available:

   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

   On Apple Silicon (M1/M2/M3/M4), add Homebrew to your PATH if the installer says to:

   ```bash
   echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
   eval "$(/opt/homebrew/bin/brew shellenv)"
   ```

4. Install **required** packages. macOS often already has `curl` and `python3`; this ensures they are present:

   ```bash
   brew install curl python3
   ```

5. Install **optional** packages (recommended):

   ```bash
   brew install bind mtr httpd
   ```

   - `bind` provides `host`
   - `mtr` provides `mtr` (you may be asked for your password when it runs)
   - `httpd` provides `ab`

6. Confirm the required tools exist. Each of `bash`, `curl`, and `python3` must print a path:

   ```bash
   command -v bash curl python3 host mtr ab
   ```

   If `ab` is not found after installing `httpd`, try:

   ```bash
   brew link httpd
   command -v ab
   ```

7. Clone the repo and make the scripts executable:

   ```bash
   git clone https://github.com/getneerajk/url-analyzer.git
   cd url-analyzer
   chmod +x lookup lib/pagespeed.py
   ```

8. Continue at [API key](#api-key).

---

### Windows

Do **not** run `./lookup` in PowerShell or Command Prompt. Install **WSL** with Ubuntu, then follow the Linux steps inside that Ubuntu terminal.

1. Open **PowerShell as Administrator** (right-click Start → Windows Terminal / PowerShell → Run as administrator).

2. Install WSL and Ubuntu:

   ```powershell
   wsl --install -d Ubuntu
   ```

   If WSL is already installed and you only need Ubuntu:

   ```powershell
   wsl --install -d Ubuntu
   wsl -l -v
   ```

3. Restart the PC if Windows asks you to.

4. Open **Ubuntu** from the Start menu. The first launch asks you to create a Linux username and password. This password is for `sudo` inside Ubuntu; it is not your Windows password.

5. Update Ubuntu and install Git plus **required** packages:

   ```bash
   sudo apt update
   sudo apt install -y git curl python3
   ```

6. Install **optional** packages (recommended):

   ```bash
   sudo apt install -y dnsutils mtr-tiny apache2-utils
   ```

   If `dnsutils` is not found:

   ```bash
   sudo apt install -y bind9-dnsutils mtr-tiny apache2-utils
   ```

7. Confirm the required tools exist. Each of `bash`, `curl`, and `python3` must print a path:

   ```bash
   command -v bash curl python3 host mtr ab
   ```

8. Clone the repo **inside WSL** (paths like `/home/you/...`, not `C:\...`):

   ```bash
   git clone https://github.com/getneerajk/url-analyzer.git
   cd url-analyzer
   chmod +x lookup lib/pagespeed.py
   ```

   If you already cloned the folder in Windows Explorer, you can open it from WSL with:

   ```bash
   cd /mnt/c/Users/YOUR_WINDOWS_USERNAME/path/to/url-analyzer
   chmod +x lookup lib/pagespeed.py
   ```

   A clone inside the Linux home directory is faster and avoids Windows/Linux line-ending issues.

9. Continue at [API key](#api-key). Run those commands in the **same Ubuntu/WSL terminal**.

**Git Bash** (from Git for Windows) can run `./lookup` with `curl` and `python3`, but `mtr` is usually unavailable and some path/line-ending issues show up. WSL is the supported Windows setup.

## API key

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
