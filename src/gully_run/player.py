"""
player.py
Player runner avatar: stylized character with responsive lane switching and jump mechanics.
"""
from __future__ import annotations

import math
from panda3d.core import NodePath

from . import constants as C
from .utils import make_box, lerp, clamp


class Player:
    """
    Player character controller:
    - Automatic forward running speed with gradual acceleration
    - Responsive 3-lane lateral switching with smooth interpolation
    - Realistic jump arc with gravity
    - Running stride bob animation
    - Bounding footprint for collision detection
    """

    HALF_W  = 0.55
    HALF_D  = 0.50
    HEIGHT  = 1.70

    def __init__(self, parent: NodePath) -> None:
        self.root = NodePath("player_root")
        self.root.reparent_to(parent)

        # Visual assembly
        self._build_avatar()

        self.lane: int = C.PLAYER_START_LANE
        self.target_x: float = C.LANE_X[self.lane]
        self.y: float = 0.0
        self.z: float = 0.0
        self.vel_z: float = 0.0

        self._run_speed = C.PLAYER_RUN_SPEED
        self._speed_timer = 0.0
        self._anim_phase = 0.0

        self.root.set_pos(self.target_x, self.y, self.z)

    def _build_avatar(self) -> None:
        """Construct a stylized futuristic desi street runner avatar."""
        # Legs / Shoes base
        shoes = make_box("player_shoes", 0.42, 0.35, 0.4, (0.1, 0.1, 0.15, 1.0))
        shoes.reparent_to(self.root)
        shoes.set_pos(0, 0, 0)

        # Torso / jacket (Neon Cyan)
        torso = make_box("player_torso", 0.45, 0.38, 0.75, C.COL_PLAYER)
        torso.reparent_to(self.root)
        torso.set_pos(0, 0, 0.4)

        # Head / Cap placeholder
        head = make_box("player_head", 0.30, 0.30, 0.50, (0.95, 0.75, 0.55, 1.0))
        head.reparent_to(self.root)
        head.set_pos(0, 0, 1.15)

        # Neon headband / scarf (Neon Magenta)
        band = make_box("player_headband", 0.32, 0.32, 0.12, C.COL_NEON_MAG)
        band.reparent_to(self.root)
        band.set_pos(0, 0, 1.48)

    # ---------------------------------------------------------------------- properties

    @property
    def pos(self) -> tuple[float, float, float]:
        return (self.root.get_x(), self.root.get_y(), self.root.get_z())

    @property
    def run_speed(self) -> float:
        return self._run_speed

    # ---------------------------------------------------------------------- controls

    def try_move_left(self) -> None:
        if self.lane > 0:
            self.lane -= 1
            self.target_x = C.LANE_X[self.lane]

    def try_move_right(self) -> None:
        if self.lane < C.NUM_LANES - 1:
            self.lane += 1
            self.target_x = C.LANE_X[self.lane]

    def try_jump(self) -> None:
        if self.z <= 0.02:  # Grounded check
            self.vel_z = C.JUMP_VELOCITY

    # ---------------------------------------------------------------------- update

    def update(self, dt: float) -> None:
        # Speed progression over time up to cap
        self._speed_timer += dt
        if self._speed_timer >= C.SPEED_UP_INTERVAL:
            self._speed_timer -= C.SPEED_UP_INTERVAL
            if self._run_speed < C.MAX_RUN_SPEED:
                self._run_speed += C.SPEED_INCREMENT

        # Forward displacement
        self.y += self._run_speed * dt

        # Smooth lane-change slide
        cur_x = self.root.get_x()
        new_x = lerp(cur_x, self.target_x, clamp(C.LANE_SWITCH_SPEED * dt, 0.0, 1.0))
        self.root.set_x(new_x)

        # Jump physics
        self.vel_z += C.GRAVITY * dt
        self.z += self.vel_z * dt
        if self.z <= 0.0:
            self.z = 0.0
            self.vel_z = 0.0

        # Running step bob animation when grounded
        bob = 0.0
        if self.z <= 0.01:
            self._anim_phase += dt * (self._run_speed * 1.2)
            bob = abs(math.sin(self._anim_phase)) * 0.12

        self.root.set_y(self.y)
        self.root.set_z(self.z + bob)
