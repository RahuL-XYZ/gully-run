"""
utils.py
Helper functions shared across modules.
"""
from __future__ import annotations

from panda3d.core import GeomNode, Geom, GeomVertexFormat, GeomVertexData
from panda3d.core import GeomVertexWriter, GeomTriangles, NodePath
from panda3d.core import LColor, LPoint3


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation."""
    return a + (b - a) * t


def clamp(val: float, lo: float, hi: float) -> float:
    """Clamp val to [lo, hi]."""
    return max(lo, min(hi, val))


def make_box(
    name: str,
    w: float,
    d: float,
    h: float,
    color: tuple[float, float, float, float],
) -> NodePath:
    """
    Build a solid coloured axis-aligned box geometry centred on X/Y,
    with its bottom at Z=0.

    w = half-extent in X
    d = half-extent in Y
    h = full height in Z
    """
    fmt = GeomVertexFormat.get_v3c4()
    vdata = GeomVertexData(name, fmt, Geom.UH_static)
    vdata.set_num_rows(24)

    vertex = GeomVertexWriter(vdata, "vertex")
    colour = GeomVertexWriter(vdata, "color")

    r, g, b, a = color

    # 6 faces × 4 vertices
    faces = [
        # bottom  (z=0)
        [(-w, -d, 0), (w, -d, 0), (w, d, 0), (-w, d, 0)],
        # top
        [(-w, -d, h), (w, -d, h), (w, d, h), (-w, d, h)],
        # front (y = -d)
        [(-w, -d, 0), (w, -d, 0), (w, -d, h), (-w, -d, h)],
        # back  (y = +d)
        [(w, d, 0), (-w, d, 0), (-w, d, h), (w, d, h)],
        # left  (x = -w)
        [(-w, d, 0), (-w, -d, 0), (-w, -d, h), (-w, d, h)],
        # right (x = +w)
        [(w, -d, 0), (w, d, 0), (w, d, h), (w, -d, h)],
    ]

    tris = GeomTriangles(Geom.UH_static)
    vi = 0
    for face in faces:
        for x, y, z in face:
            vertex.add_data3(x, y, z)
            colour.add_data4(r, g, b, a)
        # two triangles per quad
        tris.add_vertices(vi, vi + 1, vi + 2)
        tris.add_vertices(vi, vi + 2, vi + 3)
        vi += 4

    geom = Geom(vdata)
    geom.add_primitive(tris)

    node = GeomNode(name)
    node.add_geom(geom)

    return NodePath(node)


def make_flat_quad(
    name: str,
    w: float,
    d: float,
    color: tuple[float, float, float, float],
) -> NodePath:
    """Flat XY quad at Z=0, centred, w×d."""
    return make_box(name, w / 2, d / 2, 0.001, color)

