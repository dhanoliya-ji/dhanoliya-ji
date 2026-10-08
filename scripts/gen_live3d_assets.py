#!/usr/bin/env python3
"""
Live 3D pieces that loop forever and are rebuilt from real data every 30
minutes by .github/workflows/live.yml, next to the cards from
gen_live_assets.py:

    live-globe-{t}.svg     a dot-matrix Earth spinning in 3D, lit by the real
                           sun at build time, with New Delhi and the ISS
                           marked where they actually are
    live-galaxy-{t}.svg    a replay of the last 30 days of commits: every repo
                           is a planet on a tilted 3D orbit, every commit lands
                           as a burst on its planet while a timeline, a date, a
                           counter and the commit message play along
    live-helix-{t}.svg     the last 182 days of contributions wound into a
                           rotating double helix

GitHub strips <script>, and a README cannot autoplay video, so all of this is
SMIL that a browser loops forever. The trick that keeps the files small: a
point turning about an axis moves in simple harmonic motion, and SMIL's spline
interpolation with a sine-shaped bezier reproduces that from just three
values. A whole meridian of the globe shares one horizontal scale, so the
Earth is ~70 animated groups rather than thousands of animated dots.

Usage:  python scripts/gen_live3d_assets.py [--out DIR] [--prev DIR]
Env:    GITHUB_TOKEN, GH_USER. Standard library only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import math
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_live_assets import (  # noqa: E402  -- shared fetch helpers and palette
    IST, MONO, FONT, USER, SKIP_REPOS, Theme, get_json, gh_headers, svg, clip,
)

UTC_NOW = dt.datetime.now(dt.timezone.utc)
# A zero-length round-capped stroke that ignores scaling: a dot that stays round
# while its meridian is squeezed horizontally.
DOT = 'stroke-linecap="round" vector-effect="non-scaling-stroke"'
SINE = 'calcMode="spline" keyTimes="0;0.5;1" keySplines="0.37 0 0.63 1;0.37 0 0.63 1"'

LANG_COLOURS = {  # kept for future use
    "Python": "#3572A5", "Jupyter Notebook": "#DA5B0B", "C++": "#f34b7d", "C": "#8a8a8a",
    "C#": "#178600", "JavaScript": "#f1e05a", "TypeScript": "#3178c6", "HTML": "#e34c26",
    "CSS": "#663399", "Go": "#00ADD8", "Rust": "#dea584", "Java": "#b07219",
}


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def shm(attr: str, lo: float, hi: float, period: float, phase: float) -> str:
    """Animate `attr` as lo + (hi-lo)·(1-cos(2πt/T + phase))/2, i.e. a sine wave.

    The three-value spline starts at `lo`; a negative begin shifts it so the
    wave sits at the requested phase at t=0.
    """
    offset = (phase / (2 * math.pi)) % 1 * period
    return (
        f'<animate attributeName="{attr}" values="{lo:.1f};{hi:.1f};{lo:.1f}" dur="{period}s" '
        f'begin="-{offset:.2f}s" repeatCount="indefinite" {SINE}/>'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Data
# ─────────────────────────────────────────────────────────────────────────────
def fetch_iss() -> dict:
    d = get_json("https://api.wheretheiss.at/v1/satellites/25544")
    return {"lat": d["latitude"], "lon": d["longitude"], "alt": round(d["altitude"])}


def fetch_calendar() -> dict:
    q = ("query($u:String!){user(login:$u){contributionsCollection{contributionCalendar"
         "{weeks{contributionDays{date contributionCount}}}}}}")
    u = get_json("https://api.github.com/graphql", {"query": q, "variables": {"u": USER}},
                 gh_headers())["data"]["user"]
    weeks = u["contributionsCollection"]["contributionCalendar"]["weeks"]
    days = [[d["date"], d["contributionCount"]] for w in weeks for d in w["contributionDays"]]
    return {"days": days[-182:]}


def fetch_replay() -> dict:
    """Commits from the last 30 days (widened if the month was quiet), per repo."""
    repos = get_json(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner",
                     headers=gh_headers())
    repos = [r for r in repos if not r["fork"] and r["name"] not in SKIP_REPOS]
    for days in (30, 90, 365):
        since = (UTC_NOW - dt.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        commits, langs = [], {}
        for r in repos:
            if r["pushed_at"] < since:
                continue
            try:
                cs = get_json(f"https://api.github.com/repos/{USER}/{r['name']}/commits"
                              f"?since={since}&per_page=100", headers=gh_headers())
            except Exception:
                continue
            for c in cs:
                msg = c["commit"]["message"].splitlines()[0]
                commits.append([r["name"], msg, c["commit"]["committer"]["date"]])
            if cs:
                langs[r["name"]] = r.get("language") or "Other"
        if len(commits) >= 5:
            commits.sort(key=lambda x: x[2])
            return {"days": days, "since": since, "commits": commits, "langs": langs}
    raise RuntimeError("no commits in the last year")


# ─────────────────────────────────────────────────────────────────────────────
# 1. The globe
# ─────────────────────────────────────────────────────────────────────────────
# Coarse coastlines as (lon, lat) polygons -- enough for a dot-matrix Earth.
LAND = [
    # North America
    [(-168, 65), (-162, 70), (-156, 71.5), (-140, 70), (-128, 70), (-115, 68), (-95, 72), (-82, 73),
     (-78, 68), (-64, 60), (-56, 52), (-66, 45), (-70, 42), (-76, 38), (-76, 35), (-81, 31), (-80, 25.5),
     (-82, 29), (-89, 30), (-97, 27), (-97, 22), (-92, 18.5), (-87, 21), (-88, 16), (-83, 15), (-83, 10),
     (-79, 9), (-77, 8), (-80, 7.5), (-85, 10), (-92, 14.5), (-96, 16), (-105, 20), (-110, 24), (-112, 30),
     (-117, 32.5), (-121, 35), (-124, 40), (-124, 46), (-127, 50), (-133, 55), (-140, 60), (-150, 61),
     (-158, 58), (-165, 61)],
    # Greenland, Iceland
    [(-73, 78), (-60, 82), (-30, 83), (-20, 80), (-18, 75), (-22, 70), (-40, 65), (-44, 60), (-50, 63),
     (-55, 68), (-60, 75)],
    [(-24, 64), (-14, 64.5), (-14, 66), (-22, 66.5)],
    # South America
    [(-80, 9), (-75, 11), (-62, 10.5), (-52, 5), (-50, 0), (-44, -2), (-35, -5), (-35, -9), (-39, -15),
     (-41, -22), (-48, -26), (-53, -34), (-58, -38), (-62, -40), (-65, -45), (-68, -50), (-69, -55),
     (-73, -53), (-75, -47), (-73, -40), (-71.5, -30), (-70, -18), (-76, -14), (-81, -6), (-80, -1),
     (-78, 2), (-77, 7)],
    # Europe, Britain, Ireland
    [(-10, 36), (-9, 43), (-2, 43.5), (-5, 48), (-2, 49.5), (2, 51), (5, 53), (8, 54), (8, 57), (11, 58),
     (5, 59), (5, 62), (10, 64), (15, 68), (20, 70), (28, 71), (32, 69), (30, 65), (25, 65), (22, 61),
     (23, 60), (28, 60), (30, 58), (30, 50), (40, 47), (38, 45), (41, 41.5), (36, 41), (29, 41), (26, 40.5),
     (24, 38), (22, 37), (20, 40), (19, 42), (16, 43), (13, 45.5), (12, 44), (16, 41), (18, 40), (16, 38),
     (12, 38), (10, 44), (7, 43.5), (3, 43), (3, 41.5), (0, 39), (-2, 37), (-6, 36)],
    [(-6, 50), (1.5, 51), (1.7, 52.8), (0, 53.5), (-2, 56), (-2, 57.6), (-3, 58.6), (-5, 58.6), (-6, 57),
     (-5, 55), (-3, 54.5), (-4.5, 53.4), (-5, 52)],
    [(-10, 51.5), (-6, 52), (-6, 54.5), (-8, 55.3), (-10, 54)],
    # Africa, Madagascar
    [(-17, 21), (-17, 15), (-15, 11), (-8, 4.5), (-2, 5), (5, 6), (9, 4), (9, 1), (12, -5), (13, -12),
     (12, -17), (15, -27), (18, -34.5), (20, -35), (26, -34), (32, -29), (35, -24), (35, -20), (40, -16),
     (40, -10), (39, -5), (42, 0), (46, 3), (51, 11.5), (44, 11), (43, 13), (39, 17), (37, 22), (35, 28),
     (33, 31), (30, 31.5), (25, 32), (20, 32), (15, 32.5), (10, 34), (11, 37), (8, 37), (0, 36), (-6, 36),
     (-10, 30), (-13, 27)],
    [(44, -25), (47, -25), (50, -15), (49, -12), (44, -17)],
    # Asia, with Arabia and India
    [(26, 40.5), (29, 41), (36, 41), (41, 41.5), (38, 45), (40, 47), (30, 50), (30, 58), (28, 60), (30, 65),
     (32, 69), (40, 67), (44, 68), (55, 69), (65, 69), (70, 73), (80, 73), (90, 76), (100, 78), (110, 77),
     (120, 73), (130, 71), (140, 72), (150, 71), (160, 70), (170, 70), (180, 69), (180, 65), (178, 62),
     (170, 60), (163, 58), (160, 54), (156, 51), (156, 57), (150, 59), (143, 59), (140, 55), (141, 52),
     (140, 48), (135, 43), (130, 42), (129, 35), (126, 35), (126, 38), (125, 40), (121, 40), (118, 38),
     (122, 37), (120, 34), (122, 30), (120, 26), (117, 23), (110, 21), (108, 21), (106, 18), (109, 13),
     (109, 11), (105, 9), (103, 10), (101, 13), (100, 10), (98, 8), (100, 4), (103, 1.5), (104, 1.3),
     (102, 4), (103, 6), (101, 7), (99, 10), (98.5, 14), (97, 17), (94, 16), (94, 19), (92, 21), (90, 22),
     (87, 21.5), (85, 20), (80, 15), (80, 10), (77, 8), (76, 10), (74, 15), (73, 20), (70, 21),
     (68, 23.5), (66, 25), (62, 25), (57, 25.5), (56, 27), (50, 30), (48, 30), (48, 29.5), (50, 26),
     (51, 24.5), (56, 26), (59, 22), (55, 17), (52, 16), (45, 13), (43, 13), (39, 17), (37, 22), (35, 28),
     (34.5, 29.5), (35, 32), (35.5, 34), (36, 36.5), (32, 36.5), (28, 37)],
    [(80, 6), (81.8, 7), (81, 9.5), (80, 9.7), (79.8, 7)],
    # Japan, South-East Asia, Australia, New Zealand
    [(130, 31), (132, 34), (135, 34), (140, 35), (141, 38), (142, 40), (141.5, 42), (145, 43.5),
     (142, 45.5), (140, 42), (139.5, 40), (139, 38), (136, 36.5), (133, 35.5), (130, 33.5)],
    [(95, 5.5), (98, 4), (104, -2), (106, -6), (102, -4)],
    [(109, 1), (110, -3), (116, -4), (119, 1), (117, 7), (113, 3)],
    [(105, -6), (114, -7.7), (114, -8.7), (106, -7.5)],
    [(131, -1), (138, -2), (145, -4), (150, -10), (142, -9), (138, -8)],
    [(120, 18), (122, 18), (126, 7), (125, 6), (122, 7), (120, 13)],
    [(114, -22), (114, -26), (115, -34), (118, -35), (124, -34), (129, -31.5), (135, -35), (138, -35),
     (140, -38), (146, -39), (150, -37), (153, -31), (153, -25), (146, -19), (145, -15), (142, -11),
     (141, -17), (136, -12), (132, -11), (129, -15), (125, -14), (122, -17)],
    [(166.5, -46), (172, -44), (174, -41.5), (176, -38), (178, -37.5), (175, -36), (173, -35),
     (174.5, -39), (172.5, -41), (170, -42)],
]


def on_land(lon: float, lat: float) -> bool:
    if lat <= -70:
        return True  # Antarctica, near enough
    for poly in LAND:
        inside = False
        j = len(poly) - 1
        for i in range(len(poly)):
            xi, yi = poly[i]
            xj, yj = poly[j]
            if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi) + xi:
                inside = not inside
            j = i
        if inside:
            return True
    return False


def subsolar() -> tuple[float, float]:
    """Where the sun is overhead right now (degrees), ignoring the equation of time."""
    n = UTC_NOW.timetuple().tm_yday
    decl = -23.44 * math.cos(2 * math.pi * (n + 10) / 365)
    hours = UTC_NOW.hour + UTC_NOW.minute / 60
    lon = ((12 - hours) * 15 + 180) % 360 - 180
    return decl, lon


def unit(lat: float, lon: float):
    la, lo = math.radians(lat), math.radians(lon)
    return (math.cos(la) * math.cos(lo), math.cos(la) * math.sin(lo), math.sin(la))


def globe_svg(theme: Theme, iss: dict | None) -> str:
    W, H = 900, 440
    cx, cy, R = 250, 220, 175
    period = 30.0               # one full turn
    step = 4
    tilt = -23.4                # Earth's axial tilt, as a screen rotation
    sun_lat, sun_lon = subsolar()
    sun = unit(sun_lat, sun_lon)

    day_c = theme.neon[0]
    night_c = "#3b4a7a" if theme.dark else "#94a3b8"
    city_c = "#fde68a" if theme.dark else "#d97706"

    parts = [
        "<defs>"
        f'<radialGradient id="atmo"><stop offset="0.82" stop-color="{theme.neon[1]}" stop-opacity="0"/>'
        f'<stop offset="0.9" stop-color="{theme.neon[0]}" stop-opacity="{0.35 if theme.dark else 0.22}"/>'
        f'<stop offset="1" stop-color="{theme.neon[1]}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="ocean" cx="0.38" cy="0.35"><stop offset="0" stop-color="{theme.neon[1]}" '
        f'stop-opacity="{0.22 if theme.dark else 0.12}"/><stop offset="1" stop-color="{theme.neon[1]}" '
        'stop-opacity="0.02"/></radialGradient>'
        "</defs>"
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{theme.panel}" stroke="{theme.line}"/>'
    ]
    # Background stars.
    rnd = random.Random(9)
    for _ in range(60):
        x, y = rnd.uniform(10, W - 10), rnd.uniform(10, H - 10)
        if math.hypot(x - cx, y - cy) < R + 30:
            continue
        parts.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.choice((0.6, 0.9, 1.2))}" fill="{theme.muted}">'
            f'<animate attributeName="opacity" values="0.2;0.9;0.2" dur="{rnd.uniform(2, 6):.1f}s" '
            'repeatCount="indefinite"/></circle>'
        )
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="{R * 1.16:.0f}" fill="url(#atmo)">'
        f'<animate attributeName="r" values="{R * 1.13:.0f};{R * 1.19:.0f};{R * 1.13:.0f}" dur="6s" '
        'repeatCount="indefinite"/></circle>'
        f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="url(#ocean)" stroke="{theme.neon[1]}" '
        'stroke-opacity="0.35"/>'
    )

    parts.append(f'<g transform="translate({cx} {cy}) rotate({tilt})">')
    # Static parallels: with the camera on the equator they are straight chords.
    for lat in range(-60, 61, 30):
        y = -R * math.sin(math.radians(lat))
        half = R * math.cos(math.radians(lat))
        parts.append(
            f'<line x1="{-half:.1f}" y1="{y:.1f}" x2="{half:.1f}" y2="{y:.1f}" stroke="{theme.line}" '
            f'stroke-opacity="0.7" stroke-dasharray="2 4"/>'
        )

    # One group per meridian: its points sit at x = R·cos(lat), and the whole
    # group is scaled horizontally by sin(lon + θ) as the planet turns.
    samples = 24
    marks = {"delhi": (28.6, 77.2)}
    if iss:
        marks["iss"] = (iss["lat"], iss["lon"])
    lons = list(range(-180, 180, step))
    for lon in lons:
        dots_day, dots_night, lights = [], [], []
        for lat in range(-86, 87, step):
            if not on_land(lon, lat):
                continue
            x, y = R * math.cos(math.radians(lat)), -R * math.sin(math.radians(lat))
            lit = sum(a * b for a, b in zip(unit(lat, lon), sun)) > 0
            (dots_day if lit else dots_night).append(f"M{x:.1f} {y:.1f}h0")
            if not lit and rnd.random() < 0.18:
                lights.append(
                    f'<path d="M{x:.1f} {y:.1f}h0" stroke="{city_c}" stroke-width="2.4" {DOT}>'
                    f'<animate attributeName="opacity" values="0.2;1;0.2" dur="{rnd.uniform(1.5, 4):.1f}s" '
                    'repeatCount="indefinite"/></path>'
                )
        meridian = ""
        if lon % 30 == 0:
            pts = " ".join(
                f"{R * math.cos(math.radians(a)):.1f},{-R * math.sin(math.radians(a)):.1f}"
                for a in range(-90, 91, 6)
            )
            meridian = f'<polyline points="{pts}" stroke="{theme.line}" stroke-opacity="0.8" fill="none" vector-effect="non-scaling-stroke"/>'
        extra = ""
        for name, (mlat, mlon) in marks.items():
            if lon <= mlon < lon + step:
                x, y = R * math.cos(math.radians(mlat)), -R * math.sin(math.radians(mlat))
                c = theme.neon[2] if name == "delhi" else theme.neon[3]
                extra += (
                    f'<path d="M{x:.1f} {y:.1f}h0" stroke="{c}" stroke-width="10" {DOT}/>'
                    f'<path d="M{x:.1f} {y:.1f}h0" stroke="{c}" stroke-width="10" {DOT} opacity="0.5">'
                    '<animate attributeName="stroke-width" values="10;34" dur="1.6s" repeatCount="indefinite"/>'
                    '<animate attributeName="opacity" values="0.6;0" dur="1.6s" repeatCount="indefinite"/></path>'
                )
        if not (dots_day or dots_night or meridian or extra):
            continue
        phi = math.radians(lon)
        scale = []
        opac = []
        for k in range(samples + 1):
            a = phi + 2 * math.pi * k / samples
            s = math.sin(a)
            z = math.cos(a)
            scale.append(f"{s:.3f} 1")
            opac.append(f"{0.08 + 0.92 * ((z + 1) / 2) ** 2.2:.2f}")
        parts.append(
            "<g>"
            f'<animate attributeName="opacity" values="{";".join(opac)}" dur="{period}s" repeatCount="indefinite"/>'
            "<g>"
            f'<animateTransform attributeName="transform" type="scale" values="{";".join(scale)}" '
            f'dur="{period}s" repeatCount="indefinite"/>'
            f"{meridian}"
            + (f'<path d="{"".join(dots_night)}" stroke="{night_c}" stroke-width="3.6" {DOT}/>' if dots_night else "")
            + (f'<path d="{"".join(dots_day)}" stroke="{day_c}" stroke-width="3.6" {DOT}/>' if dots_day else "")
            + f'{"".join(lights)}{extra}</g></g>'
        )
    parts.append("</g>")

    # A satellite on an inclined orbit, for depth.
    parts.append(
        f'<ellipse cx="{cx}" cy="{cy}" rx="{R + 42}" ry="34" fill="none" stroke="{theme.neon[3]}" '
        f'stroke-opacity="0.35" stroke-dasharray="3 6" transform="rotate(-14 {cx} {cy})"/>'
        f'<g transform="rotate(-14 {cx} {cy})"><circle r="4" fill="{theme.neon[3]}">'
        f'<animateMotion dur="9s" repeatCount="indefinite" path="M{cx - R - 42},{cy} '
        f'A{R + 42},34 0 1 0 {cx + R + 42},{cy} A{R + 42},34 0 1 0 {cx - R - 42},{cy}"/></circle></g>'
    )

    # Info panel.
    delhi = UTC_NOW.astimezone(IST)
    d_lit = sum(a * b for a, b in zip(unit(28.6, 77.2), sun)) > 0
    rows = [
        ("UTC", UTC_NOW.strftime("%H:%M")),
        ("NEW DELHI", delhi.strftime("%H:%M") + (" · daylight" if d_lit else " · night")),
        ("SUN OVERHEAD", f"{abs(sun_lat):.1f}°{'N' if sun_lat >= 0 else 'S'} {abs(sun_lon):.1f}°{'E' if sun_lon >= 0 else 'W'}"),
    ]
    if iss:
        rows.append(("ISS RIGHT NOW",
                     f"{abs(iss['lat']):.1f}°{'N' if iss['lat'] >= 0 else 'S'} "
                     f"{abs(iss['lon']):.1f}°{'E' if iss['lon'] >= 0 else 'W'} · {iss['alt']} km up"))
    px = 500
    parts.append(
        f'<text x="{px}" y="72" font-family="{FONT}" font-size="22" font-weight="700" fill="{theme.ink}">'
        "Earth, right now</text>"
        f'<text x="{px}" y="96" font-family="{MONO}" font-size="12" fill="{theme.muted}">'
        "sunlit land glows · night side shows city lights</text>"
    )
    for i, (k, v) in enumerate(rows):
        y = 150 + i * 56
        parts.append(
            f'<text x="{px}" y="{y}" font-family="{MONO}" font-size="11" letter-spacing="2.5" '
            f'fill="{theme.muted}">{k}</text>'
            f'<text x="{px}" y="{y + 24}" font-family="{MONO}" font-size="18" font-weight="700" '
            f'fill="{theme.neon[i % 4]}">{esc(v)}'
            f'<animate attributeName="opacity" values="0;1" dur="0.6s" begin="{0.3 + i * 0.25:.2f}s" fill="freeze"/></text>'
        )
    legend_y = 150 + len(rows) * 56 + 10
    parts.append(
        f'<circle cx="{px + 6}" cy="{legend_y}" r="5" fill="{theme.neon[2]}"/>'
        f'<text x="{px + 18}" y="{legend_y + 4}" font-family="{MONO}" font-size="12" fill="{theme.ink}">New Delhi</text>'
        + (f'<circle cx="{px + 126}" cy="{legend_y}" r="5" fill="{theme.neon[3]}"/>'
           f'<text x="{px + 138}" y="{legend_y + 4}" font-family="{MONO}" font-size="12" fill="{theme.ink}">ISS</text>'
           if iss else "")
        + f'<text x="{W - 20}" y="{H - 16}" text-anchor="end" font-family="{MONO}" font-size="11" '
        f'fill="{theme.muted}">rebuilt {delhi.strftime("%H:%M IST")} · one turn every {period:.0f}s</text>'
    )
    return svg(W, H, "".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 2. Commit galaxy replay
# ─────────────────────────────────────────────────────────────────────────────
def galaxy_svg(theme: Theme, rp: dict) -> str:
    W, H = 1200, 560
    cx, cy = 600, 225
    T = 40.0                                      # one replay of the window
    commits = rp["commits"][-160:]
    # Start the clock at the first replayed commit's day, so the timeline is full.
    first = dt.datetime.fromisoformat(commits[0][2].replace("Z", "+00:00"))
    t_start = first.replace(hour=0, minute=0, second=0, microsecond=0)
    ndays = max(1, math.ceil((UTC_NOW - t_start).total_seconds() / 86400))
    span = (UTC_NOW - t_start).total_seconds()

    def frac(iso: str) -> float:
        t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return min(0.995, max(0.0, (t - t_start).total_seconds() / span))

    counts: dict[str, int] = {}
    for repo, _, _ in commits:
        counts[repo] = counts.get(repo, 0) + 1
    planets = sorted(counts, key=lambda r: -counts[r])[:8]
    palette = theme.neon + (["#fb923c", "#60a5fa", "#34d399", "#facc15"] if theme.dark
                            else ["#ea580c", "#2563eb", "#059669", "#ca8a04"])
    colour = {r: palette[i % len(palette)] for i, r in enumerate(planets)}

    parts = [
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{theme.panel}" stroke="{theme.line}"/>'
        "<defs>"
        f'<radialGradient id="core"><stop offset="0" stop-color="#fff"/><stop offset="0.25" '
        f'stop-color="{theme.neon[3]}"/><stop offset="1" stop-color="{theme.neon[1]}" stop-opacity="0"/></radialGradient>'
        "</defs>"
    ]
    rnd = random.Random(4)
    for _ in range(110):
        x, y = rnd.uniform(8, W - 8), rnd.uniform(8, 410)
        parts.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{rnd.choice((0.5, 0.8, 1.1))}" fill="{theme.muted}">'
            f'<animate attributeName="opacity" values="0.15;0.8;0.15" dur="{rnd.uniform(2, 7):.1f}s" '
            'repeatCount="indefinite"/></circle>'
        )

    # Orbits are tilted circles, so they project to ellipses; a planet runs the
    # far (upper) half first, then the near half, and is drawn twice -- behind
    # the star while far, in front of it while near.
    back, front = [], []
    for i, repo in enumerate(planets):
        rx = 110 + i * 50
        ry = rx * 0.3
        period = 9 * (rx / 120) ** 1.5           # Kepler: outer planets are slower
        phase = rnd.uniform(0, period)
        size = 5 + 2.6 * math.log2(1 + counts[repo])
        c = colour[repo]
        path = f"M{cx - rx},{cy} A{rx},{ry} 0 0 1 {cx + rx},{cy} A{rx},{ry} 0 0 1 {cx - rx},{cy}"
        back.append(
            f'<path d="M{cx - rx},{cy} A{rx},{ry} 0 0 1 {cx + rx},{cy}" stroke="{c}" stroke-opacity="0.22" fill="none"/>'
        )
        front.append(
            f'<path d="M{cx + rx},{cy} A{rx},{ry} 0 0 1 {cx - rx},{cy}" stroke="{c}" stroke-opacity="0.45" fill="none"/>'
        )
        bursts = []
        for repo2, _, when in commits:
            if repo2 != repo:
                continue
            k = frac(when)
            k2 = min(k + 0.035, 0.999)
            bursts.append(
                f'<circle r="0" fill="none" stroke="{c}" stroke-width="2">'
                f'<animate attributeName="r" values="0;0;{size + 3:.0f};{size + 22:.0f};{size + 22:.0f}" '
                f'keyTimes="0;{k:.4f};{min(k + 0.002, 0.999):.4f};{k2:.4f};1" dur="{T}s" repeatCount="indefinite"/>'
                f'<animate attributeName="opacity" values="0;0;1;0;0" '
                f'keyTimes="0;{k:.4f};{min(k + 0.002, 0.999):.4f};{k2:.4f};1" dur="{T}s" repeatCount="indefinite"/>'
                "</circle>"
            )
        label = clip(repo, 22)
        body = (
            f'<circle r="{size:.1f}" fill="{c}"/>'
            f'<circle r="{size:.1f}" fill="#fff" opacity="0.25" cx="{-size * 0.3:.1f}" cy="{-size * 0.3:.1f}" '
            f'transform="scale(0.55)"/>'
            + "".join(bursts)
            + f'<text y="{-size - 7:.0f}" text-anchor="middle" font-family="{MONO}" font-size="11" '
            f'fill="{theme.ink}">{esc(label)} · {counts[repo]}</text>'
        )
        for layer, vis in ((back, "1;0"), (front, "0;1")):
            layer.append(
                f'<g opacity="{vis[0]}">'
                f'<animate attributeName="opacity" values="{vis}" calcMode="discrete" keyTimes="0;0.5" '
                f'dur="{period:.2f}s" begin="-{phase:.2f}s" repeatCount="indefinite"/>'
                f'<g><animateMotion path="{path}" dur="{period:.2f}s" begin="-{phase:.2f}s" '
                f'repeatCount="indefinite"/>{body}</g></g>'
            )

    parts += back
    # The star: me. It flares on every commit.
    flares = []
    for _, _, when in commits:
        k = frac(when)
        flares.append(
            f'<circle cx="{cx}" cy="{cy}" r="18" fill="none" stroke="{theme.neon[3]}" stroke-width="1.5" opacity="0">'
            f'<animate attributeName="r" values="18;18;60;60" keyTimes="0;{k:.4f};{min(k + 0.03, 0.999):.4f};1" '
            f'dur="{T}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;0;0.8;0;0" keyTimes="0;{k:.4f};{min(k + 0.001, 0.999):.4f};'
            f'{min(k + 0.03, 0.999):.4f};1" dur="{T}s" repeatCount="indefinite"/></circle>'
        )
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="46" fill="url(#core)" opacity="0.8">'
        '<animate attributeName="r" values="42;52;42" dur="3s" repeatCount="indefinite"/></circle>'
        f'<circle cx="{cx}" cy="{cy}" r="12" fill="#fff"/>'
        + "".join(flares)
    )
    parts += front

    # Title.
    parts.append(
        f'<text x="30" y="40" font-family="{FONT}" font-size="20" font-weight="700" fill="{theme.ink}">'
        f"Commit replay · last {ndays} days</text>"
        f'<text x="30" y="62" font-family="{MONO}" font-size="12" fill="{theme.muted}">'
        "each repo is a planet · each commit lands as a burst · loops forever</text>"
    )

    # Timeline, playhead, date, counter, and the message of the latest landing.
    L, R_, ty = 60, W - 60, 470
    parts.append(
        f'<line x1="{L}" y1="{ty}" x2="{R_}" y2="{ty}" stroke="{theme.line}" stroke-width="2"/>'
    )
    for repo, _, when in commits:
        x = L + frac(when) * (R_ - L)
        parts.append(
            f'<line x1="{x:.1f}" y1="{ty - 7}" x2="{x:.1f}" y2="{ty + 7}" '
            f'stroke="{colour.get(repo, theme.muted)}" stroke-opacity="0.75"/>'
        )
    parts.append(
        f'<rect x="{L}" y="{ty - 1.5}" width="0" height="3" fill="{theme.neon[0]}">'
        f'<animate attributeName="width" values="0;{R_ - L}" dur="{T}s" repeatCount="indefinite"/></rect>'
        f'<circle cx="{L}" cy="{ty}" r="6" fill="{theme.neon[0]}">'
        f'<animate attributeName="cx" values="{L};{R_}" dur="{T}s" repeatCount="indefinite"/></circle>'
    )
    # Day labels, one per day, each visible for its slice of the loop.
    step_days = max(1, ndays // 30)
    for d in range(0, ndays, step_days):
        k1, k2 = d / ndays, min((d + step_days) / ndays, 1)
        day = (t_start + dt.timedelta(days=d)).astimezone(IST).strftime("%d %b %Y")
        parts.append(
            f'<text x="{L}" y="{ty + 34}" font-family="{MONO}" font-size="14" font-weight="700" '
            f'fill="{theme.neon[0]}" opacity="0">{day}'
            f'<animate attributeName="opacity" values="0;1;0" calcMode="discrete" '
            f'keyTimes="0;{k1:.4f};{k2:.4f}" dur="{T}s" repeatCount="indefinite"/></text>'
        )
    # Running commit counter and the message of the commit that just landed.
    for i, (repo, msg, when) in enumerate(commits):
        k1 = frac(when)
        k2 = frac(commits[i + 1][2]) if i + 1 < len(commits) else 0.999
        if k2 <= k1:
            k2 = min(k1 + 0.0005, 0.9995)
        parts.append(
            f'<text x="{R_}" y="{ty + 34}" text-anchor="end" font-family="{MONO}" font-size="14" '
            f'font-weight="700" fill="{theme.neon[2]}" opacity="0">{i + 1} commits'
            f'<animate attributeName="opacity" values="0;1;{1 if i + 1 == len(commits) else 0}" calcMode="discrete" '
            f'keyTimes="0;{k1:.4f};{k2:.4f}" dur="{T}s" repeatCount="indefinite"/></text>'
            f'<text x="{W / 2}" y="{ty - 22}" text-anchor="middle" font-family="{MONO}" font-size="13" '
            f'fill="{theme.ink}" opacity="0"><tspan fill="{colour.get(repo, theme.muted)}" font-weight="700">'
            f'{esc(clip(repo, 26))}</tspan> › {esc(clip(msg, 70))}'
            f'<animate attributeName="opacity" values="0;1;{1 if i + 1 == len(commits) else 0}" calcMode="discrete" '
            f'keyTimes="0;{k1:.4f};{k2:.4f}" dur="{T}s" repeatCount="indefinite"/></text>'
        )
    parts.append(
        f'<text x="{L}" y="{H - 22}" font-family="{MONO}" font-size="11" fill="{theme.muted}">'
        "planet size = commits in the window · outer orbits are slower (Kepler)</text>"
    )
    parts.append(
        f'<text x="{R_}" y="{H - 22}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{theme.muted}">'
        f"{len(commits)} commits replayed in {T:.0f}s · rebuilt {UTC_NOW.astimezone(IST).strftime('%H:%M IST')}</text>"
    )
    return svg(W, H, "".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# 3. Contribution helix
# ─────────────────────────────────────────────────────────────────────────────
def helix_svg(theme: Theme, cal: dict) -> str:
    W, H = 1200, 300
    days = cal["days"]
    n = len(days)
    L, R_ = 60, W - 60
    cy, A = 140, 66
    turns = 5
    T = 12.0
    dx = (R_ - L) / max(1, n - 1)
    peak = max([c for _, c in days] + [1])
    ramp = [theme.neon[1], theme.neon[0], theme.neon[3], theme.neon[2]]
    total = sum(c for _, c in days)

    parts = [
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="14" fill="{theme.panel}" stroke="{theme.line}"/>'
        f'<text x="30" y="36" font-family="{FONT}" font-size="18" font-weight="700" fill="{theme.ink}">'
        f"{n} days of contributions, as a double helix</text>"
        f'<text x="{W - 30}" y="36" text-anchor="end" font-family="{MONO}" font-size="12" fill="{theme.muted}">'
        f"{total} contributions · rung = a day I shipped · brighter = busier</text>"
    ]
    rungs, strand_b, strand_a = [], [], []
    for i, (date, c) in enumerate(days):
        x = L + i * dx
        phi = 2 * math.pi * turns * i / max(1, n - 1)
        # y = cy + A·sin(phi + ωt)  →  phase phi + π/2 on the cosine-shaped spline
        ya = shm("cy", cy - A, cy + A, T, phi + math.pi / 2)
        yb = shm("cy", cy - A, cy + A, T, phi + math.pi / 2 + math.pi)
        # depth = cos(phi + ωt): near side brighter
        oa = shm("opacity", 0.18, 1, T, phi + math.pi)
        ob = shm("opacity", 0.18, 1, T, phi)
        if c:
            t = math.sqrt(c / peak)
            col = ramp[min(3, int(t * 4))]
            r = 2.2 + 4.2 * t
            rungs.append(
                f'<line x1="{x:.1f}" x2="{x:.1f}" y1="{cy}" y2="{cy}" stroke="{col}" stroke-width="1.4" '
                f'stroke-opacity="{0.25 + 0.5 * t:.2f}">'
                + shm("y1", cy - A, cy + A, T, phi + math.pi / 2)
                + shm("y2", cy - A, cy + A, T, phi + math.pi / 2 + math.pi)
                + "</line>"
            )
        else:
            col, r = theme.line, 1.6
        strand_a.append(f'<circle cx="{x:.1f}" cy="{cy}" r="{r:.1f}" fill="{col}">{ya}{oa}</circle>')
        strand_b.append(f'<circle cx="{x:.1f}" cy="{cy}" r="1.6" fill="{theme.muted}">{yb}{ob}</circle>')
    parts += rungs + strand_b + strand_a
    for i, (date, _) in enumerate(days):
        if date.endswith("-01"):
            x = L + i * dx
            parts.append(
                f'<line x1="{x:.1f}" y1="{cy + A + 16}" x2="{x:.1f}" y2="{cy + A + 22}" stroke="{theme.muted}"/>'
                f'<text x="{x:.1f}" y="{cy + A + 38}" text-anchor="middle" font-family="{MONO}" font-size="11" '
                f'fill="{theme.muted}">{dt.date.fromisoformat(date).strftime("%b")}</text>'
            )
    parts.append(
        f'<text x="{R_}" y="{H - 14}" text-anchor="end" font-family="{MONO}" font-size="11" fill="{theme.muted}">'
        f"today → · rebuilt {UTC_NOW.astimezone(IST).strftime('%H:%M IST')}</text>"
    )
    return svg(W, H, "".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="live-out")
    ap.add_argument("--prev", default=None)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    prev = {}
    if args.prev and (Path(args.prev) / "data3d.json").exists():
        prev = json.loads((Path(args.prev) / "data3d.json").read_text(encoding="utf-8"))

    data, status = {}, []
    for key, fn in (("iss", fetch_iss), ("calendar", fetch_calendar), ("replay", fetch_replay)):
        try:
            data[key] = fn()
            status.append(f"{key}: live")
        except Exception as e:  # noqa: BLE001
            data[key] = prev.get(key)
            status.append(f"{key}: {'cached' if data[key] else 'missing'} ({type(e).__name__})")

    for dark in (True, False):
        t = Theme(dark)
        # The ISS is only shown when the position is fresh; a stale one would lie.
        (out / f"live-globe-{t.suffix}.svg").write_text(
            globe_svg(t, data["iss"] if status[0] == "iss: live" else None), encoding="utf-8")
        if data["replay"]:
            (out / f"live-galaxy-{t.suffix}.svg").write_text(galaxy_svg(t, data["replay"]), encoding="utf-8")
        if data["calendar"]:
            (out / f"live-helix-{t.suffix}.svg").write_text(helix_svg(t, data["calendar"]), encoding="utf-8")
    (out / "data3d.json").write_text(json.dumps(data), encoding="utf-8")
    print("\n".join(status))


if __name__ == "__main__":
    main()
