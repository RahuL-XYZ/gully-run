"""
police.py
Police pursuer avatar: stylized caricature of the pursuer in signature navy suit,
long red tie, and voluminous golden blonde swept hair, with flashing emergency sirens.
"""
from __future__ import annotations

import math
from panda3d.core import NodePath

from . import constants as C
from .utils import make_box, lerp, clamp


class Police:
    """
    Visible pursuer situated directly behind the runner.
    Stylized caricature in navy suit, iconic long red tie, and swooped blonde hair.
    Features alternating emergency sirens and lane-tracking pursuer logic.
    """

    HALF_W = 0.60
    HALF_D = 0.55
    HEIGHT = 1.75

    def __init__(self, parent: NodePath, player_y: float, player_x: float = 0.0) -> None:
        self.root = NodePath("police_root")
        self.root.reparent_to(parent)

        self._build_pursuer()

        self.x = player_x
        self.y = player_y - C.POLICE_BEHIND_DIST
        self.root.set_pos(self.x, self.y, 0)
        self._siren_timer = 0.0
        self._anim_phase = 0.0

    def _build_pursuer(self) -> None:
        """Construct the stylized caricature pursuer."""
        # 1. Dress Shoes
        for sx in (-0.20, 0.20):
            shoe = make_box(f"p_shoe_{sx}", 0.15, 0.30, 0.18, (0.05, 0.05, 0.08, 1.0))
            shoe.reparent_to(self.root)
            shoe.set_pos(sx, 0.05, 0.0)

        # 2. Navy Blue Suit Trousers
        for lx in (-0.20, 0.20):
            leg = make_box(f"p_leg_{lx}", 0.16, 0.20, 0.50, C.COL_TRUMP_SUIT)
            leg.reparent_to(self.root)
            leg.set_pos(lx, 0, 0.18)

        # 3. Navy Blue Suit Jacket Torso
        jacket = make_box("suit_jacket", 0.44, 0.30, 0.68, C.COL_TRUMP_SUIT)
        jacket.reparent_to(self.root)
        jacket.set_pos(0, 0, 0.65)

        # 4. White Dress Shirt V-opening
        shirt = make_box("dress_shirt", 0.18, 0.04, 0.45, C.COL_TRUMP_SHIRT)
        shirt.reparent_to(self.root)
        shirt.set_pos(0, -0.28, 0.82)

        # 5. Iconic Long Bright Red Necktie (Hanging down front)
        tie = make_box("red_tie", 0.08, 0.05, 0.52, C.COL_TRUMP_TIE)
        tie.reparent_to(self.root)
        tie.set_pos(0, -0.31, 0.68)

        # 6. Head
        head = make_box("pursuer_head", 0.32, 0.28, 0.38, C.COL_SKIN_BRIGHT)
        head.reparent_to(self.root)
        head.set_pos(0, 0, 1.35)

        # 7. Signature Golden Blonde Swept Hairstyle (Large voluminous front swoop)
        hair_top = make_box("hair_top", 0.35, 0.32, 0.16, C.COL_TRUMP_HAIR)
        hair_top.reparent_to(self.root)
        hair_top.set_pos(0, -0.02, 1.68)

        hair_swoop = make_box("hair_swoop", 0.34, 0.14, 0.15, C.COL_TRUMP_HAIR)
        hair_swoop.reparent_to(self.root)
        hair_swoop.set_pos(-0.04, -0.24, 1.64)

        hair_side = make_box("hair_side", 0.35, 0.16, 0.22, C.COL_TRUMP_HAIR)
        hair_side.reparent_to(self.root)
        hair_side.set_pos(0, 0.18, 1.48)

        # 8. Suit Arms (stored for chase swing animation)
        self.arm_left = make_box("p_arm_l", 0.14, 0.16, 0.58, C.COL_TRUMP_SUIT)
        self.arm_left.reparent_to(self.root)
        self.arm_left.set_pos(-0.52, 0, 0.72)

        self.arm_right = make_box("p_arm_r", 0.14, 0.16, 0.58, C.COL_TRUMP_SUIT)
        self.arm_right.reparent_to(self.root)
        self.arm_right.set_pos(0.52, 0, 0.72)

        # 9. Shoulder-mounted Dual Emergency Flashing Siren
        siren_mount = make_box("siren_mount", 0.28, 0.12, 0.08, (0.1, 0.1, 0.1, 1.0))
        siren_mount.reparent_to(self.root)
        siren_mount.set_pos(0, -0.15, 1.80)

        self.siren_left = make_box("siren_l", 0.11, 0.11, 0.15, C.COL_POLICE_SIREN_A)
        self.siren_left.reparent_to(self.root)
        self.siren_left.set_pos(-0.16, -0.15, 1.88)

        self.siren_right = make_box("siren_r", 0.11, 0.11, 0.15, C.COL_POLICE_SIREN_B)
        self.siren_right.reparent_to(self.root)
        self.siren_right.set_pos(0.16, -0.15, 1.88)

    def update(self, dt: float, player_y: float, player_x: float) -> None:
        # Alternating siren flash effect
        self._siren_timer += dt * 10.0
        if int(self._siren_timer) % 2 == 0:
            self.siren_left.set_color_scale(2.2, 0.8, 0.8, 1.0)
            self.siren_right.set_color_scale(0.3, 0.3, 0.6, 1.0)
        else:
            self.siren_left.set_color_scale(0.5, 0.3, 0.3, 1.0)
            self.siren_right.set_color_scale(0.8, 0.8, 2.5, 1.0)

        # Pursuer running arm swing animation
        self._anim_phase += dt * 14.0
        swing = math.sin(self._anim_phase) * 0.25
        self.arm_left.set_pos(-0.52, swing, 0.72)
        self.arm_right.set_pos(0.52, -swing, 0.72)

        # Smoothly track player along X with pursuer reaction delay
        self.x = lerp(self.x, player_x, clamp(7.0 * dt, 0.0, 1.0))

        # Maintain dramatic chase distance right behind the player in camera frame
        target_y = player_y - C.POLICE_BEHIND_DIST
        self.y = lerp(self.y, target_y, clamp(10.0 * dt, 0.0, 1.0))

        self.root.set_pos(self.x, self.y, 0)

    def catch_player(self, player_y: float, dt: float) -> None:
        """Surge forward to catch the runner on game over."""
        self.y = lerp(self.y, player_y - 0.45, clamp(12.0 * dt, 0.0, 1.0))
        # Arms reach forward
        self.arm_left.set_pos(-0.52, 0.35, 0.80)
        self.arm_right.set_pos(0.52, 0.35, 0.80)
        self.root.set_y(self.y)

    def distance_to_player(self, player_y: float) -> float:
        return player_y - self.y
