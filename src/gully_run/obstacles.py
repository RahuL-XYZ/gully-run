"""
obstacles.py
Spawns and manages coloured box obstacles on the road.
"""
from __future__ import annotations

import random

from panda3d.core import NodePath

from . import constants as C
from .utils import make_box


# Obstacle half-extents (approx same as player to keep test fair)
OBS_HW = 0.9
OBS_HD = 0.9
OBS_H  = 1.6


class Obstacle:
    """A single obstacle on the road."""

    def __init__(self, render: NodePath, lane: int, y: float) -> None:
        self.lane = lane
        self.y    = y
        color = random.choice([C.COL_OBSTACLE, C.COL_NEON_MAG, (0.6, 0.6, 0.6, 1)])
        self.node = make_box("obstacle", OBS_HW, OBS_HD, OBS_H, color)
        self.node.reparent_to(render)
        self.node.set_pos(C.LANE_X[lane], y, 0)

    def remove(self) -> None:
        self.node.remove_node()


class ObstacleManager:
    """Spawns obstacles ahead of the player and culls those left behind."""

    def __init__(self, render: NodePath) -> None:
        self._render = render
        self._obstacles: list[Obstacle] = []
        self._last_spawn_y: float = 0.0

    def update(self, player_y: float) -> None:
        spawn_y = player_y + C.OBSTACLE_SPAWN_DIST

        # Spawn new cluster when far enough from last
        while spawn_y - self._last_spawn_y >= C.OBSTACLE_MIN_GAP:
            self._last_spawn_y += C.OBSTACLE_MIN_GAP
            self._spawn_cluster(self._last_spawn_y)

        # Cull obstacles far behind
        alive = []
        for obs in self._obstacles:
            if obs.y < player_y - 10.0:
                obs.remove()
            else:
                alive.append(obs)
        self._obstacles = alive

    def _spawn_cluster(self, y: float) -> None:
        """Block 1 or 2 lanes, always leaving at least 1 free."""
        lanes = list(range(C.NUM_LANES))
        n_blocked = random.randint(1, C.OBSTACLE_MAX_PER_ROW)
        blocked = random.sample(lanes, n_blocked)
        for lane in blocked:
            self._obstacles.append(Obstacle(self._render, lane, y))

    def check_collision(self, player) -> bool:
        """AABB overlap test between player and every obstacle."""
        px = player.node.get_x()
        py = player.node.get_y()
        pz = player.node.get_z()

        for obs in self._obstacles:
            dx = abs(px - obs.node.get_x())
            dy = abs(py - obs.y)
            dz = pz  # player bottom is at pz, obs bottom is at 0

            if (dx < player.HALF_W + OBS_HW - 0.15
                    and dy < player.HALF_D + OBS_HD - 0.15
                    and dz < OBS_H):   # player's feet must be below top of obstacle
                return True
        return False

