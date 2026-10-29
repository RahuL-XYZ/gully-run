"""
camera.py
Smooth third-person follow camera.
"""
from __future__ import annotations

from panda3d.core import NodePath, LPoint3

from . import constants as C
from .utils import lerp


class FollowCamera:
    """Smoothly tracks the player from behind and slightly above."""

    def __init__(self, camera: NodePath, player_node: NodePath) -> None:
        self._cam = camera
        self._player = player_node
        self._cam.set_p(C.CAM_PITCH)

    def update(self, dt: float) -> None:
        px, py, pz = (
            self._player.get_x(),
            self._player.get_y(),
            self._player.get_z(),
        )
        target_x = px
        target_y = py + C.CAM_OFFSET_Y
        target_z = pz + C.CAM_OFFSET_Z

        t = min(C.CAM_SMOOTH * dt, 1.0)
        cx = lerp(self._cam.get_x(), target_x, t)
        cy = lerp(self._cam.get_y(), target_y, t)
        cz = lerp(self._cam.get_z(), target_z, t)

        self._cam.set_pos(cx, cy, cz)
        self._cam.look_at(px, py + 5, pz + 0.75)

