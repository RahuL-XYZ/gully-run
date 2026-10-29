"""
police.py
A magenta police-pursuer box that chases the player.
"""
from __future__ import annotations

from panda3d.core import NodePath

from . import constants as C
from .utils import make_box, lerp


class Police:
    """
    Visible pursuer behind the player.
    Slowly closes the gap to create urgency.
    """

    HALF_W = 0.6
    HALF_D = 0.6

    def __init__(self, render: NodePath, player_y: float) -> None:
        self.node = make_box("police", self.HALF_W, self.HALF_D, 1.6, C.COL_POLICE)
        self.node.reparent_to(render)
        self._y = player_y - C.POLICE_BEHIND_DIST
        self.node.set_pos(0, self._y, 0)

    def update(self, dt: float, player_y: float, player_speed: float) -> None:
        # Police accelerates a tiny bit faster than the player
        police_speed = player_speed * 1.05
        self._y += police_speed * dt
        # Smooth chase
        target_y = player_y - C.POLICE_BEHIND_DIST
        self._y = lerp(self._y, target_y, 0.02)
        self.node.set_y(self._y)

    def distance_to_player(self, player_y: float) -> float:
        return player_y - self._y

