"""
obstacles.py
Spawns and manages varied Indian street obstacles: low jumpable road barricades
and tall market carts that must be dodged by switching lanes.
"""
from __future__ import annotations

import random
from panda3d.core import NodePath

from . import constants as C
from .utils import make_box


class Obstacle:
    """A single roadside or lane obstacle."""

    def __init__(self, parent: NodePath, lane: int, y: float, is_tall: bool) -> None:
        self.lane = lane
        self.y = y
        self.is_tall = is_tall
        self.x = C.LANE_X[lane]

        self.root = NodePath("obstacle_root")
        self.root.reparent_to(parent)
        self.root.set_pos(self.x, self.y, 0)

        if is_tall:
            # Tall market fruit cart / container (Must be dodged, cannot jump over)
            self.half_w = 0.85
            self.half_d = 0.85
            self.height = 1.85

            cart = make_box("tall_cart", self.half_w, self.half_d, 1.4, C.COL_OBSTACLE_TALL)
            cart.reparent_to(self.root)
            cart.set_pos(0, 0, 0)

            # Cart canopy
            canopy = make_box("cart_top", self.half_w + 0.1, self.half_d + 0.1, 0.45, (0.9, 0.8, 0.2, 1.0))
            canopy.reparent_to(self.root)
            canopy.set_pos(0, 0, 1.4)
        else:
            # Low Indian police/road barrier (Can be jumped over with Spacebar or dodged)
            self.half_w = 0.90
            self.half_d = 0.45
            self.height = 0.85

            bar = make_box("low_barrier", self.half_w, self.half_d, self.height, C.COL_OBSTACLE_LOW)
            bar.reparent_to(self.root)
            bar.set_pos(0, 0, 0)

            # Hazard yellow stripe
            stripe = make_box("hazard_stripe", self.half_w + 0.02, 0.1, 0.25, (0.95, 0.90, 0.1, 1.0))
            stripe.reparent_to(self.root)
            stripe.set_pos(0, 0, 0.35)

    def remove(self) -> None:
        self.root.remove_node()


class ObstacleManager:
    """Spawns obstacles ahead of the player and culls those behind."""

    def __init__(self, parent: NodePath) -> None:
        self._parent = parent
        self._obstacles: list[Obstacle] = []
        self._last_spawn_y: float = C.OBSTACLE_START_Y

    def update(self, player_y: float) -> None:
        spawn_horizon = player_y + C.OBSTACLE_SPAWN_DIST

        # Spawn in intervals
        while spawn_horizon - self._last_spawn_y >= C.OBSTACLE_MIN_GAP:
            self._last_spawn_y += C.OBSTACLE_MIN_GAP
            self._spawn_row(self._last_spawn_y)

        # Remove obstacles left behind camera
        cutoff = player_y - 12.0
        alive = []
        for obs in self._obstacles:
            if obs.y < cutoff:
                obs.remove()
            else:
                alive.append(obs)
        self._obstacles = alive

    def _spawn_row(self, y: float) -> None:
        """Block 1 or 2 lanes, guaranteeing at least one open lane."""
        available_lanes = list(range(C.NUM_LANES))
        count_to_block = random.choice([1, 1, 2])  # 66% single lane, 33% double lane
        blocked_lanes = random.sample(available_lanes, count_to_block)

        for lane in blocked_lanes:
            is_tall = random.random() < 0.45  # 45% tall carts, 55% jumpable barriers
            self._obstacles.append(Obstacle(self._parent, lane, y, is_tall))

    def check_collision(self, player) -> bool:
        """
        Precise 3D Axis-Aligned Bounding Box (AABB) intersection check.
        Returns True if player overlaps with an obstacle.
        """
        px = player.root.get_x()
        py = player.root.get_y()
        pz = player.z  # Ground clearance height

        for obs in self._obstacles:
            dx = abs(px - obs.x)
            dy = abs(py - obs.y)

            # Lateral and longitudinal overlap tolerance
            if dx < (player.HALF_W + obs.half_w - 0.12) and dy < (player.HALF_D + obs.half_d - 0.15):
                # If player jumped above the obstacle, clear!
                if pz >= obs.height - 0.10:
                    continue
                return True

        return False
