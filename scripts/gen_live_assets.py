#!/usr/bin/env python3
"""
Build the README art that changes on its own: rebuilt every 30 minutes by
.github/workflows/live.yml and force-pushed to the orphan `live` branch, so the
refreshes never pile up in the history of the main branch.

    live-sky.svg              New Delhi right now: sky colour, sun or moon on
                              its real arc, live weather (rain, cloud, haze),
                              lit windows at night, and what I'm probably doing
    live-terminal-{t}.svg     a terminal that types out live numbers: Codeforces,
                              LeetCode, GitHub, my latest commit
    live-rating-{t}.svg       Codeforces rating history, drawing itself over
                              the rank bands
    live-pulse-{t}.svg        the last 60 days of contributions as an equalizer
    live-ticker-{t}.svg       my latest commit messages scrolling past
    data.json                 the last good value of every source

Every source is optional. If one is down, its last good value is read back
from data.json (the workflow checks out the previous `live` branch first), so
a flaky API never blanks a card.

Usage:  python scripts/gen_live_assets.py [--out DIR] [--prev DIR]
Env:    GITHUB_TOKEN (needed for the contribution calendar), GH_USER
Standard library only, like the other generators.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
import os
import random
import urllib.request
from pathlib import Path

USER = os.environ.get("GH_USER", "dhanoliya-ji")
CF_HANDLE = "G.Dhanoliya"
LC_HANDLE = "dhanoliya"
# Repos whose commits are bot noise rather than work.
SKIP_REPOS = {USER}

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
NOW = dt.datetime.now(IST)

NEON = ["#22d3ee", "#8b5cf6", "#f472b6", "#c3f53c"]
NEON_LIGHT = ["#0891b2", "#7c3aed", "#db2777", "#65a30d"]
FONT = "'Segoe UI', SF Pro Display, Helvetica Neue, Arial, sans-serif"
MONO = "'JetBrains Mono', SFMono-Regular, Consolas, 'Liberation Mono', monospace"


class Theme:
    def __init__(self, dark: bool):
        self.dark = dark
        self.suffix = "dark" if dark else "light"
        self.neon = NEON if dark else NEON_LIGHT
        self.ink = "#e6edf3" if dark else "#0f172a"
        self.muted = "#7d8590" if dark else "#64748b"
        self.panel = "#0d1117" if dark else "#ffffff"
        self.panel2 = "#161b22" if dark else "#f6f8fa"
        self.line = "#30363d" if dark else "#d0d7de"


def svg(w: int, h: int, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" fill="none" role="img">{body}</svg>\n'
    )


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def clip(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


# ─────────────────────────────────────────────────────────────────────────────
# Fetching. Each fetcher returns a dict or raises; main() handles fallback.
# ─────────────────────────────────────────────────────────────────────────────
def get_json(url: str, data: dict | None = None, headers: dict | None = None):
    h = {"User-Agent": f"{USER}-profile-readme", "Accept": "application/json"}
    h.update(headers or {})
    body = None
    if data is not None:
        body = json.dumps(data).encode()
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=h)
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.load(r)


def gh_headers() -> dict:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    return {"Authorization": f"Bearer {tok}"} if tok else {}


def fetch_codeforces() -> dict:
    info = get_json(f"https://codeforces.com/api/user.info?handles={CF_HANDLE}")["result"][0]
    hist = get_json(f"https://codeforces.com/api/user.rating?handle={CF_HANDLE}")["result"]
    return {
        "rating": info.get("rating", 0),
        "max": info.get("maxRating", 0),
        "rank": info.get("rank", "unrated"),
        "max_rank": info.get("maxRank", "unrated"),
        "history": [[h["ratingUpdateTimeSeconds"], h["newRating"]] for h in hist],
    }


def fetch_leetcode() -> dict:
    q = (
        "query($u:String!){matchedUser(username:$u){submitStatsGlobal{acSubmissionNum"
        "{difficulty count}}} userContestRanking(username:$u){rating attendedContestsCount}}"
    )
    d = get_json(
        "https://leetcode.com/graphql",
        {"query": q, "variables": {"u": LC_HANDLE}},
        {"Referer": "https://leetcode.com"},
    )["data"]
    ac = {x["difficulty"]: x["count"] for x in d["matchedUser"]["submitStatsGlobal"]["acSubmissionNum"]}
    cr = d.get("userContestRanking") or {}
    return {
        "all": ac.get("All", 0), "easy": ac.get("Easy", 0),
        "medium": ac.get("Medium", 0), "hard": ac.get("Hard", 0),
        "contest": round(cr.get("rating") or 0),
    }


def fetch_github() -> dict:
    q = (
        "query($u:String!){user(login:$u){followers{totalCount} "
        "repositories(ownerAffiliations:OWNER,privacy:PUBLIC,first:100){totalCount "
        "nodes{stargazerCount}} contributionsCollection{contributionCalendar"
        "{totalContributions weeks{contributionDays{date contributionCount}}}}}}"
    )
    u = get_json("https://api.github.com/graphql",
                 {"query": q, "variables": {"u": USER}}, gh_headers())["data"]["user"]
    cal = u["contributionsCollection"]["contributionCalendar"]
    days = [[d["date"], d["contributionCount"]] for w in cal["weeks"] for d in w["contributionDays"]]
    return {
        "followers": u["followers"]["totalCount"],
        "repos": u["repositories"]["totalCount"],
        "stars": sum(n["stargazerCount"] for n in u["repositories"]["nodes"]),
        "year_total": cal["totalContributions"],
        "days": days[-60:],
    }


def fetch_commits() -> dict:
    repos = get_json(
        f"https://api.github.com/users/{USER}/repos?sort=pushed&per_page=12&type=owner",
        headers=gh_headers(),
    )
    out = []
    for r in [r for r in repos if not r["fork"] and r["name"] not in SKIP_REPOS][:5]:
        try:
            cs = get_json(
                f"https://api.github.com/repos/{USER}/{r['name']}/commits?per_page=3",
                headers=gh_headers(),
            )
        except Exception:
            continue
        for c in cs:
            msg = c["commit"]["message"].splitlines()[0]
            if msg.lower().startswith("merge"):
                continue
            out.append([r["name"], msg, c["commit"]["committer"]["date"]])
    out.sort(key=lambda x: x[2], reverse=True)
    if not out:
        raise RuntimeError("no commits found")
    return {"commits": out[:8]}


def fetch_weather() -> dict:
    d = get_json(
        "https://api.open-meteo.com/v1/forecast?latitude=28.61&longitude=77.21"
        "&current=temperature_2m,weather_code,cloud_cover,is_day"
        "&daily=sunrise,sunset&timezone=Asia%2FKolkata&forecast_days=1"
    )
    c = d["current"]
    return {
        "temp": c["temperature_2m"], "code": c["weather_code"],
        "cloud": c["cloud_cover"],
        "sunrise": d["daily"]["sunrise"][0][-5:], "sunset": d["daily"]["sunset"][0][-5:],
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1. New Delhi, right now
# ─────────────────────────────────────────────────────────────────────────────
WEATHER_WORDS = {
    0: "clear", 1: "mostly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "fog", 51: "drizzle", 53: "drizzle", 55: "drizzle",
    61: "rain", 63: "rain", 65: "heavy rain", 80: "showers", 81: "showers",
    82: "heavy showers", 95: "thunderstorm", 96: "thunderstorm", 99: "thunderstorm",
}


def hhmm_to_h(s: str, default: float) -> float:
    try:
        h, m = s.split(":")
        return int(h) + int(m) / 60
    except Exception:
        return default


def doing(h: float) -> str:
    if h < 1.5:
        return "probably still debugging something"
    if h < 7:
        return "asleep (the servers aren't)"
    if h < 9.5:
        return "chai, then code review"
    if h < 13:
        return "deep work: backend & systems"
    if h < 14.5:
        return "lunch, then a Codeforces problem"
    if h < 18:
        return "shipping features"
    if h < 20.5:
        return "contest time on Codeforces / CodeChef"
    return "side projects and reading other people's code"


def lerp_hex(a: str, b: str, t: float) -> str:
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def sky_palette(h: float, rise: float, set_: float) -> tuple[str, str, str]:
    """(top, bottom, skyline) colours for this moment."""
    night = ("#060914", "#141a3a", "#05070f")
    dawn = ("#3b3f8f", "#f59e9e", "#1b1530")
    day = ("#3b82f6", "#bfe3ff", "#1e293b")
    dusk = ("#2a1a5e", "#fb923c", "#160f26")
    def mix(p, q, t):
        return tuple(lerp_hex(x, y, max(0.0, min(1.0, t))) for x, y in zip(p, q))
    if h < rise - 1 or h > set_ + 1:
        return night
    if h < rise:
        return mix(night, dawn, h - (rise - 1))
    if h < rise + 1.5:
        return mix(dawn, day, (h - rise) / 1.5)
    if h < set_ - 1.5:
        return day
    if h < set_:
        return mix(day, dusk, (h - (set_ - 1.5)) / 1.5)
    return mix(dusk, night, h - set_)


def skyline(W: int, base: int) -> str:
    """A loose New Delhi silhouette: India Gate, Qutub Minar, Lotus Temple, blocks."""
    p = []
    # Generic blocks first, so the landmarks sit in front of them.
    rnd = random.Random(7)
    x = 0
    while x < W:
        w = rnd.randint(28, 70)
        h = rnd.randint(18, 64)
        p.append(f"M{x},{base}V{base - h}H{x + w}V{base}Z")
        x += w + rnd.randint(0, 6)
    # Qutub Minar around x=820: a tapering tower with balconies.
    q = 820
    p.append(f"M{q - 13},{base}L{q - 6},{base - 150}H{q + 6}L{q + 13},{base}Z")
    for k in range(4):
        y = base - 30 - k * 32
        hw = 15 - k * 2
        p.append(f"M{q - hw},{y}H{q + hw}V{y - 4}H{q - hw}Z")
    p.append(f"M{q - 3},{base - 150}V{base - 160}H{q + 3}V{base - 150}Z")
    # Lotus Temple around x=1040: overlapping petals.
    lt = 1040
    for k, (dx, hgt) in enumerate(((-34, 36), (-17, 50), (0, 58), (17, 50), (34, 36))):
        p.append(
            f"M{lt + dx - 20},{base}Q{lt + dx - 10},{base - hgt} {lt + dx},{base - hgt - 4}"
            f"Q{lt + dx + 10},{base - hgt} {lt + dx + 20},{base}Z"
        )
    return "".join(p)


def india_gate(base: int, g: int = 300) -> str:
    """India Gate, drawn even-odd so the arch is a real opening."""
    return (
        f"M{g - 46},{base}V{base - 70}H{g + 46}V{base}Z"
        f"M{g - 16},{base}V{base - 40}Q{g},{base - 62} {g + 16},{base - 40}V{base}Z"
        f"M{g - 52},{base - 70}H{g + 52}V{base - 80}H{g - 52}Z"
        f"M{g - 30},{base - 80}H{g + 30}L{g + 18},{base - 92}H{g - 18}Z"
    )


def sky_svg(weather: dict | None) -> str:
    W, H = 1200, 230
    base = 200
    h = NOW.hour + NOW.minute / 60
    rise = hhmm_to_h((weather or {}).get("sunrise", ""), 6.2)
    set_ = hhmm_to_h((weather or {}).get("sunset", ""), 18.1)
    top, bottom, city = sky_palette(h, rise, set_)
    is_day = rise <= h <= set_
    code = (weather or {}).get("code", 0)
    cloud = (weather or {}).get("cloud", 15)
    rainy = code in (51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99)
    foggy = code in (45, 48)
    if rainy or foggy or code == 3:
        grey = 0.65 if rainy else 0.45
        top, bottom = lerp_hex(top, "#475569", grey), lerp_hex(bottom, "#94a3b8", grey)

    parts = [
        "<defs>"
        f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{top}"/>'
        f'<stop offset="1" stop-color="{bottom}"/></linearGradient>'
        '<radialGradient id="glow"><stop offset="0" stop-color="#fff7d6" stop-opacity="0.9"/>'
        '<stop offset="0.35" stop-color="#ffd27a" stop-opacity="0.35"/>'
        '<stop offset="1" stop-color="#ffd27a" stop-opacity="0"/></radialGradient>'
        '<radialGradient id="mglow"><stop offset="0" stop-color="#e2e8f0" stop-opacity="0.55"/>'
        '<stop offset="1" stop-color="#e2e8f0" stop-opacity="0"/></radialGradient>'
        f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="14"/></clipPath>'
        "</defs>"
        '<g clip-path="url(#frame)">'
        f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'
    ]

    # Stars, only when the sun is down; each twinkles on its own clock.
    if not is_day:
        rnd = random.Random(42)
        for i in range(90):
            x, y = rnd.uniform(0, W), rnd.uniform(0, base - 60)
            r_ = rnd.choice((0.6, 0.8, 1.0, 1.4))
            d = rnd.uniform(2.0, 6.0)
            parts.append(
                f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r_}" fill="#fff">'
                f'<animate attributeName="opacity" values="0.15;1;0.15" dur="{d:.1f}s" '
                f'begin="{rnd.uniform(0, 4):.1f}s" repeatCount="indefinite"/></circle>'
            )
        # A shooting star every so often.
        parts.append(
            '<line x1="0" y1="0" x2="70" y2="18" stroke="#fff" stroke-width="1.6" '
            'stroke-linecap="round" opacity="0">'
            '<animateTransform attributeName="transform" type="translate" '
            'values="150 10;650 140" dur="1.3s" begin="2s;9s;17s" fill="freeze"/>'
            '<animate attributeName="opacity" values="0;1;0" dur="1.3s" begin="2s;9s;17s"/></line>'
        )

    # Sun or moon, placed on its real arc for this minute.
    if is_day:
        t = (h - rise) / max(0.1, set_ - rise)
        body_fill, glow, rad = "#fff3b0", "url(#glow)", 26
    else:
        night_len = 24 - (set_ - rise)
        t = ((h - set_) % 24) / night_len
        body_fill, glow, rad = "#e5e7eb", "url(#mglow)", 20
    cx = 80 + t * (W - 160)
    cy = base - 40 - math.sin(t * math.pi) * 120
    parts.append(
        f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{rad * 3.4:.0f}" fill="{glow}">'
        f'<animate attributeName="r" values="{rad * 3.2:.0f};{rad * 3.8:.0f};{rad * 3.2:.0f}" '
        'dur="5s" repeatCount="indefinite"/></circle>'
        f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{rad}" fill="{body_fill}"/>'
    )
    if not is_day:  # crescent: bite out of the moon with the sky colour
        parts.append(
            f'<circle cx="{cx + 8:.0f}" cy="{cy - 5:.0f}" r="{rad - 2}" fill="{top}" opacity="0.92"/>'
        )

    # Clouds, as many as the live cloud cover says, drifting at different speeds.
    n_clouds = max(1, round(cloud / 14))
    rnd = random.Random(3)
    cloud_fill = "#ffffff" if is_day else "#8b93b8"
    cloud_op = 0.85 if is_day else 0.25
    for i in range(n_clouds):
        y = rnd.uniform(18, base - 110)
        s = rnd.uniform(0.6, 1.3)
        dur = rnd.uniform(60, 120)
        start = rnd.uniform(-300, W)
        parts.append(
            f'<g opacity="{cloud_op}"><g>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="{start:.0f} {y:.0f};{W + 200:.0f} {y:.0f}" dur="{dur * (W + 200 - start) / (W + 500):.0f}s" '
            'fill="freeze"/>'
            f'<g transform="scale({s:.2f})" fill="{cloud_fill}">'
            '<ellipse cx="0" cy="12" rx="46" ry="14"/><ellipse cx="-18" cy="4" rx="22" ry="16"/>'
            '<ellipse cx="14" cy="0" rx="26" ry="20"/></g></g></g>'
        )
        # A second copy enters from the left, so the sky never empties.
        parts.append(
            f'<g opacity="{cloud_op}"><g transform="translate(-200 {y:.0f})">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="-200 {y:.0f};{W + 200} {y:.0f}" dur="{dur:.0f}s" '
            f'begin="{dur * (W + 200 - start) / (W + 500):.0f}s" repeatCount="indefinite"/>'
            f'<g transform="scale({s:.2f})" fill="{cloud_fill}">'
            '<ellipse cx="0" cy="12" rx="46" ry="14"/><ellipse cx="-18" cy="4" rx="22" ry="16"/>'
            '<ellipse cx="14" cy="0" rx="26" ry="20"/></g></g></g>'
        )

    # Birds in the daytime.
    if is_day and not rainy:
        for i in range(3):
            y0 = 50 + i * 16
            parts.append(
                f'<path d="M0,0 q6,-6 12,0 q6,-6 12,0" stroke="{city}" stroke-width="1.6" fill="none">'
                f'<animateTransform attributeName="transform" type="translate" '
                f'values="-40 {y0};{W + 40} {y0 - 30}" dur="{26 + i * 4}s" begin="{i * 1.2}s" '
                'repeatCount="indefinite"/></path>'
            )

    # The city.
    parts.append(f'<path d="{skyline(W, base)}" fill="{city}"/>')
    parts.append(f'<path d="{india_gate(base)}" fill="{city}" fill-rule="evenodd"/>')
    parts.append(f'<rect y="{base}" width="{W}" height="{H - base}" fill="{city}"/>')

    # Windows that flicker on at night.
    if not is_day:
        rnd = random.Random(11)
        for i in range(70):
            x = rnd.uniform(4, W - 8)
            y = rnd.uniform(base - 56, base - 8)
            parts.append(
                f'<rect x="{x:.0f}" y="{y:.0f}" width="3" height="4" fill="#fde68a">'
                f'<animate attributeName="opacity" values="{rnd.choice(("0;0.9;0.9;0", "0.9;0.9;0;0.9", "0.2;0.9;0.2"))}" '
                f'dur="{rnd.uniform(4, 12):.1f}s" repeatCount="indefinite"/></rect>'
            )

    # Rain, if it is actually raining in Delhi.
    if rainy:
        rnd = random.Random(5)
        for i in range(120):
            x = rnd.uniform(0, W + 60)
            d = rnd.uniform(0.6, 1.1)
            parts.append(
                f'<line x1="{x:.0f}" y1="-20" x2="{x - 8:.0f}" y2="0" stroke="#cbd5e1" '
                'stroke-width="1" opacity="0.55">'
                f'<animateTransform attributeName="transform" type="translate" '
                f'values="0 0;-40 {H + 20}" dur="{d:.2f}s" begin="{rnd.uniform(0, 1):.2f}s" '
                'repeatCount="indefinite"/></line>'
            )
        if code in (95, 96, 99):
            parts.append(
                f'<rect width="{W}" height="{H}" fill="#fff" opacity="0">'
                '<animate attributeName="opacity" values="0;0;0.55;0;0.35;0" '
                'keyTimes="0;0.9;0.92;0.94;0.96;1" dur="7s" repeatCount="indefinite"/></rect>'
            )

    # Haze or fog drifting across the skyline.
    if foggy or cloud > 85:
        parts.append(
            f'<rect x="-{W}" y="{base - 90}" width="{W * 3}" height="110" fill="#cbd5e1" opacity="0.18">'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;{W} 0" '
            'dur="40s" repeatCount="indefinite"/></rect>'
        )

    # Caption plate.
    weather_word = WEATHER_WORDS.get(code, "")
    temp = (weather or {}).get("temp")
    wx = f" · {temp:.0f}°C {weather_word}" if temp is not None else ""
    clock = NOW.strftime("%H:%M")
    line1 = f"{clock} IST · New Delhi{wx}"
    line2 = f"● {doing(h)}"
    pw = max(len(line1) * 10.4, len(line2) * 8.0) + 96
    parts.append(
        f'<rect x="20" y="16" width="{pw:.0f}" height="58" rx="10" fill="#000" opacity="0.34"/>'
        f'<text x="38" y="42" font-family="{MONO}" font-size="17" font-weight="700" fill="#f8fafc">'
        f'{clock} IST<tspan fill="#cbd5e1" font-weight="400"> · New Delhi{esc(wx)}</tspan></text>'
        f'<text x="38" y="63" font-family="{MONO}" font-size="13" fill="#e2e8f0">'
        f'<tspan fill="#c3f53c">●</tspan> {esc(doing(h))}</text>'
    )
    # The status dot blinks like a live indicator.
    parts.append(
        f'<circle cx="{20 + pw - 16:.0f}" cy="30" r="4" fill="#f43f5e">'
        '<animate attributeName="opacity" values="1;0.2;1" dur="1.4s" repeatCount="indefinite"/></circle>'
        f'<text x="{20 + pw - 26:.0f}" y="34" text-anchor="end" font-family="{MONO}" font-size="10" '
        'letter-spacing="2" fill="#fecdd3">LIVE</text>'
    )
    parts.append("</g>")
    return svg(W, H, "".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 2. Terminal that types out live numbers
# ─────────────────────────────────────────────────────────────────────────────
def ago(iso: str) -> str:
    try:
        t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    except Exception:
        return ""
    s = (dt.datetime.now(dt.timezone.utc) - t).total_seconds()
    for unit, n in (("d", 86400), ("h", 3600), ("m", 60)):
        if s >= n:
            return f"{int(s // n)}{unit} ago"
    return "just now"


def terminal_svg(theme: Theme, cf, lc, gh, commits) -> str:
    W = 900
    fs, adv = 15, 9.05        # monospace advance at 15px, a touch generous
    lh = 25
    x0, y0 = 26, 76
    lines: list[tuple[str, str, str]] = []  # (prompt, command, output)
    lines.append(("$", "whoami", "Gajendra Dhanoliya · backend & systems · IIT Delhi EE '26"))
    lines.append(("$", "date", NOW.strftime("%a %d %b %Y, %H:%M IST") + " · New Delhi"))
    if cf:
        lines.append(("$", f"cf --user {CF_HANDLE}",
                      f"rating {cf['rating']} ({cf['rank']}) · peak {cf['max']} ({cf['max_rank']}) · "
                      f"{len(cf['history'])} rated contests"))
    if lc:
        lines.append(("$", f"leetcode --user {LC_HANDLE}",
                      f"{lc['all']} solved · {lc['easy']} easy / {lc['medium']} medium / {lc['hard']} hard"
                      + (f" · contest {lc['contest']}" if lc.get("contest") else "")))
    if gh:
        lines.append(("$", "gh stats",
                      f"{gh['year_total']} contributions this year · {gh['repos']} public repos · "
                      f"{gh['stars']}★ · {gh['followers']} followers"))
    if commits:
        repo, msg, when = commits[0]
        lines.append(("$", "git log -1 --oneline", clip(f"[{repo}] {msg}", 78) + f" · {ago(when)}"))
    lines.append(("$", "echo $STATUS", "open to SDE & AI/ML roles · full-time or internship"))

    H = y0 + len(lines) * lh * 2 + 30
    cycle = 22.0                 # seconds for one full replay
    type_speed = 0.035           # seconds per character typed
    out_delay = 0.25

    parts = [
        "<defs>"
        f'<linearGradient id="bar" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{theme.neon[0]}"/><stop offset="0.5" stop-color="{theme.neon[1]}"/>'
        f'<stop offset="1" stop-color="{theme.neon[2]}"/></linearGradient>'
    ]
    # Each command gets a clip rect that widens one character at a time.
    t = 0.6
    timeline = []
    for i, (_, cmd, outp) in enumerate(lines):
        start = t
        end = start + len(cmd) * type_speed
        out_at = end + out_delay
        timeline.append((start, end, out_at))
        t = out_at + 0.55
    finish = t
    for i, ((_, cmd, _), (start, end, _)) in enumerate(zip(lines, timeline)):
        w = len(cmd) * adv + 4
        k1, k2 = start / cycle, end / cycle
        parts.append(
            f'<clipPath id="c{i}"><rect x="{x0 + 18}" y="{y0 + i * lh * 2 - 18}" width="0" height="24">'
            f'<animate attributeName="width" values="0;0;{w:.0f};{w:.0f};0" '
            f'keyTimes="0;{k1:.4f};{k2:.4f};0.985;1" dur="{cycle}s" repeatCount="indefinite"/>'
            "</rect></clipPath>"
        )
    parts.append("</defs>")

    # Window chrome.
    parts.append(
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{theme.panel}" '
        f'stroke="{theme.line}"/>'
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="38" rx="12" fill="{theme.panel2}"/>'
        f'<rect x="0.5" y="26" width="{W - 1}" height="13" fill="{theme.panel2}"/>'
        f'<line x1="0" y1="39" x2="{W}" y2="39" stroke="{theme.line}"/>'
        '<circle cx="22" cy="20" r="6" fill="#ff5f57"/><circle cx="42" cy="20" r="6" fill="#febc2e"/>'
        '<circle cx="62" cy="20" r="6" fill="#28c840"/>'
        f'<text x="{W / 2}" y="25" text-anchor="middle" font-family="{MONO}" font-size="12" '
        f'fill="{theme.muted}">gajendra@iitd: ~/live — zsh</text>'
        f'<rect x="0" y="38" width="{W}" height="2" fill="url(#bar)">'
        f'<animate attributeName="width" values="0;{W}" dur="{finish:.1f}s" fill="freeze"/></rect>'
    )

    for i, ((prompt, cmd, outp), (start, end, out_at)) in enumerate(zip(lines, timeline)):
        y = y0 + i * lh * 2
        parts.append(
            f'<text x="{x0}" y="{y}" font-family="{MONO}" font-size="{fs}" font-weight="700" '
            f'fill="{theme.neon[3 if theme.dark else 3]}">{prompt}</text>'
            f'<text x="{x0 + 18}" y="{y}" font-family="{MONO}" font-size="{fs}" fill="{theme.ink}" '
            f'clip-path="url(#c{i})">{esc(cmd)}</text>'
        )
        # The output fades in once the command is "entered".
        k = out_at / cycle
        parts.append(
            f'<text x="{x0 + 18}" y="{y + lh - 2}" font-family="{MONO}" font-size="{fs - 1}" '
            f'fill="{theme.neon[i % 3] if i else theme.muted}" opacity="0">{esc(outp)}'
            f'<animate attributeName="opacity" values="0;0;1;1;0" '
            f'keyTimes="0;{k:.4f};{min(k + 0.01, 0.98):.4f};0.985;1" dur="{cycle}s" '
            'repeatCount="indefinite"/></text>'
        )
        # A block cursor that rides the edge of the clip while typing.
        w = len(cmd) * adv
        k1, k2, k3 = start / cycle, end / cycle, out_at / cycle
        parts.append(
            f'<rect x="{x0 + 18}" y="{y - 14}" width="9" height="18" fill="{theme.neon[0]}" opacity="0">'
            f'<animate attributeName="x" values="{x0 + 18};{x0 + 18};{x0 + 18 + w:.0f};{x0 + 18 + w:.0f}" '
            f'keyTimes="0;{k1:.4f};{k2:.4f};1" dur="{cycle}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0.85;0.85;0;0" '
            f'keyTimes="0;{k1:.4f};{k3:.4f};{min(k3 + 0.001, 0.999):.4f};1" dur="{cycle}s" '
            'repeatCount="indefinite"/></rect>'
        )

    # Final prompt with a blinking cursor, shown after the last line.
    y = y0 + len(lines) * lh * 2
    kf = finish / cycle
    parts.append(
        f'<g opacity="0"><animate attributeName="opacity" values="0;0;1;1;0" '
        f'keyTimes="0;{kf:.4f};{min(kf + 0.005, 0.98):.4f};0.985;1" dur="{cycle}s" repeatCount="indefinite"/>'
        f'<text x="{x0}" y="{y}" font-family="{MONO}" font-size="{fs}" font-weight="700" '
        f'fill="{theme.neon[3]}">$</text>'
        f'<rect x="{x0 + 18}" y="{y - 14}" width="9" height="18" fill="{theme.neon[0]}">'
        '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1s" '
        'repeatCount="indefinite"/></rect></g>'
    )
    parts.append(
        f'<text x="{W - 20}" y="{H - 14}" text-anchor="end" font-family="{MONO}" font-size="11" '
        f'fill="{theme.muted}">refreshed {NOW.strftime("%H:%M IST")} · rebuilds every 30 min</text>'
    )
    return svg(W, H, "".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 3. Codeforces rating, drawing itself over the rank bands
# ─────────────────────────────────────────────────────────────────────────────
CF_BANDS = [  # (from, to, name, dark colour, light colour)
    (0, 1200, "newbie", "#808080", "#808080"),
    (1200, 1400, "pupil", "#22c55e", "#16a34a"),
    (1400, 1600, "specialist", "#03a89e", "#0f766e"),
    (1600, 1900, "expert", "#3b82f6", "#2563eb"),
    (1900, 2100, "candidate master", "#a855f7", "#9333ea"),
]


def rating_svg(theme: Theme, cf: dict) -> str:
    W, H = 900, 300
    L, R, T, B = 60, 30, 46, 40
    hist = cf["history"]
    if len(hist) < 2:
        hist = hist * 2 or [[0, 0], [1, 0]]
    ys = [v for _, v in hist]
    lo = max(0, min(ys) - 150)
    hi = max(ys) + 260
    t0, t1 = hist[0][0], hist[-1][0]

    def X(t):
        return L + (t - t0) / max(1, t1 - t0) * (W - L - R)

    def Y(v):
        return T + (1 - (v - lo) / (hi - lo)) * (H - T - B)

    parts = [
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{theme.panel}" stroke="{theme.line}"/>'
        f'<clipPath id="plot"><rect x="{L}" y="{T}" width="{W - L - R}" height="{H - T - B}"/></clipPath>'
    ]
    # Rank bands.
    parts.append('<g clip-path="url(#plot)">')
    for a, b, name, cd, cl in CF_BANDS:
        if b < lo or a > hi:
            continue
        y1, y2 = Y(min(b, hi)), Y(max(a, lo))
        c = cd if theme.dark else cl
        parts.append(
            f'<rect x="{L}" y="{y1:.1f}" width="{W - L - R}" height="{y2 - y1:.1f}" fill="{c}" '
            f'opacity="{0.10 if theme.dark else 0.08}"/>'
        )
        if y2 - y1 > 16:
            parts.append(
                f'<text x="{L + 10}" y="{y1 + 14:.1f}" font-family="{MONO}" '
                f'font-size="10" letter-spacing="2" fill="{c}" opacity="0.85">{name.upper()}</text>'
            )
    parts.append("</g>")
    # Y ticks.
    for v in range((lo // 200 + 1) * 200, hi, 200):
        parts.append(
            f'<line x1="{L}" y1="{Y(v):.1f}" x2="{W - R}" y2="{Y(v):.1f}" stroke="{theme.line}" '
            'stroke-dasharray="3 5"/>'
            f'<text x="{L - 10}" y="{Y(v) + 4:.1f}" text-anchor="end" font-family="{MONO}" '
            f'font-size="11" fill="{theme.muted}">{v}</text>'
        )

    pts = [(X(t), Y(v)) for t, v in hist]
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    length = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)) + 2
    cycle = 12
    area = d + f" L{pts[-1][0]:.1f},{H - B} L{pts[0][0]:.1f},{H - B} Z"
    parts.append(
        "<defs>"
        f'<linearGradient id="ln" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{theme.neon[1]}"/>'
        f'<stop offset="1" stop-color="{theme.neon[0]}"/></linearGradient>'
        f'<linearGradient id="ar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{theme.neon[0]}" '
        f'stop-opacity="0.28"/><stop offset="1" stop-color="{theme.neon[0]}" stop-opacity="0"/></linearGradient>'
        "</defs>"
        f'<path d="{area}" fill="url(#ar)" opacity="0">'
        f'<animate attributeName="opacity" values="0;0;1;1;0" keyTimes="0;0.25;0.45;0.95;1" '
        f'dur="{cycle}s" repeatCount="indefinite"/></path>'
        f'<path d="{d}" stroke="url(#ln)" stroke-width="2.6" stroke-linejoin="round" '
        f'stroke-linecap="round" stroke-dasharray="{length:.0f}" stroke-dashoffset="{length:.0f}">'
        f'<animate attributeName="stroke-dashoffset" values="{length:.0f};0;0;{length:.0f}" '
        f'keyTimes="0;0.4;0.95;1" dur="{cycle}s" repeatCount="indefinite"/></path>'
    )
    # Points pop in as the line reaches them.
    run = 0.0
    for i, (x, y) in enumerate(pts):
        if i:
            run += math.dist(pts[i - 1], pts[i])
        k = 0.4 * run / length
        parts.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="0" fill="{theme.panel}" stroke="{theme.neon[0]}" '
            f'stroke-width="2"><animate attributeName="r" values="0;0;3.6;3.6;0" '
            f'keyTimes="0;{k:.4f};{min(k + 0.02, 0.94):.4f};0.95;1" dur="{cycle}s" '
            'repeatCount="indefinite"/></circle>'
        )
    # Peak marker and the current point, pulsing.
    pi = max(range(len(hist)), key=lambda i: hist[i][1])
    px, py = pts[pi]
    parts.append(
        f'<text x="{px:.1f}" y="{py - 14:.1f}" text-anchor="middle" font-family="{MONO}" '
        f'font-size="12" font-weight="700" fill="{theme.neon[2]}">peak {hist[pi][1]}</text>'
    )
    lx, ly = pts[-1]
    parts.append(
        f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="5" fill="{theme.neon[2]}"/>'
        f'<circle cx="{lx:.1f}" cy="{ly:.1f}" r="5" fill="none" stroke="{theme.neon[2]}" stroke-width="2">'
        '<animate attributeName="r" values="5;18" dur="1.8s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0.9;0" dur="1.8s" repeatCount="indefinite"/></circle>'
    )
    # Header.
    parts.append(
        f'<text x="{L}" y="30" font-family="{FONT}" font-size="16" font-weight="700" fill="{theme.ink}">'
        f'Codeforces · {CF_HANDLE}</text>'
        f'<text x="{W - R}" y="30" text-anchor="end" font-family="{MONO}" font-size="12" fill="{theme.muted}">'
        f'now {cf["rating"]} · peak {cf["max"]} {cf["max_rank"]} · {len(cf["history"])} contests · '
        f'live {NOW.strftime("%d %b %H:%M")}</text>'
    )
    # Year labels along the bottom.
    seen = set()
    for t, _ in hist:
        yr = dt.datetime.fromtimestamp(t, IST).year
        if yr in seen:
            continue
        seen.add(yr)
        parts.append(
            f'<text x="{X(t):.1f}" y="{H - 16}" font-family="{MONO}" font-size="11" '
            f'fill="{theme.muted}">{yr}</text>'
        )
    return svg(W, H, "".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 4. Contribution pulse: last 60 days as an equalizer
# ─────────────────────────────────────────────────────────────────────────────
def pulse_svg(theme: Theme, gh: dict) -> str:
    W, H = 900, 200
    days = gh["days"]
    n = len(days)
    L, R, top, base = 30, 30, 50, 160
    bw = (W - L - R) / n
    peak = max([c for _, c in days] + [1])
    total = sum(c for _, c in days)
    active = sum(1 for _, c in days if c)
    best = max(days, key=lambda d: d[1]) if days else ["", 0]

    parts = [
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{theme.panel}" stroke="{theme.line}"/>'
        "<defs>"
        f'<linearGradient id="eq" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="{theme.neon[1]}"/>'
        f'<stop offset="0.6" stop-color="{theme.neon[0]}"/><stop offset="1" stop-color="{theme.neon[3]}"/>'
        "</linearGradient></defs>"
        f'<text x="{L}" y="32" font-family="{FONT}" font-size="16" font-weight="700" fill="{theme.ink}">'
        f"Last 60 days on GitHub</text>"
        f'<text x="{W - R}" y="32" text-anchor="end" font-family="{MONO}" font-size="12" fill="{theme.muted}">'
        f"{total} contributions · active {active}/{n} days · best {best[1]} on {best[0][5:]}</text>"
        f'<line x1="{L}" y1="{base + 0.5}" x2="{W - R}" y2="{base + 0.5}" stroke="{theme.line}"/>'
    ]
    for i, (date, c) in enumerate(days):
        h = 4 + (math.sqrt(c / peak) * (base - top - 6) if c else 0)
        x = L + i * bw + bw * 0.18
        w = bw * 0.64
        lo = h * 0.72
        delay = i * 0.03
        breathe = 2.2 + (i % 7) * 0.25
        fill = "url(#eq)" if c else theme.line
        parts.append(
            f'<rect x="{x:.1f}" y="{base - h:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{min(w / 2, 3):.1f}" fill="{fill}">'
            # Rise from the baseline on load, then breathe forever.
            f'<animate attributeName="height" values="0;{h:.1f}" dur="0.7s" begin="{delay:.2f}s" fill="freeze"/>'
            f'<animate attributeName="y" values="{base};{base - h:.1f}" dur="0.7s" begin="{delay:.2f}s" fill="freeze"/>'
            + (
                f'<animate attributeName="height" values="{h:.1f};{lo:.1f};{h:.1f}" dur="{breathe:.2f}s" '
                f'begin="{0.8 + delay:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="y" values="{base - h:.1f};{base - lo:.1f};{base - h:.1f}" '
                f'dur="{breathe:.2f}s" begin="{0.8 + delay:.2f}s" repeatCount="indefinite"/>'
                if c else ""
            )
            + "</rect>"
        )
    # A scan line sweeping across, like a heartbeat monitor.
    parts.append(
        f'<rect x="{L}" y="{top - 6}" width="2" height="{base - top + 6}" fill="{theme.neon[2]}" opacity="0.7">'
        f'<animate attributeName="x" values="{L};{W - R}" dur="5s" repeatCount="indefinite"/></rect>'
    )
    # Month ticks.
    for i, (date, _) in enumerate(days):
        if date.endswith("-01") or i == 0:
            parts.append(
                f'<text x="{L + i * bw:.1f}" y="{base + 22}" font-family="{MONO}" font-size="11" '
                f'fill="{theme.muted}">{dt.date.fromisoformat(date).strftime("%b %d")}</text>'
            )
    parts.append(
        f'<text x="{W - R}" y="{base + 22}" text-anchor="end" font-family="{MONO}" font-size="11" '
        f'fill="{theme.muted}">today</text>'
    )
    return svg(W, H, "".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 5. Ticker of latest commit messages
# ─────────────────────────────────────────────────────────────────────────────
def ticker_svg(theme: Theme, commits: list) -> str:
    W, H = 1200, 46
    items = [f"{repo}  ›  {clip(msg, 64)}  ·  {ago(when)}" for repo, msg, when in commits]
    gap = "      ◆      "
    text = gap.join(items) + gap
    width = len(text) * 8.0    # 13px mono advance, generous
    dur = max(20, width / 70)  # ~70 px/s
    parts = [
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="{theme.panel}" stroke="{theme.line}"/>'
        f'<clipPath id="tk"><rect x="150" y="0" width="{W - 160}" height="{H}"/></clipPath>'
        f'<rect x="0.5" y="0.5" width="140" height="{H - 1}" rx="10" fill="{theme.neon[1]}"/>'
        f'<rect x="120" y="0.5" width="21" height="{H - 1}" fill="{theme.neon[1]}"/>'
        f'<circle cx="20" cy="{H / 2}" r="4.5" fill="#fff">'
        '<animate attributeName="opacity" values="1;0.25;1" dur="1.2s" repeatCount="indefinite"/></circle>'
        f'<text x="32" y="{H / 2 + 4.5}" font-family="{MONO}" font-size="12.5" font-weight="700" '
        'letter-spacing="1.5" fill="#fff">LATEST PUSH</text>'
        '<g clip-path="url(#tk)"><g>'
        f'<animateTransform attributeName="transform" type="translate" values="0 0;-{width:.0f} 0" '
        f'dur="{dur:.0f}s" repeatCount="indefinite"/>'
    ]
    for k in range(2):  # two copies back to back = seamless loop
        parts.append(
            f'<text x="{160 + k * width:.0f}" y="{H / 2 + 4.5}" font-family="{MONO}" font-size="13" '
            f'fill="{theme.ink}" xml:space="preserve">{esc(text)}</text>'
        )
    parts.append("</g></g>")
    return svg(W, H, "".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="live-out")
    ap.add_argument("--prev", default=None, help="previous live branch checkout, for fallback data")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    prev = {}
    if args.prev and (Path(args.prev) / "data.json").exists():
        prev = json.loads((Path(args.prev) / "data.json").read_text(encoding="utf-8"))

    data, status = {}, []
    for key, fn in (("cf", fetch_codeforces), ("lc", fetch_leetcode), ("gh", fetch_github),
                    ("commits", fetch_commits), ("weather", fetch_weather)):
        try:
            data[key] = fn()
            status.append(f"{key}: live")
        except Exception as e:  # noqa: BLE001 -- any failure falls back
            data[key] = prev.get(key)
            status.append(f"{key}: {'cached' if data[key] else 'missing'} ({type(e).__name__})")
    data["generated"] = NOW.isoformat(timespec="minutes")

    (out / "live-sky.svg").write_text(sky_svg(data["weather"]), encoding="utf-8")
    commits = (data["commits"] or {}).get("commits", [])
    for dark in (True, False):
        t = Theme(dark)
        (out / f"live-terminal-{t.suffix}.svg").write_text(
            terminal_svg(t, data["cf"], data["lc"], data["gh"], commits), encoding="utf-8")
        if data["cf"]:
            (out / f"live-rating-{t.suffix}.svg").write_text(rating_svg(t, data["cf"]), encoding="utf-8")
        if data["gh"]:
            (out / f"live-pulse-{t.suffix}.svg").write_text(pulse_svg(t, data["gh"]), encoding="utf-8")
        if commits:
            (out / f"live-ticker-{t.suffix}.svg").write_text(ticker_svg(t, commits), encoding="utf-8")
    (out / "data.json").write_text(json.dumps(data, indent=1), encoding="utf-8")
    print("\n".join(status))


if __name__ == "__main__":
    main()
