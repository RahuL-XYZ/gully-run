"""
lighting.py
Scene lighting setup for Gully Run: directional moonlight with real-time dynamic shadows,
warm chai-stall street glow, and neon point lights.
"""
from __future__ import annotations

from panda3d.core import (
    AmbientLight, DirectionalLight, PointLight,
    LColor, NodePath,
)


class LightingManager:
    """Manages scene lights, shadow casting, and dynamic follower lights."""

    def __init__(self, render: NodePath) -> None:
        self.render = render
        self.lights: list[NodePath] = []

        # 1. Ambient – deep night indigo
        alight = AmbientLight("ambient_light")
        alight.set_color(LColor(0.24, 0.20, 0.32, 1.0))
        self.alnp = render.attach_new_node(alight)
        render.set_light(self.alnp)
        self.lights.append(self.alnp)

        # 2. Main street directional moonlight with dynamic shadow caster
        self.dlight = DirectionalLight("moon_light")
        self.dlight.set_color(LColor(0.88, 0.90, 0.96, 1.0))
        self.dlight.set_shadow_caster(True, 1024, 1024)

        # Shadow frustum lens centered around the runner's corridor
        lens = self.dlight.get_lens()
        lens.set_film_size(32, 40)
        lens.set_near_far(1.0, 70.0)

        self.dlnp = render.attach_new_node(self.dlight)
        self.dlnp.set_hpr(-40, -55, 0)
        self.dlnp.set_pos(0, 0, 15)
        render.set_light(self.dlnp)
        self.lights.append(self.dlnp)

        # 3. Warm chai-stall street glow fill
        warm_fill = DirectionalLight("warm_fill")
        warm_fill.set_color(LColor(0.38, 0.22, 0.12, 1.0))
        self.wlnp = render.attach_new_node(warm_fill)
        self.wlnp.set_hpr(140, -35, 0)
        render.set_light(self.wlnp)
        self.lights.append(self.wlnp)

        # 4. Neon cyan accent point light
        self.neon_cyan = PointLight("neon_cyan_point")
        self.neon_cyan.set_color(LColor(0.05, 0.85, 1.0, 1.0))
        self.neon_cyan.set_attenuation((1.0, 0.04, 0.005))
        self.ncnp = render.attach_new_node(self.neon_cyan)
        self.ncnp.set_pos(0, 12, 4.5)
        render.set_light(self.ncnp)
        self.lights.append(self.ncnp)

        # 5. Neon magenta accent point light
        self.neon_mag = PointLight("neon_mag_point")
        self.neon_mag.set_color(LColor(1.0, 0.08, 0.75, 1.0))
        self.neon_mag.set_attenuation((1.0, 0.04, 0.005))
        self.nmnp = render.attach_new_node(self.neon_mag)
        self.nmnp.set_pos(-5.5, 18, 4.5)
        render.set_light(self.nmnp)
        self.lights.append(self.nmnp)

    def update(self, player_y: float) -> None:
        """Keep the shadow-casting moon light and neon point lights focused around the runner."""
        # Shadow frustum tracks player forward
        self.dlnp.set_y(player_y + 8.0)
        # Point lights travel along with street ambiance
        self.ncnp.set_y(player_y + 12.0)
        self.nmnp.set_y(player_y + 20.0)
