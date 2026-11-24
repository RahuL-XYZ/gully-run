"""
collectibles.py
Manages collectible gold coins, jump-arc coin trails, and game power-ups:
- Coin Magnet (pulls nearby coins towards player)
- Turbo Rush (invincibility + speed burst)
- 2X Multiplier (doubles distance & coin rewards)
"""
from __future__ import annotations

import math
import random
from panda3d.core import NodePath

from . import constants as C
from .utils import make_box, lerp, clamp


class Coin:
    """A single spinning golden coin."""

    RADIUS = 0.35
    HEIGHT = 0.55

    def __init__(self, parent: NodePath, x: float, y: float, z: float) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.base_z = z
        self._bob_phase = random.uniform(0.0, 6.28)

        self.root = NodePath("coin_root")
        self.root.reparent_to(parent)
        self.root.set_pos(x, y, z)

        # 3D Gold coin mesh (octagonal look with gold face and rim)
        self.coin_mesh = make_box("coin_body", 0.30, 0.08, 0.30, C.COL_COIN)
        self.coin_mesh.reparent_to(self.root)
        self.coin_mesh.set_pos(0, 0, 0)

        # Glowing center core
        core = make_box("coin_core", 0.16, 0.10, 0.16, (1.0, 1.0, 0.6, 1.0))
        core.reparent_to(self.coin_mesh)
        core.set_pos(0, 0, 0.07)

    def update(self, dt: float, player_pos: tuple[float, float, float] | None = None, magnet_active: bool = False) -> None:
        # Spin rotation
        self.coin_mesh.set_h(self.coin_mesh.get_h() + dt * 240.0)

        # Subtle vertical floating bob
        self._bob_phase += dt * 4.0
        bob = math.sin(self._bob_phase) * 0.08

        # Magnet attraction
        if magnet_active and player_pos is not None:
            px, py, pz = player_pos
            dist = math.sqrt((self.x - px) ** 2 + (self.y - py) ** 2 + (self.z - pz) ** 2)
            if dist < 9.0:
                pull_rate = clamp(14.0 * dt, 0.0, 1.0)
                self.x = lerp(self.x, px, pull_rate)
                self.y = lerp(self.y, py, pull_rate)
                self.z = lerp(self.z, pz + 0.6, pull_rate)
                self.root.set_pos(self.x, self.y, self.z)
                return

        self.root.set_pos(self.x, self.y, self.base_z + bob)

    def check_pickup(self, px: float, py: float, pz: float) -> bool:
        dx = abs(self.x - px)
        dy = abs(self.y - py)
        dz = abs(self.z - (pz + 0.6))
        return dx < 0.95 and dy < 1.05 and dz < 1.10

    def remove(self) -> None:
        self.root.remove_node()


class PowerUp:
    """A floating, spinning special ability pickup."""

    TYPE_MAGNET = "magnet"
    TYPE_TURBO = "turbo"
    TYPE_2X = "2x"

    def __init__(self, parent: NodePath, x: float, y: float, kind: str) -> None:
        self.x = x
        self.y = y
        self.z = 0.90
        self.kind = kind
        self._bob_phase = random.uniform(0.0, 6.28)

        self.root = NodePath("powerup_root")
        self.root.reparent_to(parent)
        self.root.set_pos(x, y, self.z)

        # Distinct 3D mesh based on power-up type
        if kind == self.TYPE_MAGNET:
            color = C.COL_POWER_MAGNET
            # Blue housing with metallic poles
            self.mesh = make_box("magnet_box", 0.35, 0.35, 0.35, color)
            self.mesh.reparent_to(self.root)
            self.mesh.set_pos(0, 0, 0)
            pole_l = make_box("p_l", 0.10, 0.10, 0.22, (0.9, 0.9, 0.95, 1.0))
            pole_l.reparent_to(self.mesh)
            pole_l.set_pos(-0.20, 0, 0.25)
            pole_r = make_box("p_r", 0.10, 0.10, 0.22, (0.9, 0.9, 0.95, 1.0))
            pole_r.reparent_to(self.mesh)
            pole_r.set_pos(0.20, 0, 0.25)

        elif kind == self.TYPE_TURBO:
            color = C.COL_POWER_TURBO
            # Fiery orange rocket prism
            self.mesh = make_box("turbo_box", 0.32, 0.32, 0.45, color)
            self.mesh.reparent_to(self.root)
            self.mesh.set_pos(0, 0, 0)
            fin = make_box("turbo_fin", 0.42, 0.10, 0.20, (1.0, 0.9, 0.1, 1.0))
            fin.reparent_to(self.mesh)
            fin.set_pos(0, 0, 0.12)

        else:  # 2X Multiplier
            color = C.COL_POWER_2X
            # Emerald green emblem
            self.mesh = make_box("2x_box", 0.36, 0.36, 0.36, color)
            self.mesh.reparent_to(self.root)
            self.mesh.set_pos(0, 0, 0)
            core = make_box("2x_core", 0.20, 0.20, 0.20, (1.0, 1.0, 1.0, 1.0))
            core.reparent_to(self.mesh)
            core.set_pos(0, 0, 0.08)

    def update(self, dt: float) -> None:
        self.mesh.set_h(self.mesh.get_h() + dt * 160.0)
        self._bob_phase += dt * 3.5
        bob = math.sin(self._bob_phase) * 0.12
        self.root.set_z(self.z + bob)

    def check_pickup(self, px: float, py: float, pz: float) -> bool:
        dx = abs(self.x - px)
        dy = abs(self.y - py)
        dz = abs(self.z - (pz + 0.6))
        return dx < 1.15 and dy < 1.25 and dz < 1.30

    def remove(self) -> None:
        self.root.remove_node()


class CollectibleManager:
    """Spawns, updates, animates, and checks collisions for coins and power-ups."""

    def __init__(self, parent: NodePath) -> None:
        self._parent = parent
        self.coins: list[Coin] = []
        self.powerups: list[PowerUp] = []
        self._last_spawn_y: float = 24.0

    def update(
        self,
        dt: float,
        player_y: float,
        player_pos: tuple[float, float, float],
        magnet_active: bool = False,
    ) -> tuple[int, str | None]:
        """
        Updates rotation and magnet physics. Checks pickup collisions.
        Returns: (coins_collected_this_frame, powerup_type_collected_or_None)
        """
        # 1. Spawn ahead
        spawn_horizon = player_y + C.OBSTACLE_SPAWN_DIST
        while spawn_horizon - self._last_spawn_y >= 16.0:
            self._last_spawn_y += 16.0
            self._spawn_cluster(self._last_spawn_y)

        # 2. Update coins & check pickup
        coins_collected = 0
        px, py, pz = player_pos
        alive_coins: list[Coin] = []

        for coin in self.coins:
            coin.update(dt, player_pos, magnet_active)
            if coin.check_pickup(px, py, pz):
                coin.remove()
                coins_collected += 1
            elif coin.y < player_y - 12.0:
                coin.remove()
            else:
                alive_coins.append(coin)
        self.coins = alive_coins

        # 3. Update power-ups & check pickup
        powerup_collected: str | None = None
        alive_powerups: list[PowerUp] = []

        for p in self.powerups:
            p.update(dt)
            if p.check_pickup(px, py, pz):
                powerup_collected = p.kind
                p.remove()
            elif p.y < player_y - 12.0:
                p.remove()
            else:
                alive_powerups.append(p)
        self.powerups = alive_powerups

        return coins_collected, powerup_collected

    def _spawn_cluster(self, y: float) -> None:
        """Spawn either a straight coin run, an arced coin trail, or an occasional power-up."""
        lane = random.randint(0, C.NUM_LANES - 1)
        lane_x = C.LANE_X[lane]

        pattern = random.choice(["line", "line", "arc", "line", "powerup"])

        if pattern == "line":
            # Straight trail of 4 coins along road surface
            for i in range(4):
                cy = y + (i * 2.2)
                self.coins.append(Coin(self._parent, lane_x, cy, 0.55))

        elif pattern == "arc":
            # Parabolic jump-arc of 5 coins (encourages jumping!)
            steps = 5
            for i in range(steps):
                t = i / (steps - 1)  # 0.0 to 1.0
                cy = y + (i * 2.0)
                # Inverted parabola arc height peaking at 1.8m
                cz = 0.55 + 4.0 * t * (1.0 - t) * 1.35
                self.coins.append(Coin(self._parent, lane_x, cy, cz))

        elif pattern == "powerup":
            # Single floating power-up pickup
            kind = random.choice([PowerUp.TYPE_MAGNET, PowerUp.TYPE_TURBO, PowerUp.TYPE_2X])
            self.powerups.append(PowerUp(self._parent, lane_x, y, kind))
            # Also add a couple coins before it
            self.coins.append(Coin(self._parent, lane_x, y - 2.5, 0.55))
            self.coins.append(Coin(self._parent, lane_x, y + 2.5, 0.55))

    def clear(self) -> None:
        for c in self.coins:
            c.remove()
        for p in self.powerups:
            p.remove()
        self.coins.clear()
        self.powerups.clear()
