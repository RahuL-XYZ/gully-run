"""
player.py
Player runner avatar: stylized caricature of the runner in signature kurta & saffron Nehru jacket,
with running arm swing, stride bobbing, and responsive 3-lane movement.
"""
from __future__ import annotations

import math
from panda3d.core import NodePath

from . import constants as C
from .utils import make_box, lerp, clamp


class Player:
    """
    Player character controller:
    - Stylized caricature with kurta, saffron Nehru jacket, spectacles, and white beard
    - Dynamic arm swing and footstep bobbing while sprinting
    - Automatic forward running speed with gradual acceleration
    - Responsive 3-lane lateral switching with smooth interpolation
    - Jump arc with gravity
    """

    HALF_W  = 0.55
    HALF_D  = 0.50
    HEIGHT  = 1.75

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
        """Construct the stylized caricature avatar."""
        # 1. Shoes / Mojaris
        for sx in (-0.18, 0.18):
            shoe = make_box(f"shoe_{sx}", 0.14, 0.28, 0.18, (0.22, 0.14, 0.10, 1.0))
            shoe.reparent_to(self.root)
            shoe.set_pos(sx, 0.04, 0.0)

        # 2. White Pajama / Lower Legs
        for lx in (-0.18, 0.18):
            leg = make_box(f"leg_{lx}", 0.15, 0.18, 0.45, C.COL_MODI_KURTA)
            leg.reparent_to(self.root)
            leg.set_pos(lx, 0, 0.18)

        # 3. White Kurta Body Base
        kurta = make_box("kurta_base", 0.38, 0.26, 0.85, C.COL_MODI_KURTA)
        kurta.reparent_to(self.root)
        kurta.set_pos(0, 0, 0.40)

        # 4. Signature Saffron Nehru Jacket / Modi Vest
        vest = make_box("nehru_vest", 0.40, 0.28, 0.65, C.COL_MODI_JACKET)
        vest.reparent_to(self.root)
        vest.set_pos(0, 0, 0.58)

        # Mandarin collar strip
        collar = make_box("vest_collar", 0.26, 0.22, 0.12, C.COL_MODI_JACKET)
        collar.reparent_to(self.root)
        collar.set_pos(0, 0, 1.22)

        # Pocket square / emblem accent
        pocket = make_box("vest_pocket", 0.08, 0.02, 0.08, (0.98, 0.98, 0.98, 1.0))
        pocket.reparent_to(self.root)
        pocket.set_pos(0.22, -0.29, 1.0)

        # 5. Head
        head = make_box("player_head", 0.28, 0.26, 0.38, C.COL_SKIN_INDIAN)
        head.reparent_to(self.root)
        head.set_pos(0, 0, 1.32)

        # 6. Signature Silver Hair (styled parted on top & back)
        hair = make_box("player_hair", 0.30, 0.28, 0.14, C.COL_MODI_HAIR)
        hair.reparent_to(self.root)
        hair.set_pos(0, 0.02, 1.62)

        hair_back = make_box("hair_back", 0.29, 0.10, 0.25, C.COL_MODI_HAIR)
        hair_back.reparent_to(self.root)
        hair_back.set_pos(0, 0.18, 1.45)

        # 7. Signature Silver-White Trimmed Beard & Moustache
        beard = make_box("player_beard", 0.26, 0.16, 0.22, C.COL_MODI_BEARD)
        beard.reparent_to(self.root)
        beard.set_pos(0, -0.16, 1.26)

        # 8. Golden Rimless Spectacles
        glasses_l = make_box("glass_l", 0.09, 0.04, 0.07, C.COL_MODI_GLASSES)
        glasses_l.reparent_to(self.root)
        glasses_l.set_pos(-0.13, -0.26, 1.50)

        glasses_r = make_box("glass_r", 0.09, 0.04, 0.07, C.COL_MODI_GLASSES)
        glasses_r.reparent_to(self.root)
        glasses_r.set_pos(0.13, -0.26, 1.50)

        bridge = make_box("glass_bridge", 0.06, 0.03, 0.02, C.COL_MODI_GLASSES)
        bridge.reparent_to(self.root)
        bridge.set_pos(0, -0.26, 1.51)

        # 9. Left & Right Arms (stored for running swing animation)
        self.arm_left = make_box("arm_l", 0.12, 0.14, 0.55, C.COL_MODI_KURTA)
        self.arm_left.reparent_to(self.root)
        self.arm_left.set_pos(-0.46, 0, 0.65)

        self.arm_right = make_box("arm_r", 0.12, 0.14, 0.55, C.COL_MODI_KURTA)
        self.arm_right.reparent_to(self.root)
        self.arm_right.set_pos(0.46, 0, 0.65)

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

        # Running step bob and arm swing animation
        bob = 0.0
        if self.z <= 0.01:
            self._anim_phase += dt * (self._run_speed * 1.1)
            bob = abs(math.sin(self._anim_phase)) * 0.12

            # Dynamic arm swing
            swing = math.sin(self._anim_phase) * 0.22
            self.arm_left.set_pos(-0.46, swing, 0.65)
            self.arm_right.set_pos(0.46, -swing, 0.65)
        else:
            # Jumping pose (arms slightly raised forward)
            self.arm_left.set_pos(-0.46, 0.18, 0.72)
            self.arm_right.set_pos(0.46, 0.18, 0.72)

        self.root.set_y(self.y)
        self.root.set_z(self.z + bob)
