"""
hud.py
Heads-up display (HUD) showing score, speed, controls guide, and game-over dialog.
"""
from __future__ import annotations

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectFrame import DirectFrame
from panda3d.core import TextNode

from . import constants as C


class HUD:
    """Manages all 2D screen interface overlays."""

    def __init__(self) -> None:
        # Distance / Score indicator
        self._score_text = OnscreenText(
            text="DISTANCE: 0 m",
            pos=(-1.28, 0.90),
            fg=C.COL_NEON_CYAN,
            scale=0.065,
            align=TextNode.ALeft,
            mayChange=True,
            shadow=(0, 0, 0, 0.8),
        )

        # Runner speed
        self._speed_text = OnscreenText(
            text="SPEED: 0.0 m/s",
            pos=(-1.28, 0.82),
            fg=C.COL_NEON_MAG,
            scale=0.048,
            align=TextNode.ALeft,
            mayChange=True,
            shadow=(0, 0, 0, 0.8),
        )

        # In-game control reminder (top right)
        self._controls_hint = OnscreenText(
            text="[A / D] Lane Switch   [SPACE] Jump",
            pos=(1.28, 0.90),
            fg=(0.85, 0.85, 0.85, 0.9),
            scale=0.045,
            align=TextNode.ARight,
            mayChange=False,
            shadow=(0, 0, 0, 0.8),
        )

        # Police proximity / pursuit alert
        self._police_alert = OnscreenText(
            text="",
            pos=(0.0, -0.85),
            fg=(1.0, 0.2, 0.3, 1.0),
            scale=0.06,
            align=TextNode.ACenter,
            mayChange=True,
            shadow=(0, 0, 0, 0.9),
        )

        # Game-over overlay container
        self._gameover_frame = DirectFrame(
            frameSize=(-0.85, 0.85, -0.42, 0.42),
            frameColor=(0.04, 0.02, 0.08, 0.88),
            pos=(0, 0, 0),
        )
        self._gameover_frame.hide()

        self._gameover_title = OnscreenText(
            text="BUSTED!",
            pos=(0, 0.20),
            fg=(1.0, 0.15, 0.25, 1.0),
            scale=0.13,
            align=TextNode.ACenter,
            mayChange=False,
            parent=self._gameover_frame,
            shadow=(0, 0, 0, 1),
        )

        self._gameover_subtitle = OnscreenText(
            text="The police caught you in the gully!",
            pos=(0, 0.08),
            fg=(0.8, 0.8, 0.8, 1.0),
            scale=0.048,
            align=TextNode.ACenter,
            mayChange=False,
            parent=self._gameover_frame,
        )

        self._gameover_score = OnscreenText(
            text="",
            pos=(0, -0.05),
            fg=C.COL_NEON_CYAN,
            scale=0.075,
            align=TextNode.ACenter,
            mayChange=True,
            parent=self._gameover_frame,
            shadow=(0, 0, 0, 1),
        )

        self._gameover_restart = OnscreenText(
            text="Press [ R ] to Run Again   |   Press [ ESC ] to Quit",
            pos=(0, -0.22),
            fg=(0.95, 0.90, 0.20, 1.0),
            scale=0.052,
            align=TextNode.ACenter,
            mayChange=False,
            parent=self._gameover_frame,
            shadow=(0, 0, 0, 1),
        )

    # ------------------------------------------------------------------

    def update(self, score: int, speed: float, police_dist: float) -> None:
        self._score_text.setText(f"DISTANCE: {score:,} m")
        self._speed_text.setText(f"SPEED: {speed:.1f} m/s")

        if police_dist < 4.0:
            self._police_alert.setText("POLICE IS RIGHT BEHIND YOU!")
        else:
            self._police_alert.setText("")

    def show_gameover(self, score: int) -> None:
        self._police_alert.setText("")
        self._gameover_score.setText(f"FINAL DISTANCE: {score:,} METERS")
        self._gameover_frame.show()

    def hide_gameover(self) -> None:
        self._gameover_frame.hide()

    def destroy(self) -> None:
        self._score_text.destroy()
        self._speed_text.destroy()
        self._controls_hint.destroy()
        self._police_alert.destroy()
        self._gameover_frame.destroy()
