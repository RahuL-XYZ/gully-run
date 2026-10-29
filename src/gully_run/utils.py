"""
utils.py
Helper functions and procedural 3D mesh generators for Gully Run.
"""
from __future__ import annotations

from panda3d.core import (
    GeomNode, Geom, GeomVertexFormat, GeomVertexData,
    GeomVertexWriter, GeomTriangles, NodePath,
)


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
    Build a solid colored axis-aligned 3D box geometry centered on X/Y,
    with its base at Z=0. Normals are generated for proper directional shading.

    w = half-extent in X (width / 2)
    d = half-extent in Y (depth / 2)
    h = full height in Z
    """
    fmt = GeomVertexFormat.get_v3n3c4()
    vdata = GeomVertexData(name, fmt, Geom.UH_static)
    vdata.set_num_rows(24)

    vertex = GeomVertexWriter(vdata, "vertex")
    normal = GeomVertexWriter(vdata, "normal")
    colour = GeomVertexWriter(vdata, "color")

    r, g, b, a = color

    # (face_vertices, face_normal)
    faces = [
        # Bottom (z = 0)
        ([(-w, -d, 0), (w, -d, 0), (w, d, 0), (-w, d, 0)], (0, 0, -1)),
        # Top (z = h)
        ([(-w, -d, h), (w, -d, h), (w, d, h), (-w, d, h)], (0, 0, 1)),
        # Front (-Y)
        ([(-w, -d, 0), (w, -d, 0), (w, -d, h), (-w, -d, h)], (0, -1, 0)),
        # Back (+Y)
        ([(w, d, 0), (-w, d, 0), (-w, d, h), (w, d, h)], (0, 1, 0)),
        # Left (-X)
        ([(-w, d, 0), (-w, -d, 0), (-w, -d, h), (-w, d, h)], (-1, 0, 0)),
        # Right (+X)
        ([(w, -d, 0), (w, d, 0), (w, d, h), (w, -d, h)], (1, 0, 0)),
    ]

    tris = GeomTriangles(Geom.UH_static)
    vi = 0
    for face_verts, (nx, ny, nz) in faces:
        for x, y, z in face_verts:
            vertex.add_data3(x, y, z)
            normal.add_data3(nx, ny, nz)
            colour.add_data4(r, g, b, a)
        # Two triangles per quad
        tris.add_vertices(vi, vi + 1, vi + 2)
        tris.add_vertices(vi, vi + 2, vi + 3)
        vi += 4

    geom = Geom(vdata)
    geom.add_primitive(tris)

    node = GeomNode(name)
    node.add_geom(geom)

    np = NodePath(node)
    np.set_two_sided(True)
    return np


def make_flat_quad(
    name: str,
    w: float,
    d: float,
    color: tuple[float, float, float, float],
    depth_offset: int = 0,
) -> NodePath:
    """Flat horizontal quad at Z=0, centered, w x d."""
    np = make_box(name, w / 2, d / 2, 0.005, color)
    if depth_offset != 0:
        np.set_depth_offset(depth_offset)
    return np
