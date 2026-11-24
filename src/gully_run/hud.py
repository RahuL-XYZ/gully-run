"""
hud.py
Heads-up display (HUD) showing score, coins, speed, high-score records,
active power-up timers, pause menu, and game-over dialog.
"""
from __future__ import annotations

from direct.gui.OnscreenText import OnscreenText
from direct.gui.DirectFrame import DirectFrame
from panda3d.core import TextNode

from . import constants as C


class HUD:
    """Manages all 2D screen interface overlays."""

    def __init__(self, highscore: int = 0) -> None:
        # Distance / Score indicator
        self._score_text = OnscreenText(
            text="DISTANCE: 0 m",
            pos=(-1.28, 0.90),
            fg=C.COL_NEON_CYAN,
            scale=0.062,
            align=TextNode.ALeft,
            mayChange=True,
            shadow=(0, 0, 0, 0.8),
        )

        # High-score record
        self._best_text = OnscreenText(
            text=f"BEST: {highscore:,} m",
            pos=(-1.28, 0.83),
            fg=(0.80, 0.80, 0.85, 0.9),
            scale=0.046,
            align=TextNode.ALeft,
            mayChange=True,
            shadow=(0, 0, 0, 0.8),
        )

        # Coins collected counter
        self._coins_text = OnscreenText(
            text="COINS: 0",
            pos=(-1.28, 0.76),
            fg=C.COL_COIN,
            scale=0.052,
            align=TextNode.ALeft,
            mayChange=True,
            shadow=(0, 0, 0, 0.8),
        )

        # Runner speed
        self._speed_text = OnscreenText(
            text="SPEED: 0.0 m/s",
            pos=(-1.28, 0.69),
            fg=C.COL_MODI_JACKET,
            scale=0.044,
            align=TextNode.ALeft,
            mayChange=True,
            shadow=(0, 0, 0, 0.8),
        )

        # Active Power-up indicator (Center top)
        self._powerup_text = OnscreenText(
            text="",
            pos=(0.0, 0.88),
            fg=(1.0, 1.0, 1.0, 1.0),
            scale=0.058,
            align=TextNode.ACenter,
            mayChange=True,
            shadow=(0, 0, 0, 0.9),
        )

        # In-game control reminder (top right)
        self._controls_hint = OnscreenText(
            text="[W] Jump  [S] Slide  [A/D] Lane  [P] Pause",
            pos=(1.28, 0.90),
            fg=(0.90, 0.90, 0.95, 0.9),
            scale=0.042,
            align=TextNode.ARight,
            mayChange=False,
            shadow=(0, 0, 0, 0.8),
        )

        # Character role tag
        self._char_tag = OnscreenText(
            text="RUNNER: NaMo  vs  PURSUER: Don",
            pos=(1.28, 0.83),
            fg=C.COL_TRUMP_HAIR,
            scale=0.038,
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

        # ── Pause Overlay ──────────────────────────────────────────────────
        self._pause_frame = DirectFrame(
            frameSize=(-0.70, 0.70, -0.35, 0.35),
            frameColor=(0.04, 0.02, 0.08, 0.88),
            pos=(0, 0, 0),
        )
        self._pause_frame.hide()

        self._pause_title = OnscreenText(
            text="GAME PAUSED",
            pos=(0, 0.15),
            fg=C.COL_NEON_CYAN,
            scale=0.10,
            align=TextNode.ACenter,
            parent=self._pause_frame,
            shadow=(0, 0, 0, 1),
        )

        self._pause_hint = OnscreenText(
            text="Press [ P ] to Resume\nPress [ R ] to Restart\nPress [ ESC ] to Quit",
            pos=(0, -0.05),
            fg=(0.9, 0.9, 0.95, 1.0),
            scale=0.050,
            align=TextNode.ACenter,
            parent=self._pause_frame,
            shadow=(0, 0, 0, 1),
        )

        # ── Game-Over Overlay Container ────────────────────────────────────
        self._gameover_frame = DirectFrame(
            frameSize=(-0.90, 0.90, -0.48, 0.48),
            frameColor=(0.04, 0.02, 0.08, 0.92),
            pos=(0, 0, 0),
        )
        self._gameover_frame.hide()

        self._gameover_title = OnscreenText(
            text="BUSTED IN THE GULLY!",
            pos=(0, 0.28),
            fg=C.COL_TRUMP_TIE,
            scale=0.11,
            align=TextNode.ACenter,
            mayChange=False,
            parent=self._gameover_frame,
            shadow=(0, 0, 0, 1),
        )

        self._gameover_subtitle = OnscreenText(
            text="The Chief Pursuer caught up to your sprint!",
            pos=(0, 0.17),
            fg=(0.85, 0.85, 0.90, 1.0),
            scale=0.044,
            align=TextNode.ACenter,
            mayChange=False,
            parent=self._gameover_frame,
        )

        self._gameover_score = OnscreenText(
            text="",
            pos=(0, 0.04),
            fg=C.COL_NEON_CYAN,
            scale=0.068,
            align=TextNode.ACenter,
            mayChange=True,
            parent=self._gameover_frame,
            shadow=(0, 0, 0, 1),
        )

        self._gameover_coins = OnscreenText(
            text="",
            pos=(0, -0.06),
            fg=C.COL_COIN,
            scale=0.056,
            align=TextNode.ACenter,
            mayChange=True,
            parent=self._gameover_frame,
            shadow=(0, 0, 0, 1),
        )

        self._gameover_record = OnscreenText(
            text="",
            pos=(0, -0.16),
            fg=(0.95, 0.85, 0.2, 1.0),
            scale=0.052,
            align=TextNode.ACenter,
            mayChange=True,
            parent=self._gameover_frame,
            shadow=(0, 0, 0, 1),
        )

        self._gameover_restart = OnscreenText(
            text="Press [ R ] to Run Again   |   Press [ ESC ] to Quit",
            pos=(0, -0.32),
            fg=C.COL_LANE_MARK,
            scale=0.048,
            align=TextNode.ACenter,
            mayChange=False,
            parent=self._gameover_frame,
            shadow=(0, 0, 0, 1),
        )

    # ------------------------------------------------------------------

    def update(
        self,
        score: int,
        coins: int,
        speed: float,
        police_dist: float,
        powerup_info: tuple[str, float] | None = None,
    ) -> None:
        self._score_text.setText(f"DISTANCE: {score:,} m")
        self._coins_text.setText(f"COINS: {coins:,}")
        self._speed_text.setText(f"SPEED: {speed:.1f} m/s")

        # Active powerup display
        if powerup_info is not None:
            kind, time_left = powerup_info
            if kind == "magnet":
                self._powerup_text.setText(f"MAGNET: {time_left:.1f}s")
                self._powerup_text.setFg(C.COL_POWER_MAGNET)
            elif kind == "turbo":
                self._powerup_text.setText(f"TURBO RUSH: {time_left:.1f}s (INVINCIBLE)")
                self._powerup_text.setFg(C.COL_POWER_TURBO)
            elif kind == "2x":
                self._powerup_text.setText(f"2X MULTIPLIER: {time_left:.1f}s")
                self._powerup_text.setFg(C.COL_POWER_2X)
        else:
            self._powerup_text.setText("")

        # Police proximity warning
        if police_dist < 4.0:
            self._police_alert.setText("PURSUER CLOSING IN!")
        else:
            self._police_alert.setText("")

    def set_best_score(self, best: int) -> None:
        self._best_text.setText(f"BEST: {best:,} m")

    def show_gameover(self, score: int, coins: int, highscore: int, is_new_record: bool) -> None:
        self._police_alert.setText("")
        self._powerup_text.setText("")
        self._gameover_score.setText(f"FINAL DISTANCE: {score:,} METERS")
        self._gameover_coins.setText(f"COINS COLLECTED: +{coins:,}")

        if is_new_record:
            self._gameover_record.setText("NEW PERSONAL BEST RECORD!")
            self._gameover_record.setFg((0.3, 1.0, 0.4, 1.0))
        else:
            self._gameover_record.setText(f"ALL-TIME BEST: {highscore:,} METERS")
            self._gameover_record.setFg((0.85, 0.85, 0.90, 1.0))

        self._gameover_frame.show()

    def hide_gameover(self) -> None:
        self._gameover_frame.hide()

    def show_pause(self) -> None:
        self._pause_frame.show()

    def hide_pause(self) -> None:
        self._pause_frame.hide()

    def destroy(self) -> None:
        self._score_text.destroy()
        self._best_text.destroy()
        self._coins_text.destroy()
        self._speed_text.destroy()
        self._powerup_text.destroy()
        self._controls_hint.destroy()
        self._char_tag.destroy()
        self._police_alert.destroy()
        self._pause_frame.destroy()
        self._gameover_frame.destroy()
