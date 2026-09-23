#!/usr/bin/env python3
"""PageSpeed Insights (Lighthouse) analysis for url-analyzer."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

PSI_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"

# Google Core Web Vitals thresholds (ms unless noted)
THRESHOLDS = {
    "lcp": {"good": 2500, "poor": 4000},
    "fcp": {"good": 1800, "poor": 3000},
    "tbt": {"good": 200, "poor": 600},
    "cls": {"good": 0.1, "poor": 0.25},
    "ttfb": {"good": 800, "poor": 1800},
    "si": {"good": 3400, "poor": 5800},
    "tti": {"good": 3800, "poor": 7300},
}

LCP_CAUSE_AUDITS = {
    "server-response-time": "Slow server/TTFB delays HTML — origin or cache miss",
    "render-blocking-resources": "Render-blocking CSS/JS delays LCP element paint",
    "largest-contentful-paint-element": "LCP element identified — check its load priority",
    "prioritize-lcp-image": "LCP image not prioritized (fetchpriority/preload missing)",
    "lcp-lazy-loaded": "LCP image is lazy-loaded — should load immediately",
    "uses-optimized-images": "LCP or hero images need compression",
    "modern-image-formats": "Serve WebP/AVIF instead of JPEG/PNG for LCP image",
    "uses-responsive-images": "Oversized images — LCP image larger than display size",
    "offscreen-images": "Below-fold images competing for bandwidth before LCP",
    "unused-javascript": "Heavy JS blocks main thread before LCP paints",
    "bootup-time": "JavaScript boot time delays rendering",
    "mainthread-work-breakdown": "Main-thread busy — layout/paint delayed",
    "uses-rel-preload": "Critical resources (fonts/LCP image) not preloaded",
    "font-display": "Web fonts block text/LCP render",
    "third-party-summary": "Third-party scripts delay LCP",
    "redirects": "Redirects add latency before content loads",
    "uses-text-compression": "HTML/JS/CSS not gzip/brotli compressed",
    "dom-size": "Large DOM slows style calculation and render",
    "efficient-animated-content": "Large GIF/video hurting LCP",
    "unsized-images": "Images without width/height cause layout work",
}

GENERAL_SPEED_AUDITS = {
    "unused-css-rules": "Remove unused CSS to reduce parse time",
    "unminified-css": "Minify CSS",
    "unminified-javascript": "Minify JavaScript",
    "legacy-javascript": "Serve modern JS to supported browsers",
    "duplicated-javascript": "Duplicate JS modules loaded",
    "total-byte-weight": "Page payload too large",
    "uses-long-cache-ttl": "Static assets lack long cache headers",
    "network-rtt": "High network round-trip time",
    "network-server-latency": "High server latency on network path",
    "long-tasks": "Long main-thread tasks hurt interactivity",
    "third-party-facades": "Consider facades for heavy embeds",
    "critical-request-chains": "Long critical request chains delay render",
}


def load_api_key() -> tuple[str | None, str]:
    """Return (key, source) where source is env, file path, or empty."""
    key = os.environ.get("PAGESPEED_API_KEY", "").strip()
    if key:
        return key, "PAGESPEED_API_KEY environment variable"
    for path in (
        Path.cwd() / ".pagespeed_api_key",
        Path(__file__).resolve().parent.parent / ".pagespeed_api_key",
    ):
        if path.is_file():
            return path.read_text().strip(), str(path.resolve())
    return None, ""


def load_api_key_simple() -> str | None:
    key, _ = load_api_key()
    return key


def rating(value: float | None, metric: str) -> str:
    if value is None:
        return "UNKNOWN"
    t = THRESHOLDS[metric]
    if metric == "cls":
        if value <= t["good"]:
            return "GOOD"
        if value <= t["poor"]:
            return "NEEDS IMPROVEMENT"
        return "POOR"
    if value <= t["good"]:
        return "GOOD"
    if value <= t["poor"]:
        return "NEEDS IMPROVEMENT"
    return "POOR"


def fmt_ms(ms: float | None) -> str:
    if ms is None:
        return "n/a"
    if ms >= 1000:
        return f"{ms / 1000:.1f}s"
    return f"{ms:.0f}ms"


def fetch_psi(url: str, strategy: str, api_key: str | None) -> dict[str, Any]:
    params = {
        "url": url,
        "strategy": strategy,
        "category": "performance",
    }
    if api_key:
        params["key"] = api_key
    query = urllib.parse.urlencode(params)
    req = urllib.request.Request(f"{PSI_URL}?{query}")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def audit_value(audits: dict, key: str) -> tuple[float | None, str | None]:
    audit = audits.get(key) or {}
    return audit.get("numericValue"), audit.get("displayValue")


def collect_opportunities(audits: dict) -> list[dict[str, Any]]:
    items = []
    for audit_id, audit in audits.items():
        details = audit.get("details") or {}
        if details.get("type") != "opportunity":
            continue
        score = audit.get("score")
        if score is None or score >= 1:
            continue
        items.append(
            {
                "id": audit_id,
                "title": audit.get("title", audit_id),
                "savings": audit.get("displayValue", ""),
                "score": score,
            }
        )
    items.sort(key=lambda x: x["score"])
    return items


def collect_failed_diagnostics(audits: dict, audit_map: dict) -> list[str]:
    causes = []
    for audit_id, explanation in audit_map.items():
        audit = audits.get(audit_id) or {}
        score = audit.get("score")
        if score is None:
            continue
        if score < 1:
            detail = audit.get("displayValue", "")
            line = f"{explanation}"
            if detail:
                line += f" ({detail})"
            causes.append(line)
    return causes


def crux_summary(data: dict) -> list[str]:
    lines = []
    for label, block_key in (
        ("Page (field data)", "loadingExperience"),
        ("Origin (field data)", "originLoadingExperience"),
    ):
        block = data.get(block_key) or {}
        metrics = block.get("metrics") or {}
        if not metrics:
            continue
        lines.append(f"  {label}:")
        mapping = {
            "LARGEST_CONTENTFUL_PAINT_MS": "LCP",
            "FIRST_CONTENTFUL_PAINT_MS": "FCP",
            "CUMULATIVE_LAYOUT_SHIFT_SCORE": "CLS",
            "INTERACTION_TO_NEXT_PAINT": "INP",
            "EXPERIMENTAL_TIME_TO_FIRST_BYTE": "TTFB",
        }
        for key, short in mapping.items():
            m = metrics.get(key)
            if not m:
                continue
            cat = m.get("category", "?")
            pct = m.get("percentile")
            if key == "CUMULATIVE_LAYOUT_SHIFT_SCORE" and pct is not None:
                lines.append(f"    {short}: {pct / 100:.3f} [{cat}] (p75 real users)")
            elif pct is not None:
                lines.append(f"    {short}: {fmt_ms(pct)} [{cat}] (p75 real users)")
    return lines


def analyze_strategy(data: dict, strategy: str) -> dict[str, Any]:
    lr = data.get("lighthouseResult") or {}
    audits = lr.get("audits") or {}
    perf = (lr.get("categories") or {}).get("performance") or {}
    score = perf.get("score")
    perf_score = round(score * 100) if score is not None else None

    lcp, lcp_disp = audit_value(audits, "largest-contentful-paint")
    fcp, fcp_disp = audit_value(audits, "first-contentful-paint")
    tbt, tbt_disp = audit_value(audits, "total-blocking-time")
    cls, cls_disp = audit_value(audits, "cumulative-layout-shift")
    si, si_disp = audit_value(audits, "speed-index")
    ttfb, ttfb_disp = audit_value(audits, "server-response-time")
    tti, tti_disp = audit_value(audits, "interactive")

    flags: list[tuple[str, str]] = []
    report: list[str] = []

    strat_label = strategy.upper()
    report.append(f"--- {strat_label} Lighthouse (PageSpeed Insights) ---")
    if perf_score is not None:
        speed_label = "FAST" if perf_score >= 90 else "AVERAGE" if perf_score >= 50 else "SLOW"
        report.append(f"Performance Score: {perf_score}/100 [{speed_label}]")
        if perf_score < 50:
            flags.append(("WARN", f"{strat_label} performance score {perf_score}/100 — site is slow"))
        elif perf_score < 90:
            flags.append(("INFO", f"{strat_label} performance score {perf_score}/100 — room to improve"))

    report.append("")
    report.append("Core Web Vitals (lab):")
    vitals = [
        ("LCP", lcp, lcp_disp, "lcp"),
        ("FCP", fcp, fcp_disp, "fcp"),
        ("TBT", tbt, tbt_disp, "tbt"),
        ("CLS", cls, cls_disp, "cls"),
        ("TTFB", ttfb, ttfb_disp, "ttfb"),
        ("Speed Index", si, si_disp, "si"),
        ("TTI", tti, tti_disp, "tti"),
    ]
    for name, num, disp, key in vitals:
        r = rating(num, key)
        display = disp or (fmt_ms(num) if key != "cls" else f"{num:.3f}" if num is not None else "n/a")
        report.append(f"  {name}: {display} [{r}]")
        if r == "POOR":
            flags.append(("WARN", f"{strat_label} {name} is POOR — {display}"))
        elif r == "NEEDS IMPROVEMENT":
            flags.append(("INFO", f"{strat_label} {name} needs improvement — {display}"))

    crux = crux_summary(data)
    if crux:
        report.append("")
        report.append("Chrome UX Report (real users):")
        report.extend(crux)

    lcp_causes = collect_failed_diagnostics(audits, LCP_CAUSE_AUDITS)
    general_causes = collect_failed_diagnostics(audits, GENERAL_SPEED_AUDITS)
    opportunities = collect_opportunities(audits)

    if lcp and lcp > THRESHOLDS["lcp"]["good"]:
        report.append("")
        report.append("Likely reasons for slow / poor LCP:")
        if lcp_causes:
            for i, cause in enumerate(lcp_causes[:12], 1):
                report.append(f"  {i}. {cause}")
                flags.append(("WARN", f"LCP cause: {cause}"))
        else:
            report.append("  No specific LCP audit failures — check network, TTFB, and LCP element type in log")
            flags.append(("INFO", "Poor LCP but no single dominant Lighthouse audit — check TTFB and caching"))

    other_causes = [c for c in general_causes if c not in lcp_causes]
    if other_causes or opportunities:
        report.append("")
        report.append("Other speed opportunities:")
        for i, cause in enumerate(other_causes[:8], 1):
            report.append(f"  {i}. {cause}")
        for opp in opportunities[:10]:
            report.append(f"  • {opp['title']}: {opp['savings']}")
            if opp["score"] < 0.5:
                flags.append(("WARN", f"Fix: {opp['title']} — est. savings {opp['savings']}"))

    lcp_el = audits.get("largest-contentful-paint-element") or {}
    lcp_detail = (lcp_el.get("details") or {}).get("items") or []
    if lcp_detail:
        report.append("")
        report.append("LCP element:")
        item = lcp_detail[0] if lcp_detail else {}
        for k in ("node", "url", "size", "loadTime", "renderTime"):
            if item.get(k):
                report.append(f"  {k}: {item[k]}")

    return {
        "strategy": strategy,
        "perf_score": perf_score,
        "lcp_ms": lcp,
        "ttfb_ms": ttfb,
        "flags": flags,
        "report": report,
        "raw": data,
    }


def parse_api_error(body: str) -> tuple[str, str, list[str]]:
    try:
        err = json.loads(body).get("error", {})
    except json.JSONDecodeError:
        return body[:200], "UNKNOWN", []

    message = err.get("message", "Unknown error")
    reason = ""
    for detail in err.get("details") or []:
        if detail.get("@type", "").endswith("ErrorInfo"):
            reason = detail.get("reason", reason)

    hints: list[str] = []
    if reason == "API_KEY_INVALID" or "expired" in message.lower():
        hints = [
            "Google says 'expired' but usually means the key is invalid or misconfigured:",
            "  1. Enable PageSpeed Insights API on the SAME project as this key:",
            "     https://console.cloud.google.com/apis/library/pagespeedonline.googleapis.com",
            "  2. API restrictions: set to 'Don't restrict key' OR allow 'PageSpeed Insights API'",
            "     https://console.cloud.google.com/apis/credentials",
            "  3. Application restrictions: use 'None' for server/CLI use (not HTTP referrers)",
            "  4. If you clicked 'Regenerate key', the old key is dead — create a NEW key",
            "  5. Copy the new key into .pagespeed_api_key (no spaces/newlines)",
            "  Test: python3 lib/pagespeed.py --test-key",
        ]
    elif "quota" in message.lower() or reason == "RATE_LIMIT_EXCEEDED":
        hints = [
            "Quota exceeded — wait and retry, or use a dedicated API key from your own GCP project.",
        ]

    return message, reason, hints


def test_api_key(api_key: str, source: str) -> int:
    print("Testing PageSpeed API key...")
    print(f"  Source: {source}")
    print(f"  Key prefix: {api_key[:8]}...{api_key[-4:]} (length {len(api_key)})")
    try:
        data = fetch_psi("https://example.com", "mobile", api_key)
        score = (
            (data.get("lighthouseResult") or {})
            .get("categories", {})
            .get("performance", {})
            .get("score")
        )
        print(f"  OK — key works. Example.com performance score: {round(score * 100) if score else 'n/a'}")
        return 0
    except urllib.error.HTTPError as exc:
        body = exc.read().decode()
        message, reason, hints = parse_api_error(body)
        print(f"  FAILED — {message}")
        if reason:
            print(f"  Reason: {reason}")
        for hint in hints:
            print(hint)
        return 1
    except urllib.error.URLError as exc:
        print(f"  Network error: {exc.reason}")
        return 1


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: pagespeed.py <url> [run_dir]", file=sys.stderr)
        print("       pagespeed.py --test-key", file=sys.stderr)
        return 1

    if sys.argv[1] == "--test-key":
        api_key, source = load_api_key()
        if not api_key:
            print("No API key found in PAGESPEED_API_KEY or .pagespeed_api_key")
            return 2
        return test_api_key(api_key, source)

    url = sys.argv[1]
    run_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    api_key, _ = load_api_key()

    if not api_key:
        msg = (
            "PageSpeed API key not set — add PAGESPEED_API_KEY env var or .pagespeed_api_key file\n"
            "  1. https://console.cloud.google.com/apis/library/pagespeedonline.googleapis.com\n"
            "  2. Create API key at https://console.cloud.google.com/apis/credentials\n"
            "  3. echo 'YOUR_KEY' > .pagespeed_api_key"
        )
        print(msg)
        print("FLAG|ERROR|PageSpeed API key missing — Lighthouse audit skipped", file=sys.stderr)
        return 2

    all_flags: list[tuple[str, str]] = []
    full_report: list[str] = ["=== Lighthouse / PageSpeed Analysis ===", ""]

    for strategy in ("mobile", "desktop"):
        try:
            print(f"Running PageSpeed ({strategy})...", file=sys.stderr)
            data = fetch_psi(url, strategy, api_key)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode()
            message, reason, hints = parse_api_error(body)
            print(f"PageSpeed API error ({strategy}): {message}")
            if reason:
                print(f"  Reason: {reason}")
            if hints and strategy == "mobile":
                print("")
                for hint in hints:
                    print(hint)
            flag_msg = f"PageSpeed API failed ({strategy}): {message}"
            if reason == "API_KEY_INVALID":
                flag_msg = "PageSpeed API key rejected (API_KEY_INVALID) — see hints above"
            print(f"FLAG|ERROR|{flag_msg}", file=sys.stderr)
            continue
        except urllib.error.URLError as exc:
            print(f"PageSpeed network error ({strategy}): {exc.reason}")
            print(f"FLAG|ERROR|PageSpeed network error: {exc.reason}", file=sys.stderr)
            continue

        if run_dir:
            run_dir.mkdir(parents=True, exist_ok=True)
            out = run_dir / f"pagespeed_{strategy}.json"
            out.write_text(json.dumps(data, indent=2))
            print(f"JSON|{out.resolve()}", file=sys.stderr)

        result = analyze_strategy(data, strategy)
        all_flags.extend(result["flags"])
        full_report.extend(result["report"])
        full_report.append("")

    if len(full_report) <= 2:
        return 2

    print("\n".join(full_report))

    seen = set()
    for level, msg in all_flags:
        key = (level, msg)
        if key in seen:
            continue
        seen.add(key)
        print(f"FLAG|{level}|{msg}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
