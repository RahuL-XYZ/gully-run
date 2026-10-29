"""
lighting.py
Scene lighting setup for Gully Run's neon-accented night market aesthetic.
"""
from __future__ import annotations

from panda3d.core import (
    AmbientLight, DirectionalLight, PointLight,
    LColor, NodePath,
)


def setup_lighting(render: NodePath) -> list[NodePath]:
    """
    Configure atmospheric night lighting with neon highlights.
    Returns the list of light NodePaths.
    """
    lights: list[NodePath] = []

    # 1. Ambient – deep night indigo
    alight = AmbientLight("ambient_light")
    alight.set_color(LColor(0.18, 0.14, 0.26, 1.0))
    alnp = render.attach_new_node(alight)
    render.set_light(alnp)
    lights.append(alnp)

    # 2. Main street directional moonlight
    dlight = DirectionalLight("moon_light")
    dlight.set_color(LColor(0.85, 0.88, 0.95, 1.0))
    dlnp = render.attach_new_node(dlight)
    dlnp.set_hpr(-40, -55, 0)
    render.set_light(dlnp)
    lights.append(dlnp)

    # 3. Warm chai-stall street glow
    warm_fill = DirectionalLight("warm_fill")
    warm_fill.set_color(LColor(0.40, 0.24, 0.10, 1.0))
    wlnp = render.attach_new_node(warm_fill)
    wlnp.set_hpr(140, -35, 0)
    render.set_light(wlnp)
    lights.append(wlnp)

    # 4. Neon cyan accent point light
    neon_cyan = PointLight("neon_cyan_point")
    neon_cyan.set_color(LColor(0.1, 0.8, 1.0, 1.0))
    neon_cyan.set_attenuation((1.0, 0.04, 0.005))
    ncnp = render.attach_new_node(neon_cyan)
    ncnp.set_pos(0, 15, 5)
    render.set_light(ncnp)
    lights.append(ncnp)

    # 5. Neon magenta accent point light
    neon_mag = PointLight("neon_mag_point")
    neon_mag.set_color(LColor(1.0, 0.1, 0.8, 1.0))
    neon_mag.set_attenuation((1.0, 0.04, 0.005))
    nmnp = render.attach_new_node(neon_mag)
    nmnp.set_pos(-6, 20, 5)
    render.set_light(nmnp)
    lights.append(nmnp)

    return lights
