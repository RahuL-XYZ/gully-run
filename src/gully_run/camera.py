"""
camera.py
Third-person follow camera tracking the player and pursuer down the Indian market streets.
"""
from __future__ import annotations

from panda3d.core import NodePath

from . import constants as C
from .utils import lerp, clamp


class FollowCamera:
    """
    Smooth third-person chase camera.
    Maintains a cinematic angle behind the player that keeps both the
    runner and the pursuing police vehicle clearly visible in frame.
    """

    def __init__(self, camera: NodePath, player_root: NodePath) -> None:
        self._cam = camera
        self._player = player_root

        # Initial positioning
        px = player_root.get_x()
        py = player_root.get_y()
        pz = player_root.get_z()

        self._cam.set_pos(px * 0.6, py + C.CAM_OFFSET_Y, pz + C.CAM_OFFSET_Z)
        self._cam.set_p(C.CAM_PITCH)

    def update(self, dt: float) -> None:
        px = self._player.get_x()
        py = self._player.get_y()
        pz = self._player.get_z()

        # Follow targets
        target_x = px * 0.65  # Slight lag behind lane changes for cinematic feel
        target_y = py + C.CAM_OFFSET_Y
        target_z = pz * 0.45 + C.CAM_OFFSET_Z

        lerp_rate = clamp(C.CAM_SMOOTH * dt, 0.0, 1.0)
        cx = lerp(self._cam.get_x(), target_x, lerp_rate)
        cy = lerp(self._cam.get_y(), target_y, lerp_rate)
        cz = lerp(self._cam.get_z(), target_z, lerp_rate)

        self._cam.set_pos(cx, cy, cz)

        # Look down the street ahead of player
        look_target_x = px * 0.4
        look_target_y = py + 7.5
        look_target_z = 1.1 + (pz * 0.3)
        self._cam.look_at(look_target_x, look_target_y, look_target_z)
