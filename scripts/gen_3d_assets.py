"""Generate the animated 3D SVGs used by README.md.

GitHub strips <script> from rendered markdown, so nothing here is scripted:
the geometry is projected in Python at N keyframes and baked into SMIL
<animate> values. Browsers interpolate between the frames, which is real 3D
rotation rather than a 2D fake. Every animated element also carries a static
attribute, so a renderer without SMIL still shows a sensible still frame.

Usage:  python scripts/gen_3d_assets.py
Output: assets/ring-3d-{light,dark}.svg   rotating account/transfer ring
        assets/mesh-3d-{light,dark}.svg   travelling 3D wireframe surface

Both builders assert that every projected point lands inside the viewBox, so a
tweak to the camera can't silently clip the artwork.
"""

from __future__ import annotations

import math
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"

# One palette per GitHub colour mode. Backgrounds stay transparent so the SVG
# sits on whatever GitHub paints behind it.
THEMES = {
    "light": {
        "edge": "#94a3b8",
        "node": "#4f46e5",
        "node_alt": "#0ea5e9",
        "alert": "#e11d48",
        "mesh_near": "#4f46e5",
        "mesh_far": "#a5b4fc",
    },
    "dark": {
        "edge": "#4c5a72",
        "node": "#a78bfa",
        "node_alt": "#22d3ee",
        "alert": "#fb7185",
        "mesh_near": "#a78bfa",
        "mesh_far": "#3b3168",
    },
}


def r(value: float) -> str:
    """Round for file size; SMIL interpolates fine at one decimal."""
    return f"{value:.1f}".rstrip("0").rstrip(".")


def rotate_y(point, angle):
    x, y, z = point
    c, s = math.cos(angle), math.sin(angle)
    return (x * c + z * s, y, -x * s + z * c)


def rotate_x(point, angle):
    x, y, z = point
    c, s = math.cos(angle), math.sin(angle)
    return (x, y * c - z * s, y * s + z * c)


class Camera:
    """Perspective camera that also reports how deep each point sits."""

    def __init__(self, width, height, distance, depth_span):
        self.width = width
        self.height = height
        self.distance = distance
        self.depth_span = depth_span
        self.seen = []  # every projected point, for the bounds check

    def project(self, point):
        x, y, z = point
        factor = self.distance / (self.distance - z)
        depth = max(0.0, min(1.0, (z + self.depth_span) / (2 * self.depth_span)))
        screen = (self.width / 2 + x * factor, self.height / 2 + y * factor)
        self.seen.append(screen)
        return (screen[0], screen[1], depth)

    def check(self, name, margin=2.0):
        """Fail loudly rather than ship art that is clipped by the viewBox."""
        xs = [x for x, _ in self.seen]
        ys = [y for _, y in self.seen]
        box = (min(xs), max(xs), min(ys), max(ys))
        if (box[0] < margin or box[1] > self.width - margin
                or box[2] < margin or box[3] > self.height - margin):
            raise SystemExit(
                f"{name}: geometry leaves the {self.width}x{self.height} "
                f"viewBox (x {box[0]:.0f}..{box[1]:.0f}, "
                f"y {box[2]:.0f}..{box[3]:.0f})"
            )
        return box


def animate(attribute, values, duration):
    return (f'<animate attributeName="{attribute}" values="{values}" '
            f'dur="{duration}s" repeatCount="indefinite"/>')


def series(values):
    return ";".join(r(v) for v in values)


# ----------------------------- the rotating ring -----------------------------

def torus_points(count: int, major: float, minor: float):
    """Nodes spread over a torus: a ring of accounts with real thickness."""
    golden = math.pi * (3.0 - math.sqrt(5.0))
    points = []
    for i in range(count):
        phi = 2 * math.pi * i / count          # around the ring
        theta = golden * i * 2.0               # around the tube
        radius = major + minor * math.cos(theta)
        points.append((radius * math.cos(phi),
                       minor * math.sin(theta),
                       radius * math.sin(phi)))
    return points


def nearest_edges(points, per_node: int = 2):
    """Connect each node to its closest neighbours, deduplicated."""
    edges = set()
    for i, a in enumerate(points):
        closest = sorted(
            (math.dist(a, b), j) for j, b in enumerate(points) if j != i
        )
        for _, j in closest[:per_node]:
            edges.add((min(i, j), max(i, j)))
    return sorted(edges)


def ring_svg(theme: str, nodes: int = 44, frames: int = 30,
             width: int = 880, height: int = 280, duration: int = 26) -> str:
    """A money-movement ring, rotating in perspective.

    Wide and shallow on purpose: it reads as a banner rather than a blob, and
    a ring is the shape fraud actually makes in a transaction graph.
    """
    colours = THEMES[theme]
    major, minor = 290.0, 40.0
    tilt = math.radians(12)
    camera = Camera(width, height, distance=1800.0, depth_span=major + minor)
    points = torus_points(nodes, major, minor)
    edges = nearest_edges(points)
    alerts = {5, 16, 27, 38}  # a few nodes read as flagged accounts

    # frames + 1 so the last frame equals the first and the loop is seamless.
    projected = [
        [camera.project(rotate_x(rotate_y(p, 2 * math.pi * f / frames), tilt))
         for p in points]
        for f in range(frames + 1)
    ]
    camera.check(f"ring-3d-{theme}")

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
        'aria-label="A ring of accounts and transfers rotating in 3D">',
        "<defs>",
        f'<radialGradient id="glow-{theme}">'
        f'<stop offset="0%" stop-color="{colours["alert"]}" stop-opacity=".5"/>'
        f'<stop offset="100%" stop-color="{colours["alert"]}" stop-opacity="0"/>'
        "</radialGradient>",
        "</defs>",
        # Edges first so the nodes sit on top of them.
        f'<g stroke="{colours["edge"]}" stroke-width="1" fill="none">',
    ]

    for i, j in edges:
        xs1 = [frame[i][0] for frame in projected]
        ys1 = [frame[i][1] for frame in projected]
        xs2 = [frame[j][0] for frame in projected]
        ys2 = [frame[j][1] for frame in projected]
        # Fade the edges that swing round the back.
        ops = [round(0.1 + 0.4 * (frame[i][2] + frame[j][2]) / 2, 2)
               for frame in projected]
        out.append(
            f'<line x1="{r(xs1[0])}" y1="{r(ys1[0])}" x2="{r(xs2[0])}" '
            f'y2="{r(ys2[0])}" opacity="{ops[0]}">'
            + animate("x1", series(xs1), duration)
            + animate("y1", series(ys1), duration)
            + animate("x2", series(xs2), duration)
            + animate("y2", series(ys2), duration)
            + animate("opacity", ";".join(str(o) for o in ops), duration)
            + "</line>"
        )
    out.append("</g>")

    for index in range(nodes):
        xs = [frame[index][0] for frame in projected]
        ys = [frame[index][1] for frame in projected]
        # Radius and opacity carry the depth cue: near nodes bigger, brighter.
        radii = [1.7 + 3.3 * frame[index][2] for frame in projected]
        ops = [round(0.32 + 0.68 * frame[index][2], 2) for frame in projected]
        fill = colours["alert"] if index in alerts else (
            colours["node"] if index % 3 else colours["node_alt"])

        if index in alerts:
            halo = [value * 4.0 for value in radii]
            out.append(
                f'<circle cx="{r(xs[0])}" cy="{r(ys[0])}" r="{r(halo[0])}" '
                f'fill="url(#glow-{theme})">'
                + animate("cx", series(xs), duration)
                + animate("cy", series(ys), duration)
                + animate("r", series(halo), duration)
                + animate("opacity", "1;.2;1", 2.4)
                + "</circle>"
            )

        out.append(
            f'<circle cx="{r(xs[0])}" cy="{r(ys[0])}" r="{r(radii[0])}" '
            f'fill="{fill}" opacity="{ops[0]}">'
            + animate("cx", series(xs), duration)
            + animate("cy", series(ys), duration)
            + animate("r", series(radii), duration)
            + animate("opacity", ";".join(str(o) for o in ops), duration)
            + "</circle>"
        )

    out.append("</svg>")
    return "".join(out)


# ---------------------------- the travelling surface -------------------------

def mesh_svg(theme: str, columns: int = 17, rows: int = 9, frames: int = 24,
             width: int = 880, height: int = 220, duration: int = 14) -> str:
    """A wireframe surface with a wave travelling across it, in real 3D."""
    colours = THEMES[theme]
    span_x, span_z, amplitude = 340.0, 130.0, 30.0
    yaw, pitch = math.radians(0), math.radians(31)
    camera = Camera(width, height, distance=1600.0, depth_span=span_z + amplitude)

    def surface(u: int, v: int, phase: float):
        x = (u / (columns - 1) - 0.5) * 2 * span_x
        z = (v / (rows - 1) - 0.5) * 2 * span_z
        y = (amplitude * math.sin(3.1 * x / span_x + phase)
             * math.cos(1.6 * z / span_z + phase * 0.6))
        return rotate_x(rotate_y((x, -y, z), yaw), pitch)

    grid = [
        [[camera.project(surface(u, v, 2 * math.pi * f / frames))
          for u in range(columns)]
         for v in range(rows)]
        for f in range(frames + 1)
    ]
    camera.check(f"mesh-3d-{theme}")

    def polyline(sequences):
        """One polyline whose vertices are animated through every frame."""
        values = ";".join(
            " ".join(f"{r(x)},{r(y)}" for x, y, _ in seq) for seq in sequences
        )
        first = " ".join(f"{r(x)},{r(y)}" for x, y, _ in sequences[0])
        return (f'<polyline points="{first}">'
                + animate("points", values, duration)
                + "</polyline>")

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
        'aria-label="Animated 3D wireframe surface">',
        "<defs>",
        f'<linearGradient id="mesh-{theme}" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{colours["mesh_far"]}"/>'
        f'<stop offset="100%" stop-color="{colours["mesh_near"]}"/>'
        "</linearGradient>",
        "</defs>",
        f'<g fill="none" stroke="url(#mesh-{theme})" stroke-width="1.1" '
        'stroke-linecap="round" opacity=".9">',
    ]
    for v in range(rows):
        out.append(polyline([grid[f][v] for f in range(frames + 1)]))
    for u in range(columns):
        out.append(polyline([[grid[f][v][u] for v in range(rows)]
                             for f in range(frames + 1)]))
    out.append("</g></svg>")
    return "".join(out)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        for name, svg in (("ring-3d", ring_svg(theme)),
                          ("mesh-3d", mesh_svg(theme))):
            path = ASSETS / f"{name}-{theme}.svg"
            path.write_text(svg, encoding="utf-8")
            print(f"{path.name}: {len(svg) / 1024:.1f} KB")


if __name__ == "__main__":
    main()
