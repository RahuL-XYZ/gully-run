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
            fg=C.COL_MODI_JACKET,
            scale=0.048,
            align=TextNode.ALeft,
            mayChange=True,
            shadow=(0, 0, 0, 0.8),
        )

        # In-game control reminder (top right)
        self._controls_hint = OnscreenText(
            text="[A / D] Lane Switch   [SPACE] Jump",
            pos=(1.28, 0.90),
            fg=(0.90, 0.90, 0.95, 0.9),
            scale=0.045,
            align=TextNode.ARight,
            mayChange=False,
            shadow=(0, 0, 0, 0.8),
        )

        # Character role tag
        self._char_tag = OnscreenText(
            text="RUNNER: NaMo  vs  PURSUER: Don",
            pos=(1.28, 0.83),
            fg=C.COL_TRUMP_HAIR,
            scale=0.040,
            align=TextNode.ARight,
            mayChange=False,
            shadow=(0, 0, 0, 0.8),
        )

        # Police proximity / pursuit alert
        self._police_alert = OnscreenText(
            text="",
            pos=(0.0, -0.85),
            fg=C.COL_TRUMP_TIE,
            scale=0.065,
            align=TextNode.ACenter,
            mayChange=True,
            shadow=(0, 0, 0, 0.9),
        )

        # Game-over overlay container
        self._gameover_frame = DirectFrame(
            frameSize=(-0.90, 0.90, -0.45, 0.45),
            frameColor=(0.04, 0.02, 0.08, 0.90),
            pos=(0, 0, 0),
        )
        self._gameover_frame.hide()

        self._gameover_title = OnscreenText(
            text="BUSTED IN THE GULLY!",
            pos=(0, 0.22),
            fg=C.COL_TRUMP_TIE,
            scale=0.12,
            align=TextNode.ACenter,
            mayChange=False,
            parent=self._gameover_frame,
            shadow=(0, 0, 0, 1),
        )

        self._gameover_subtitle = OnscreenText(
            text="The Chief Pursuer caught up to your sprint!",
            pos=(0, 0.10),
            fg=(0.85, 0.85, 0.90, 1.0),
            scale=0.048,
            align=TextNode.ACenter,
            mayChange=False,
            parent=self._gameover_frame,
        )

        self._gameover_score = OnscreenText(
            text="",
            pos=(0, -0.04),
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
            fg=C.COL_LANE_MARK,
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
            self._police_alert.setText("⚠ PURSUER CLOSING IN!")
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
        self._char_tag.destroy()
        self._police_alert.destroy()
        self._gameover_frame.destroy()
