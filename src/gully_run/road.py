"""
road.py
Builds and scrolls the endless road, lane markings, curbs and Indian market street scenery.
"""
from __future__ import annotations

import random
from panda3d.core import NodePath

from . import constants as C
from .utils import make_box, make_flat_quad


# ---------------------------------------------------------------------------
# Street-side scenery generators
# ---------------------------------------------------------------------------

def _make_building(parent: NodePath, x_sign: int) -> NodePath:
    """Multi-story Indian street shop/apartment building with neon sign accents."""
    w = random.uniform(3.5, 6.0)
    d = random.uniform(5.0, 9.0)
    h = random.uniform(8.0, 22.0)
    col = random.choice([C.COL_BUILDING_A, C.COL_BUILDING_B])

    root = NodePath("building_group")
    root.reparent_to(parent)

    # Base structure
    box = make_box("building_main", w / 2, d / 2, h, col)
    box.reparent_to(root)

    # Lateral offset outside road curb
    edge_x = x_sign * (C.ROAD_WIDTH / 2 + w / 2 + random.uniform(0.6, 2.5))
    root.set_pos(edge_x, 0, 0)

    # Rooftop / facade neon billboard strip
    neon_col = random.choice([C.COL_NEON_CYAN, C.COL_NEON_MAG])
    neon_strip = make_box("neon_sign", w / 2 + 0.1, 0.25, 0.6, neon_col)
    neon_strip.reparent_to(root)
    neon_strip.set_pos(0, 0, h - 0.4)

    # Window glow accent blocks
    if h > 10:
        win_col = (0.95, 0.75, 0.20, 1.0)
        win = make_box("window_light", 0.6, 0.15, 0.8, win_col)
        win.reparent_to(root)
        win.set_pos(-x_sign * (w / 2 - 0.2), 0, h * 0.5)

    return root


def _make_chai_stall(parent: NodePath, x_sign: int) -> NodePath:
    """Roadside Indian chai tapri (tea stall) with counter, warm awning and signboard."""
    root = NodePath("chai_stall")
    root.reparent_to(parent)
    edge_x = x_sign * (C.ROAD_WIDTH / 2 + 1.6)
    root.set_pos(edge_x, 0, 0)

    # Counter base
    counter = make_box("counter", 1.2, 0.9, 1.2, C.COL_CHAI)
    counter.reparent_to(root)

    # Corner pillars
    for px in (-1.1, 1.1):
        for py in (-0.8, 0.8):
            pillar = make_box("pillar", 0.06, 0.06, 2.2, (0.3, 0.25, 0.2, 1.0))
            pillar.reparent_to(root)
            pillar.set_pos(px, py, 0)

    # Overhead slanted awning
    awning = make_box("awning", 1.4, 1.1, 0.15, C.COL_NEON_MAG)
    awning.reparent_to(root)
    awning.set_pos(0, 0, 2.2)

    # Chai banner
    board = make_box("board", 1.1, 0.08, 0.35, (0.95, 0.85, 0.1, 1.0))
    board.reparent_to(root)
    board.set_pos(0, -x_sign * 0.95, 2.35)

    return root


def _make_rickshaw(parent: NodePath, x_sign: int) -> NodePath:
    """Parked classic green & yellow Indian auto-rickshaw."""
    root = NodePath("rickshaw")
    root.reparent_to(parent)
    edge_x = x_sign * (C.ROAD_WIDTH / 2 + 1.8)
    root.set_pos(edge_x, 0, 0)

    # Lower body (dark green)
    lower = make_box("rick_lower", 0.8, 1.4, 0.8, C.COL_RICK_GREEN)
    lower.reparent_to(root)
    lower.set_pos(0, 0, 0.2)

    # Roof canopy (bright yellow)
    roof = make_box("rick_roof", 0.82, 1.2, 0.6, C.COL_RICK_YELLOW)
    roof.reparent_to(root)
    roof.set_pos(0, 0, 1.0)

    # Windshield / headlight placeholder
    hl = make_box("rick_hl", 0.25, 0.1, 0.25, C.COL_NEON_CYAN)
    hl.reparent_to(root)
    hl.set_pos(0, -1.4, 0.5)

    return root


# ---------------------------------------------------------------------------
# RoadManager
# ---------------------------------------------------------------------------

class RoadManager:
    """
    Manages an endless scrolling road built from tiled modular segments.
    Recycles segments behind the player and constructs asphalt, curbs,
    divider lane markings, and bustling roadside scenery.
    """

    def __init__(self, render: NodePath) -> None:
        self._render = render
        self._segments: list[dict] = []
        self._next_spawn_y: float = 0.0

        for i in range(C.NUM_SEGMENTS):
            self._spawn_segment(i * C.ROAD_SEGMENT_LEN)

    # ------------------------------------------------------------------ build

    def _build_segment(self, parent: NodePath) -> None:
        L = C.ROAD_SEGMENT_LEN

        # Main road surface
        road = make_flat_quad("road_asphalt", C.ROAD_WIDTH, L, C.COL_ROAD, depth_offset=0)
        road.reparent_to(parent)

        # Raised curbs on road borders
        for xi in (-C.ROAD_WIDTH / 2 - 0.2, C.ROAD_WIDTH / 2 + 0.2):
            curb = make_box("curb", 0.2, L / 2, 0.18, C.COL_CURB)
            curb.reparent_to(parent)
            curb.set_pos(xi, 0, 0)

        # Dashed lane dividers (between lane 0-1 and lane 1-2)
        dash_len = 2.4
        dash_gap = 2.4
        divider_x_offsets = [-C.LANE_WIDTH / 2, C.LANE_WIDTH / 2]

        y = -L / 2
        while y < L / 2:
            for xi in divider_x_offsets:
                mark = make_flat_quad("lane_mark", 0.14, dash_len, C.COL_LANE_MARK, depth_offset=2)
                mark.reparent_to(parent)
                mark.set_pos(xi, y + dash_len / 2, 0.01)
            y += dash_len + dash_gap

        # Outer white road boundary lines
        for xi in (-C.ROAD_WIDTH / 2 + 0.1, C.ROAD_WIDTH / 2 - 0.1):
            line = make_flat_quad("border_line", 0.12, L, (0.85, 0.85, 0.85, 1.0), depth_offset=1)
            line.reparent_to(parent)
            line.set_pos(xi, 0, 0.01)

        # Sidewalk pedestrian pavement strips
        for side in (-1, 1):
            sidewalk = make_flat_quad(
                "sidewalk", 4.0, L, (0.16, 0.14, 0.18, 1.0), depth_offset=0
            )
            sidewalk.reparent_to(parent)
            sidewalk.set_pos(side * (C.ROAD_WIDTH / 2 + 2.2), 0, 0.05)

        # Scenery placement on both flanks
        scenery_pool = [_make_building, _make_chai_stall, _make_rickshaw]
        for side in (-1, 1):
            # 2 scenery items per side per segment for a rich crowded market look
            for _ in range(2):
                builder = random.choice(scenery_pool)
                item = builder(parent, side)
                item.set_y(random.uniform(-L / 2.3, L / 2.3))

    def _spawn_segment(self, y_center: float) -> None:
        node = NodePath(f"road_seg_{int(y_center)}")
        node.reparent_to(self._render)
        node.set_pos(0, y_center, 0)
        self._build_segment(node)
        self._segments.append({"node": node, "y": y_center})
        self._next_spawn_y = y_center + C.ROAD_SEGMENT_LEN

    # ----------------------------------------------------------------- update

    def update(self, player_y: float) -> None:
        """Spawn ahead and recycle passed segments."""
        if self._next_spawn_y - player_y < C.NUM_SEGMENTS * C.ROAD_SEGMENT_LEN * 0.6:
            self._spawn_segment(self._next_spawn_y)

        cutoff = player_y - C.ROAD_SEGMENT_LEN * 1.5
        alive = []
        for seg in self._segments:
            if seg["y"] + C.ROAD_SEGMENT_LEN / 2 < cutoff:
                seg["node"].remove_node()
            else:
                alive.append(seg)
        self._segments = alive
