#!/usr/bin/env python3
"""
Animated section headers and rolling metric counters for the profile README.

    title-{slug}-{theme}.svg    section headings: letters rise in one by one,
                                a wave ripples through them every few seconds,
                                the fill cycles through the four accents and a
                                faint RGB-split glitch fires now and then
    metric-{id}-{theme}.svg     a project's headline number on an odometer:
                                each digit rolls into place, holds, fades and
                                rolls again

Pure SMIL like the other generators: GitHub strips <script>, so everything is
baked into <animate> elements. Every animated element also has a sensible
static value, so a renderer without SMIL still shows the finished text.

    python scripts/gen_motion_assets.py      # writes assets/title-*, assets/metric-*

No dependencies.
"""

from __future__ import annotations

import html
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

NEON = ["#22d3ee", "#8b5cf6", "#f472b6", "#c3f53c"]
NEON_LIGHT = ["#0891b2", "#7c3aed", "#db2777", "#65a30d"]
MONO = "'JetBrains Mono', SFMono-Regular, Consolas, 'Liberation Mono', monospace"

TITLES = {
    "about": "ABOUT ME",
    "experience": "EXPERIENCE",
    "build": "WHAT I BUILD",
    "more": "MORE SYSTEMS",
    "opensource": "OPEN SOURCE",
    "stack": "THE STACK",
    "live": "LIVE FROM DELHI",
    "arena": "THE ARENA",
    "numbers": "THE NUMBERS",
    "recent": "RECENTLY PUSHED",
    "talk": "LET'S TALK",
}

# id -> (value, caption, accent index). Digits roll; everything else is static.
METRICS = {
    "routeos": ("20–35%", "LESS FLEET DISTANCE VS GREEDY", 0),
    "docminds": ("19", "FILE TYPES IN · PAGE CITES OUT", 1),
    "crucible": ("128MB", "CAP · NO NETWORK · 2s TIMEOUT", 3),
    "miniredis": ("29µs", "P50 LATENCY · 63K OPS/S PEAK", 2),
    "gridsmith": ("0", "SILENT ERRORS IN 202 CELLS", 0),
    "sentinelgraph": ("3..5", "HOP RINGS IN ONE CYPHER LINE", 1),
}


class Theme:
    def __init__(self, dark: bool):
        self.dark = dark
        self.neon = NEON if dark else NEON_LIGHT
        self.muted = "#7d8590" if dark else "#64748b"
        self.suffix = "dark" if dark else "light"


def cycling_stops(theme: Theme, dur: str, phase: int = 0) -> str:
    out = []
    for i, off in enumerate(("0%", "50%", "100%")):
        k = (i + phase) % 4
        seq = theme.neon[k:] + theme.neon[:k]
        seq = seq + [seq[0]]
        out.append(
            f'<stop offset="{off}" stop-color="{seq[0]}">'
            f'<animate attributeName="stop-color" values="{";".join(seq)}" '
            f'dur="{dur}" repeatCount="indefinite"/></stop>'
        )
    return "".join(out)


def svg(w: int, h: int, body: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" fill="none" role="img">{body}</svg>\n'
    )


# ─────────────────────────────────────────────────────────────────────────────
# Section titles
# ─────────────────────────────────────────────────────────────────────────────
def title_svg(theme: Theme, text: str) -> str:
    W, H = 1200, 92
    fs = 34
    adv = 31.0                      # per-letter pitch, generous letter-spacing
    span = adv * (len(text) - 1)
    x0 = W / 2 - span / 2
    y = 56
    wave_cycle = 6.0

    parts = [
        "<defs>"
        f'<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="{x0 - 20:.0f}" y1="0" '
        f'x2="{x0 + span + 20:.0f}" y2="0">{cycling_stops(theme, "8s")}</linearGradient>'
        f'<linearGradient id="wl" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{theme.neon[1]}" '
        f'stop-opacity="0"/><stop offset="1" stop-color="{theme.neon[1]}" stop-opacity="0.8"/></linearGradient>'
        f'<linearGradient id="wr" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{theme.neon[2]}" '
        f'stop-opacity="0.8"/><stop offset="1" stop-color="{theme.neon[2]}" stop-opacity="0"/></linearGradient>'
        "</defs>"
    ]

    # Wings either side of the title, each with a spark running outwards.
    left_end, right_start = x0 - 66, x0 + span + 66
    parts.append(
        f'<rect x="{left_end - 260:.0f}" y="{y - 12}" width="260" height="1.6" fill="url(#wl)"/>'
        f'<rect x="{right_start:.0f}" y="{y - 12}" width="260" height="1.6" fill="url(#wr)"/>'
        f'<circle cy="{y - 11.2}" r="2.6" fill="{theme.neon[0]}">'
        f'<animate attributeName="cx" values="{left_end:.0f};{left_end - 260:.0f}" dur="2.6s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="1;0" dur="2.6s" repeatCount="indefinite"/></circle>'
        f'<circle cy="{y - 11.2}" r="2.6" fill="{theme.neon[0]}">'
        f'<animate attributeName="cx" values="{right_start:.0f};{right_start + 260:.0f}" dur="2.6s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="1;0" dur="2.6s" repeatCount="indefinite"/></circle>'
    )
    # Spinning diamonds.
    for cx, c, d in ((left_end + 20, theme.neon[1], "-"), (right_start - 20, theme.neon[2], "")):
        parts.append(
            f'<g transform="translate({cx:.0f} {y - 11})"><rect x="-7" y="-7" width="14" height="14" '
            f'fill="none" stroke="{c}" stroke-width="2">'
            f'<animateTransform attributeName="transform" type="rotate" values="45;{d}315" dur="5s" '
            'repeatCount="indefinite"/></rect>'
            f'<rect x="-2.5" y="-2.5" width="5" height="5" fill="{c}" transform="rotate(45)">'
            '<animate attributeName="opacity" values="1;0.3;1" dur="1.6s" repeatCount="indefinite"/></rect></g>'
        )

    # Glitch ghosts: the whole word, offset, flashing for a few frames.
    for dx, c, begin in ((-3, theme.neon[0], 0.0), (3, theme.neon[2], 0.06)):
        parts.append(
            f'<g opacity="0" transform="translate({dx} 0)">'
            '<animate attributeName="opacity" values="0;0;0.7;0;0.5;0;0" '
            'keyTimes="0;0.80;0.81;0.82;0.83;0.84;1" '
            f'dur="7s" begin="{2.5 + begin:.2f}s" repeatCount="indefinite"/>'
        )
        for i, ch in enumerate(text):
            if ch != " ":
                parts.append(
                    f'<text x="{x0 + i * adv:.1f}" y="{y}" text-anchor="middle" font-family="{MONO}" '
                    f'font-size="{fs}" font-weight="800" fill="{c}">{html.escape(ch)}</text>'
                )
        parts.append("</g>")

    # The letters: rise in on load, then a wave rolls through every cycle.
    for i, ch in enumerate(text):
        if ch == " ":
            continue
        x = x0 + i * adv
        d0 = 0.15 + i * 0.05
        k = (i / max(1, len(text))) * 0.35
        parts.append(
            f'<g><g opacity="1">'
            f'<animate attributeName="opacity" values="0;1" dur="0.45s" begin="0s" fill="freeze" '
            f'keyTimes="0;1" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>'
            f'<animateTransform attributeName="transform" type="translate" values="0 0;0 0;0 -7;0 0;0 0" '
            f'keyTimes="0;{k:.3f};{k + 0.06:.3f};{k + 0.14:.3f};1" dur="{wave_cycle}s" begin="1.6s" '
            'repeatCount="indefinite"/>'
            f'<text x="{x:.1f}" y="{y}" text-anchor="middle" font-family="{MONO}" font-size="{fs}" '
            f'font-weight="800" fill="url(#ink)">{html.escape(ch)}'
            f'<animate attributeName="y" values="{y + 22};{y}" dur="0.55s" begin="{d0:.2f}s" fill="freeze" '
            'calcMode="spline" keyTimes="0;1" keySplines="0.2 0.8 0.2 1"/>'
            f'<animate attributeName="opacity" values="0;0;1" keyTimes="0;{d0 / (d0 + 0.3):.3f};1" '
            f'dur="{d0 + 0.3:.2f}s" fill="freeze"/>'
            "</text></g></g>"
        )

    # A thin underline that draws itself, then a highlight runs along it.
    parts.append(
        f'<rect x="{W / 2:.0f}" y="{y + 16}" width="0" height="2" rx="1" fill="url(#ink)" opacity="0.6">'
        f'<animate attributeName="x" values="{W / 2:.0f};{x0 - 10:.0f}" dur="0.9s" begin="0.4s" fill="freeze"/>'
        f'<animate attributeName="width" values="0;{span + 20:.0f}" dur="0.9s" begin="0.4s" fill="freeze"/></rect>'
        f'<rect x="{x0 - 10:.0f}" y="{y + 15.5}" width="46" height="3" rx="1.5" fill="{theme.neon[3]}" opacity="0">'
        f'<animate attributeName="x" values="{x0 - 10:.0f};{x0 + span - 36:.0f};{x0 - 10:.0f}" dur="4s" '
        'begin="1.3s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="0;0.9" dur="0.3s" begin="1.3s" fill="freeze"/></rect>'
    )
    return svg(W, H, "".join(parts))


# ─────────────────────────────────────────────────────────────────────────────
# Odometer metrics
# ─────────────────────────────────────────────────────────────────────────────
def metric_svg(theme: Theme, value: str, caption: str, accent: int) -> str:
    W, H = 360, 118
    fs, adv, row = 50, 31.0, 58
    y = 62
    span = adv * (len(value) - 1)
    x0 = W / 2 - span / 2
    c = theme.neon[accent]
    cycle = 9.0

    parts = [
        "<defs>"
        f'<linearGradient id="ink" gradientUnits="userSpaceOnUse" x1="{x0 - 20:.0f}" y1="0" '
        f'x2="{x0 + span + 20:.0f}" y2="0">{cycling_stops(theme, "7s", accent)}</linearGradient>'
        f'<clipPath id="win"><rect x="0" y="{y - fs * 0.86:.0f}" width="{W}" height="{fs * 1.08:.0f}"/></clipPath>'
        "</defs>"
    ]

    # Soft glow behind the number, breathing. Fainter on white.
    glow = "0.04;0.14;0.04" if theme.dark else "0.02;0.07;0.02"
    parts.append(
        f'<ellipse cx="{W / 2}" cy="{y - 16}" rx="{span / 2 + 50:.0f}" ry="34" fill="{c}" opacity="0.06">'
        f'<animate attributeName="opacity" values="{glow}" dur="3.2s" repeatCount="indefinite"/></ellipse>'
    )

    parts.append('<g clip-path="url(#win)"><g>')
    # The whole number fades just before each re-roll, so the reset is unseen.
    parts.append(
        '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.9;0.96;1" '
        f'dur="{cycle}s" repeatCount="indefinite"/>'
    )
    for i, ch in enumerate(value):
        x = x0 + i * adv
        if ch.isdigit():
            target = int(ch)
            turns = 1 + (i % 2)                      # alternate digits spin further
            seq = [str(d % 10) for d in range(10 * turns + target + 1)]
            end = -(len(seq) - 1) * row
            dur_roll = 1.3 + i * 0.22
            k = dur_roll / cycle
            col = "".join(
                f'<text x="{x:.1f}" y="{y + j * row}" text-anchor="middle" font-family="{MONO}" '
                f'font-size="{fs}" font-weight="800" fill="url(#ink)">{d}</text>'
                for j, d in enumerate(seq)
            )
            parts.append(
                f'<g transform="translate(0 {end})">'
                f'<animateTransform attributeName="transform" type="translate" '
                f'values="0 0;0 {end};0 {end}" keyTimes="0;{k:.3f};1" calcMode="spline" '
                f'keySplines="0.15 0.6 0.25 1;0 0 1 1" dur="{cycle}s" repeatCount="indefinite"/>'
                f"{col}</g>"
            )
        else:
            parts.append(
                f'<text x="{x:.1f}" y="{y}" text-anchor="middle" font-family="{MONO}" font-size="{fs}" '
                f'font-weight="800" fill="url(#ink)">{html.escape(ch)}</text>'
            )
    parts.append("</g></g>")

    # Caption, with a scanning underline above it.
    parts.append(
        f'<rect x="{W / 2 - 70}" y="{y + 12}" width="140" height="1.5" fill="{c}" opacity="0.35"/>'
        f'<rect x="{W / 2 - 70}" y="{y + 11.5}" width="26" height="2.5" rx="1" fill="{c}">'
        f'<animate attributeName="x" values="{W / 2 - 70};{W / 2 + 44};{W / 2 - 70}" dur="3s" '
        'repeatCount="indefinite"/></rect>'
        f'<text x="{W / 2}" y="{y + 38}" text-anchor="middle" font-family="{MONO}" font-size="11.5" '
        f'letter-spacing="1.6" fill="{theme.muted}">{html.escape(caption)}</text>'
    )
    return svg(W, H, "".join(parts))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    n = 0
    for dark in (True, False):
        t = Theme(dark)
        for slug, text in TITLES.items():
            (OUT / f"title-{slug}-{t.suffix}.svg").write_text(title_svg(t, text), encoding="utf-8")
            n += 1
        for mid, (value, caption, accent) in METRICS.items():
            (OUT / f"metric-{mid}-{t.suffix}.svg").write_text(
                metric_svg(t, value, caption, accent), encoding="utf-8")
            n += 1
    print(f"wrote {n} files to {OUT}")


if __name__ == "__main__":
    main()
