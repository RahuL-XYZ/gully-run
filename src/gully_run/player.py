"""
player.py
Player avatar: a cyan box that runs forward, slides between lanes and jumps.
"""
from __future__ import annotations

from panda3d.core import NodePath

from . import constants as C
from .utils import make_box, lerp, clamp


class Player:
    """
    Wraps the player NodePath and handles:
    - Automatic forward movement
    - Lateral lane switching
    - Jump physics
    - Collision footprint (bounding box query)
    """

    # Approximate half-extents for overlap tests
    HALF_W = 0.6
    HALF_D = 0.6
    HEIGHT  = 1.5

    def __init__(self, render: NodePath) -> None:
        self._render = render

        self.node = make_box("player", self.HALF_W, self.HALF_D, self.HEIGHT, C.COL_PLAYER)
        self.node.reparent_to(render)

        self.lane: int   = C.PLAYER_START_LANE
        self.target_x: float = C.LANE_X[self.lane]
        self.y: float    = 0.0
        self.z: float    = 0.0    # height above road
        self.vel_z: float = 0.0   # vertical velocity

        self._run_speed = C.PLAYER_RUN_SPEED
        self._speed_timer = 0.0

        self.node.set_pos(self.target_x, self.y, self.z)

    # ---------------------------------------------------------------------- properties

    @property
    def pos(self) -> tuple[float, float, float]:
        return (self.node.get_x(), self.node.get_y(), self.node.get_z())

    @property
    def run_speed(self) -> float:
        return self._run_speed

    # ---------------------------------------------------------------------- input

    def try_move_left(self) -> None:
        if self.lane > 0:
            self.lane -= 1
            self.target_x = C.LANE_X[self.lane]

    def try_move_right(self) -> None:
        if self.lane < C.NUM_LANES - 1:
            self.lane += 1
            self.target_x = C.LANE_X[self.lane]

    def try_jump(self) -> None:
        if self.z <= 0.01:          # only jump when grounded
            self.vel_z = C.JUMP_VELOCITY

    # ---------------------------------------------------------------------- update

    def update(self, dt: float) -> None:
        # Speed ramp-up
        self._speed_timer += dt
        if self._speed_timer >= C.SPEED_UP_INTERVAL:
            self._speed_timer -= C.SPEED_UP_INTERVAL
            self._run_speed += C.SPEED_INCREMENT

        # Forward movement
        self.y += self._run_speed * dt

        # Lateral slide
        cur_x = self.node.get_x()
        new_x = lerp(cur_x, self.target_x, clamp(C.LANE_SWITCH_SPEED * dt, 0.0, 1.0))
        self.node.set_x(new_x)

        # Vertical (jump / gravity)
        self.vel_z += C.GRAVITY * dt
        self.z += self.vel_z * dt
        if self.z <= 0.0:
            self.z = 0.0
            self.vel_z = 0.0

        self.node.set_y(self.y)
        self.node.set_z(self.z)

