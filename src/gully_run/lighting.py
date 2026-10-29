"""
lighting.py
Scene lighting setup for Gully Run.
"""
from __future__ import annotations

from panda3d.core import (
    AmbientLight, DirectionalLight, PointLight,
    LColor, LVector3, NodePath,
)


def setup_lighting(render: NodePath) -> None:
    """Attach ambient + directional lights to render; add a couple of neon point lights."""

    # Ambient – very dark blue-purple
    alight = AmbientLight("ambient")
    alight.set_color(LColor(0.08, 0.06, 0.14, 1))
    alnp = render.attach_new_node(alight)
    render.set_light(alnp)

    # Primary directional – cool white from upper-left
    dlight = DirectionalLight("sun")
    dlight.set_color(LColor(0.7, 0.75, 0.9, 1))
    dlnp = render.attach_new_node(dlight)
    dlnp.set_hpr(-45, -60, 0)
    render.set_light(dlnp)

    # Fill light from the right – warm orange (chai-stall warmth)
    flight = DirectionalLight("fill")
    flight.set_color(LColor(0.3, 0.2, 0.05, 1))
    flnp = render.attach_new_node(flight)
    flnp.set_hpr(135, -30, 0)
    render.set_light(flnp)

    # Neon cyan point light near road centre
    plight_c = PointLight("neon_cyan")
    plight_c.set_color(LColor(0.0, 0.6, 0.8, 1))
    plight_c.set_attenuation((1, 0.05, 0.01))
    plnp_c = render.attach_new_node(plight_c)
    plnp_c.set_pos(0, 20, 4)
    render.set_light(plnp_c)

    # Neon magenta point light offset left
    plight_m = PointLight("neon_mag")
    plight_m.set_color(LColor(0.8, 0.0, 0.6, 1))
    plight_m.set_attenuation((1, 0.05, 0.01))
    plnp_m = render.attach_new_node(plight_m)
    plnp_m.set_pos(-5, 15, 4)
    render.set_light(plnp_m)

