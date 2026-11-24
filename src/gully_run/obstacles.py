"""
obstacles.py
Spawns and manages varied Indian street obstacles:
1. Low road barricades (can be jumped over with W / Space or dodged)
2. Tall market carts (must be dodged by switching lanes)
3. Overhead street barriers & scaffoldings (must be crouched/slid under with S or dodged)
"""
from __future__ import annotations

import random
from panda3d.core import NodePath

from . import constants as C
from .utils import make_box


class Obstacle:
    """A single roadside or lane obstacle."""

    KIND_LOW = "low"
    KIND_TALL = "tall"
    KIND_OVERHEAD = "overhead"

    def __init__(self, parent: NodePath, lane: int, y: float, kind: str) -> None:
        self.lane = lane
        self.y = y
        self.kind = kind
        self.x = C.LANE_X[lane]

        self.root = NodePath("obstacle_root")
        self.root.reparent_to(parent)
        self.root.set_pos(self.x, self.y, 0)

        if kind == self.KIND_TALL:
            # Tall market fruit cart / container (Must be dodged, cannot jump or crouch)
            self.half_w = 0.85
            self.half_d = 0.85
            self.height = 1.85
            self.clearance_z = 0.0

            cart = make_box("tall_cart", self.half_w, self.half_d, 1.4, C.COL_OBSTACLE_TALL)
            cart.reparent_to(self.root)
            cart.set_pos(0, 0, 0)

            canopy = make_box("cart_top", self.half_w + 0.1, self.half_d + 0.1, 0.45, (0.9, 0.8, 0.2, 1.0))
            canopy.reparent_to(self.root)
            canopy.set_pos(0, 0, 1.4)

        elif kind == self.KIND_OVERHEAD:
            # Overhead checkpoint height barrier (Must crouch / slide underneath with S)
            self.half_w = 1.15
            self.half_d = 0.40
            self.height = 2.40
            self.clearance_z = 1.05  # Opening underneath from 0.0 to 1.05m

            # Left & Right upright support pillars
            for px in (-self.half_w + 0.12, self.half_w - 0.12):
                post = make_box(f"post_{px}", 0.09, 0.09, 2.30, (0.28, 0.28, 0.32, 1.0))
                post.reparent_to(self.root)
                post.set_pos(px, 0, 0)

            # High horizontal crossbeam (Z = 1.05 to 1.75)
            beam = make_box(
                "overhead_beam",
                self.half_w - 0.02,
                0.22,
                0.55,
                C.COL_OBSTACLE_OVERHEAD,
            )
            beam.reparent_to(self.root)
            beam.set_pos(0, 0, 1.05)

            # Overhead hazard stripes / caution banner
            banner = make_box("caution_strip", self.half_w - 0.1, 0.08, 0.22, (0.1, 0.1, 0.12, 1.0))
            banner.reparent_to(self.root)
            banner.set_pos(0, -0.24, 1.22)

            # Top arch cap
            top_arch = make_box("top_arch", self.half_w, 0.12, 0.15, (0.85, 0.2, 0.15, 1.0))
            top_arch.reparent_to(self.root)
            top_arch.set_pos(0, 0, 2.15)

        else:
            # Low Indian police/road barrier (Can be jumped over with W / Space or dodged)
            self.half_w = 0.90
            self.half_d = 0.45
            self.height = 0.85
            self.clearance_z = 0.0

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

        # Obstacle variety: low (jump), overhead (crouch), tall (dodge)
        choices = [
            Obstacle.KIND_LOW,
            Obstacle.KIND_OVERHEAD,
            Obstacle.KIND_TALL,
            Obstacle.KIND_LOW,
            Obstacle.KIND_OVERHEAD,
        ]

        for lane in blocked_lanes:
            kind = random.choice(choices)
            self._obstacles.append(Obstacle(self._parent, lane, y, kind))

    def check_collision(self, player) -> bool:
        """
        Precise 3D Axis-Aligned Bounding Box (AABB) intersection check.
        Considers player jumping, standing, and crouching states against
        low barricades, tall carts, and overhead crouch barriers.
        """
        px = player.root.get_x()
        py = player.root.get_y()
        pz = player.z  # Ground clearance height

        # Player effective height based on crouch/stand state
        player_head_z = pz + (C.PLAYER_CROUCH_HEIGHT if player.is_crouching else C.PLAYER_STAND_HEIGHT)

        for obs in self._obstacles:
            dx = abs(px - obs.x)
            dy = abs(py - obs.y)

            # Lateral and longitudinal overlap tolerance
            if dx < (player.HALF_W + obs.half_w - 0.12) and dy < (player.HALF_D + obs.half_d - 0.15):

                if obs.kind == Obstacle.KIND_LOW:
                    # Low barricade: jump over clears it
                    if pz >= obs.height - 0.10:
                        continue
                    return True

                elif obs.kind == Obstacle.KIND_OVERHEAD:
                    # Overhead barrier: crossbeam spans from obs.clearance_z up to obs.height.
                    # If player crouches underneath (player_head_z < clearance_z) and isn't jumping high, clears!
                    if player.is_crouching and player_head_z <= obs.clearance_z + 0.05 and pz <= 0.15:
                        continue
                    # Otherwise standing or jumping collides with the overhead bar!
                    return True

                else:
                    # Tall obstacle: cannot jump over or crouch under
                    return True

        return False
