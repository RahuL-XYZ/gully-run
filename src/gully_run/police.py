"""
police.py
Police pursuer avatar: chases right behind the player in full view of the camera
with flashing emergency sirens and reactive lane tracking.
"""
from __future__ import annotations

import math
from panda3d.core import NodePath

from . import constants as C
from .utils import make_box, lerp, clamp


class Police:
    """
    Visible police pursuer situated directly behind the runner.
    Follows the player's lane with realistic reaction lag and features
    alternating red/blue emergency siren lightbars.
    """

    HALF_W = 0.65
    HALF_D = 0.60
    HEIGHT = 1.70

    def __init__(self, parent: NodePath, player_y: float, player_x: float = 0.0) -> None:
        self.root = NodePath("police_root")
        self.root.reparent_to(parent)

        self._build_pursuer()

        self.x = player_x
        self.y = player_y - C.POLICE_BEHIND_DIST
        self.root.set_pos(self.x, self.y, 0)
        self._siren_timer = 0.0

    def _build_pursuer(self) -> None:
        """Construct a stylized police officer / chase vehicle with siren."""
        # Main uniform / vehicle body
        body = make_box("police_body", self.HALF_W, self.HALF_D, 1.25, C.COL_POLICE)
        body.reparent_to(self.root)
        body.set_pos(0, 0, 0)

        # Upper visor / cap
        cap = make_box("police_cap", 0.50, 0.45, 0.40, (0.12, 0.12, 0.20, 1.0))
        cap.reparent_to(self.root)
        cap.set_pos(0, 0, 1.25)

        # Dual flashing siren bar (Left = Red, Right = Blue)
        self.siren_left = make_box("siren_l", 0.22, 0.18, 0.22, C.COL_POLICE_SIREN_A)
        self.siren_left.reparent_to(self.root)
        self.siren_left.set_pos(-0.30, 0, 1.65)

        self.siren_right = make_box("siren_r", 0.22, 0.18, 0.22, C.COL_POLICE_SIREN_B)
        self.siren_right.reparent_to(self.root)
        self.siren_right.set_pos(0.30, 0, 1.65)

    def update(self, dt: float, player_y: float, player_x: float) -> None:
        # Alternating siren flash effect
        self._siren_timer += dt * 10.0
        if int(self._siren_timer) % 2 == 0:
            self.siren_left.set_color_scale(2.0, 1.0, 1.0, 1.0)
            self.siren_right.set_color_scale(0.3, 0.3, 0.6, 1.0)
        else:
            self.siren_left.set_color_scale(0.6, 0.3, 0.3, 1.0)
            self.siren_right.set_color_scale(1.0, 1.0, 2.5, 1.0)

        # Smoothly track player along X with pursuer reaction delay
        self.x = lerp(self.x, player_x, clamp(7.0 * dt, 0.0, 1.0))

        # Maintain dramatic chase distance right behind the player in camera frame
        target_y = player_y - C.POLICE_BEHIND_DIST
        self.y = lerp(self.y, target_y, clamp(10.0 * dt, 0.0, 1.0))

        self.root.set_pos(self.x, self.y, 0)

    def catch_player(self, player_y: float, dt: float) -> None:
        """Surge forward to tackle/catch player on game over."""
        self.y = lerp(self.y, player_y - 0.4, clamp(12.0 * dt, 0.0, 1.0))
        self.root.set_y(self.y)

    def distance_to_player(self, player_y: float) -> float:
        return player_y - self.y
