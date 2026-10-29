"""
road.py
Builds and scrolls the endless road, lane markings, curbs and bustling Indian market street scenery:
chai stalls, auto-rickshaws, multi-story buildings, overhead festive garlands, and sidewalk lamp posts.
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
    w = random.uniform(4.0, 6.5)
    d = random.uniform(6.0, 10.0)
    h = random.uniform(9.0, 24.0)
    col = random.choice([C.COL_BUILDING_A, C.COL_BUILDING_B])

    root = NodePath("building_group")
    root.reparent_to(parent)

    # Base structure
    box = make_box("building_main", w / 2, d / 2, h, col)
    box.reparent_to(root)

    # Lateral offset outside road curb
    edge_x = x_sign * (C.ROAD_WIDTH / 2 + w / 2 + random.uniform(1.0, 2.8))
    root.set_pos(edge_x, 0, 0)

    # Rooftop / facade neon billboard strip
    neon_col = random.choice([C.COL_NEON_CYAN, C.COL_NEON_MAG])
    neon_strip = make_box("neon_sign", w / 2 + 0.1, 0.25, 0.6, neon_col)
    neon_strip.reparent_to(root)
    neon_strip.set_pos(0, 0, h - 0.4)

    # Balcony ledges
    for floor_z in range(4, int(h) - 2, 4):
        balcony = make_box("balcony", w / 2 - 0.4, 0.35, 0.20, (0.2, 0.2, 0.24, 1.0))
        balcony.reparent_to(root)
        balcony.set_pos(0, -x_sign * (d / 2 + 0.15), float(floor_z))

    return root


def _make_chai_stall(parent: NodePath, x_sign: int) -> NodePath:
    """Roadside Indian chai tapri (tea stall) with counter, warm awning, and signboard."""
    root = NodePath("chai_stall")
    root.reparent_to(parent)
    edge_x = x_sign * (C.ROAD_WIDTH / 2 + 1.8)
    root.set_pos(edge_x, 0, 0)

    # Counter base
    counter = make_box("counter", 1.3, 0.9, 1.2, C.COL_CHAI)
    counter.reparent_to(root)

    # Chai kettle placeholder
    kettle = make_box("kettle", 0.22, 0.22, 0.35, (0.85, 0.85, 0.90, 1.0))
    kettle.reparent_to(root)
    kettle.set_pos(0.4, 0, 1.25)

    # Corner pillars
    for px in (-1.2, 1.2):
        for py in (-0.8, 0.8):
            pillar = make_box("pillar", 0.06, 0.06, 2.3, (0.32, 0.26, 0.22, 1.0))
            pillar.reparent_to(root)
            pillar.set_pos(px, py, 0)

    # Overhead slanted awning
    awning = make_box("awning", 1.5, 1.15, 0.15, C.COL_NEON_MAG)
    awning.reparent_to(root)
    awning.set_pos(0, 0, 2.3)

    # Chai & Samosa signboard
    board = make_box("board", 1.2, 0.08, 0.38, (0.95, 0.85, 0.15, 1.0))
    board.reparent_to(root)
    board.set_pos(0, -x_sign * 0.95, 2.45)

    return root


def _make_rickshaw(parent: NodePath, x_sign: int) -> NodePath:
    """Parked classic green & yellow Indian auto-rickshaw with wheels and headlights."""
    root = NodePath("rickshaw")
    root.reparent_to(parent)
    edge_x = x_sign * (C.ROAD_WIDTH / 2 + 2.0)
    root.set_pos(edge_x, 0, 0)

    # 3 Black Rubber Wheels
    wheel_col = (0.12, 0.12, 0.14, 1.0)
    # Front center wheel
    wf = make_box("w_front", 0.15, 0.32, 0.35, wheel_col)
    wf.reparent_to(root)
    wf.set_pos(0, -1.2, 0.0)

    # Rear two wheels
    for wx in (-0.75, 0.75):
        wr = make_box(f"w_rear_{wx}", 0.15, 0.32, 0.35, wheel_col)
        wr.reparent_to(root)
        wr.set_pos(wx, 0.8, 0.0)

    # Lower body (dark green)
    lower = make_box("rick_lower", 0.82, 1.4, 0.75, C.COL_RICK_GREEN)
    lower.reparent_to(root)
    lower.set_pos(0, 0, 0.28)

    # Roof canopy (bright yellow)
    roof = make_box("rick_roof", 0.84, 1.3, 0.65, C.COL_RICK_YELLOW)
    roof.reparent_to(root)
    roof.set_pos(0, 0, 1.05)

    # Front windshield glass
    glass = make_box("windshield", 0.76, 0.06, 0.50, (0.1, 0.7, 0.9, 0.8))
    glass.reparent_to(root)
    glass.set_pos(0, -0.9, 1.05)

    # Bright headlight
    hl = make_box("rick_hl", 0.22, 0.10, 0.22, (0.98, 0.95, 0.40, 1.0))
    hl.reparent_to(root)
    hl.set_pos(0, -1.45, 0.55)

    return root


def _make_street_lamp(parent: NodePath, x_sign: int) -> NodePath:
    """Sidewalk street lamp post with glowing lantern."""
    root = NodePath("lamp_post")
    root.reparent_to(parent)
    edge_x = x_sign * (C.ROAD_WIDTH / 2 + 0.6)
    root.set_pos(edge_x, 0, 0)

    # Tall vertical pole
    pole = make_box("pole", 0.07, 0.07, 4.2, (0.25, 0.25, 0.30, 1.0))
    pole.reparent_to(root)
    pole.set_pos(0, 0, 0)

    # Horizontal arm reaching slightly over the curb
    arm = make_box("lamp_arm", 0.45, 0.06, 0.06, (0.25, 0.25, 0.30, 1.0))
    arm.reparent_to(root)
    arm.set_pos(-x_sign * 0.40, 0, 4.15)

    # Glowing lantern
    lantern = make_box("lantern", 0.18, 0.18, 0.28, (0.98, 0.88, 0.30, 1.0))
    lantern.reparent_to(root)
    lantern.set_pos(-x_sign * 0.80, 0, 3.90)

    return root


def _make_overhead_garland(parent: NodePath, y_pos: float) -> NodePath:
    """Festive market garland banner stretching across all 3 road lanes."""
    root = NodePath("overhead_banner")
    root.reparent_to(parent)
    root.set_pos(0, y_pos, 0)

    span_half_w = C.ROAD_WIDTH / 2 + 1.2

    # Left and right anchor poles
    for px in (-span_half_w, span_half_w):
        pole = make_box(f"banner_pole_{px}", 0.08, 0.08, 5.0, (0.3, 0.3, 0.35, 1.0))
        pole.reparent_to(root)
        pole.set_pos(px, 0, 0)

    # Overhead wire cable
    wire = make_box("wire", span_half_w, 0.04, 0.04, (0.2, 0.2, 0.2, 1.0))
    wire.reparent_to(root)
    wire.set_pos(0, 0, 4.8)

    # Hanging colorful pennants / bunting flags
    flag_colors = [
        (0.95, 0.30, 0.10, 1.0),  # Saffron
        (0.10, 0.85, 0.95, 1.0),  # Cyan
        (0.95, 0.15, 0.70, 1.0),  # Magenta
        (0.95, 0.85, 0.15, 1.0),  # Yellow
    ]
    step = 1.4
    x = -span_half_w + step
    i = 0
    while x < span_half_w - 0.5:
        col = flag_colors[i % len(flag_colors)]
        flag = make_box(f"flag_{i}", 0.25, 0.02, 0.40, col)
        flag.reparent_to(root)
        flag.set_pos(x, 0, 4.4)
        x += step
        i += 1

    return root


# ---------------------------------------------------------------------------
# RoadManager
# ---------------------------------------------------------------------------

class RoadManager:
    """
    Manages an endless scrolling road built from tiled modular segments.
    Recycles segments behind the player and constructs asphalt, curbs,
    divider lane markings, overhead garlands, and bustling roadside scenery.
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

        # Sidewalk street lamps (spaced along segment)
        for side in (-1, 1):
            lamp = _make_street_lamp(parent, side)
            lamp.set_y(-L / 4)
            lamp2 = _make_street_lamp(parent, side)
            lamp2.set_y(L / 4)

        # Scenery placement on both flanks
        scenery_pool = [_make_building, _make_chai_stall, _make_rickshaw]
        for side in (-1, 1):
            for _ in range(2):
                builder = random.choice(scenery_pool)
                item = builder(parent, side)
                item.set_y(random.uniform(-L / 2.4, L / 2.4))

        # Overhead festive banner crossing the street (1 per segment)
        _make_overhead_garland(parent, random.uniform(-L / 3, L / 3))

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
