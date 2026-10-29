"""
hud.py
On-screen HUD: score, speed, police proximity, and game-over overlay.
"""
from __future__ import annotations

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectFrame import DirectFrame
from panda3d.core import TextNode

from . import constants as C


class HUD:
    """Manages all 2-D overlay elements."""

    def __init__(self) -> None:
        self._score_text = OnscreenText(
            text="Score: 0",
            pos=(-1.25, 0.88),
            fg=C.COL_NEON_CYAN,
            scale=0.07,
            align=TextNode.ALeft,
            mayChange=True,
        )
        self._speed_text = OnscreenText(
            text="Speed: 0",
            pos=(-1.25, 0.78),
            fg=C.COL_NEON_MAG,
            scale=0.055,
            align=TextNode.ALeft,
            mayChange=True,
        )
        self._police_text = OnscreenText(
            text="",
            pos=(0.0, -0.85),
            fg=(1, 0.3, 0.3, 1),
            scale=0.07,
            align=TextNode.ACenter,
            mayChange=True,
        )

        # Game-over overlay (hidden until needed)
        self._gameover_frame = DirectFrame(
            frameSize=(-0.9, 0.9, -0.35, 0.35),
            frameColor=(0, 0, 0, 0.75),
            pos=(0, 0, 0),
        )
        self._gameover_frame.hide()

        self._gameover_title = OnscreenText(
            text="GAME OVER",
            pos=(0, 0.12),
            fg=(1, 0.2, 0.2, 1),
            scale=0.14,
            align=TextNode.ACenter,
            mayChange=True,
            parent=self._gameover_frame,
        )
        self._gameover_score = OnscreenText(
            text="",
            pos=(0, -0.02),
            fg=(1, 1, 1, 1),
            scale=0.07,
            align=TextNode.ACenter,
            mayChange=True,
            parent=self._gameover_frame,
        )
        self._gameover_hint = OnscreenText(
            text="Press R to restart  |  ESC to quit",
            pos=(0, -0.18),
            fg=(0.7, 0.7, 0.7, 1),
            scale=0.055,
            align=TextNode.ACenter,
            mayChange=True,
            parent=self._gameover_frame,
        )

    # ------------------------------------------------------------------

    def update(self, score: int, speed: float, police_dist: float) -> None:
        self._score_text.setText(f"Score: {score:,}")
        self._speed_text.setText(f"Speed: {speed:.1f} m/s")

        if police_dist < 6.0:
            self._police_text.setText("⚠ POLICE CLOSING IN!")
        else:
            self._police_text.setText("")

    def show_gameover(self, score: int) -> None:
        self._gameover_score.setText(f"Distance: {score:,} m")
        self._gameover_frame.show()

    def hide_gameover(self) -> None:
        self._gameover_frame.hide()

    def destroy(self) -> None:
        self._score_text.destroy()
        self._speed_text.destroy()
        self._police_text.destroy()
        self._gameover_frame.destroy()

