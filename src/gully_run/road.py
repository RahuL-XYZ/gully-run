"""
road.py
Builds and scrolls the endless road, lane markings and street scenery.
"""
from __future__ import annotations

import random

from panda3d.core import NodePath, AmbientLight, DirectionalLight, LColor
from panda3d.core import LPoint3, LVector3

from . import constants as C
from .utils import make_box, make_flat_quad


# ---------------------------------------------------------------------------
# Street-side scenery helpers
# ---------------------------------------------------------------------------

def _make_building(parent: NodePath, x_sign: int) -> NodePath:
    """Spawn a random-height building on one side of the road."""
    w = random.uniform(3.0, 6.0)
    d = random.uniform(4.0, 8.0)
    h = random.uniform(6.0, 18.0)
    col = random.choice([C.COL_BUILDING_A, C.COL_BUILDING_B])

    box = make_box("building", w / 2, d / 2, h, col)
    edge_x = x_sign * (C.ROAD_WIDTH / 2 + w / 2 + random.uniform(0.5, 2.0))
    box.reparent_to(parent)
    box.set_pos(edge_x, 0, 0)

    # Neon accent strip on top
    neon_col = random.choice([C.COL_NEON_CYAN, C.COL_NEON_MAG])
    neon = make_box("neon", w / 2 + 0.1, 0.15, 0.3, neon_col)
    neon.reparent_to(box)
    neon.set_pos(0, 0, h - 0.15)

    return box


def _make_chai_stall(parent: NodePath, x_sign: int) -> NodePath:
    """Simple chai-stall placeholder (small coloured box + canopy)."""
    stall = make_box("chai_stall", 1.0, 0.8, 1.5, C.COL_CHAI)
    ex = x_sign * (C.ROAD_WIDTH / 2 + 1.2)
    stall.reparent_to(parent)
    stall.set_pos(ex, 0, 0)
    # canopy
    canopy = make_box("canopy", 1.3, 1.1, 0.15, C.COL_NEON_MAG)
    canopy.reparent_to(stall)
    canopy.set_pos(0, 0, 1.5)
    return stall


def _make_rickshaw(parent: NodePath, x_sign: int) -> NodePath:
    """Auto-rickshaw silhouette: boxy body + wheels."""
    body = make_box("rick_body", 1.0, 1.8, 1.4, C.COL_NEON_CYAN)
    ex = x_sign * (C.ROAD_WIDTH / 2 + 1.3)
    body.reparent_to(parent)
    body.set_pos(ex, 0, 0.4)
    return body


def _make_barricade(parent: NodePath) -> NodePath:
    """Road barricade – a wide flat slab near the road edge."""
    bar = make_box("barricade", C.ROAD_WIDTH / 2, 0.3, 0.8, C.COL_NEON_MAG)
    bar.reparent_to(parent)
    bar.set_pos(0, 0, 0)
    return bar


# ---------------------------------------------------------------------------
# RoadManager
# ---------------------------------------------------------------------------

class RoadManager:
    """
    Manages a pool of road segments that scroll backward as the player moves.
    Each segment contains the asphalt quad, lane markings, and scenery.
    """

    def __init__(self, render: NodePath) -> None:
        self._render = render
        self._segments: list[dict] = []   # list of {'node': NodePath, 'y': float}
        self._next_spawn_y: float = 0.0

        # Pre-create segments
        for i in range(C.NUM_SEGMENTS):
            self._spawn_segment(i * C.ROAD_SEGMENT_LEN)

    # ------------------------------------------------------------------ build

    def _build_segment(self, parent: NodePath) -> None:
        """Fill a segment node with road, markings and scenery geometry."""
        L = C.ROAD_SEGMENT_LEN

        # Asphalt
        road = make_flat_quad("road", C.ROAD_WIDTH, L, C.COL_ROAD)
        road.reparent_to(parent)

        # Lane markings  (dashed lines between lanes)
        dash_h = 2.0
        dash_gap = 2.0
        y = -L / 2
        while y < L / 2:
            for xi in [-C.LANE_WIDTH / 2, C.LANE_WIDTH / 2]:
                mark = make_flat_quad("mark", 0.12, dash_h, C.COL_LANE_MARK)
                mark.reparent_to(parent)
                mark.set_pos(xi, y + dash_h / 2, 0.002)
            y += dash_h + dash_gap

        # Road edge lines
        for xi in [-C.ROAD_WIDTH / 2, C.ROAD_WIDTH / 2]:
            edge = make_flat_quad("edge", 0.2, L, (0.8, 0.8, 0.8, 1))
            edge.reparent_to(parent)
            edge.set_pos(xi, 0, 0.002)

        # Scenery  (one set per segment, random)
        scenery_choices = [_make_building, _make_chai_stall, _make_rickshaw]
        for x_sign in (-1, 1):
            fn = random.choice(scenery_choices)
            s = fn(parent, x_sign)
            # spread along the segment
            s.set_y(s.get_y() + random.uniform(-L / 3, L / 3))

        # Occasionally add a barricade at very edge of road (decorative only)
        if random.random() < 0.3:
            b = _make_barricade(parent)
            b.set_y(random.uniform(-L / 3, L / 3))

    def _spawn_segment(self, y_center: float) -> None:
        node = NodePath(f"seg_{int(y_center)}")
        node.reparent_to(self._render)
        node.set_pos(0, y_center, 0)
        self._build_segment(node)
        self._segments.append({"node": node, "y": y_center})
        self._next_spawn_y = y_center + C.ROAD_SEGMENT_LEN

    # ----------------------------------------------------------------- update

    def update(self, player_y: float) -> None:
        """Recycle segments that have passed behind the camera."""
        # Spawn new segment when the furthest is getting close
        if self._next_spawn_y - player_y < C.NUM_SEGMENTS * C.ROAD_SEGMENT_LEN / 2:
            self._spawn_segment(self._next_spawn_y)

        # Remove segments too far behind
        cutoff = player_y - C.ROAD_SEGMENT_LEN * 1.5
        alive = []
        for seg in self._segments:
            if seg["y"] + C.ROAD_SEGMENT_LEN / 2 < cutoff:
                seg["node"].remove_node()
            else:
                alive.append(seg)
        self._segments = alive

