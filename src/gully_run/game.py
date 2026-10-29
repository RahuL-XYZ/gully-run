"""
game.py
Main Panda3D application class for Gully Run.
"""
from __future__ import annotations

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import LColor, WindowProperties

from . import constants as C
from .player    import Player
from .road      import RoadManager
from .camera    import FollowCamera
from .obstacles import ObstacleManager
from .police    import Police
from .hud       import HUD
from .lighting  import setup_lighting


class GullyRun(ShowBase):
    """Top-level game application."""

    def __init__(self) -> None:
        super().__init__()

        # ── Window ──────────────────────────────────────────────────────────
        props = WindowProperties()
        props.set_title(C.WINDOW_TITLE)
        props.set_size(C.WIN_W, C.WIN_H)
        self.win.request_properties(props)

        self.set_background_color(*C.COL_BG)

        # Disable default mouse-look
        self.disable_mouse()

        # ── Scene ───────────────────────────────────────────────────────────
        setup_lighting(self.render)

        self._build_world()

        # ── Key bindings ────────────────────────────────────────────────────
        self.accept("escape",      self._on_escape)
        self.accept("a",           self._on_left)
        self.accept("arrow_left",  self._on_left)
        self.accept("d",           self._on_right)
        self.accept("arrow_right", self._on_right)
        self.accept("space",       self._on_jump)
        self.accept("r",           self._on_restart)

        # ── State ───────────────────────────────────────────────────────────
        self._game_over = False

        # ── Main update task ────────────────────────────────────────────────
        self.task_mgr.add(self._update, "update")

    # ---------------------------------------------------------------- world build

    def _build_world(self) -> None:
        """(Re-)construct all game objects."""
        # Clear any previous scene children except lights/camera
        self.render.node().remove_all_children()
        setup_lighting(self.render)

        self._player    = Player(self.render)
        self._road      = RoadManager(self.render)
        self._obstacles = ObstacleManager(self.render)
        self._police    = Police(self.render, self._player.y)
        self._follow_cam = FollowCamera(self.camera, self._player.node)
        self._hud        = HUD()
        self._score      = 0
        self._game_over  = False

    # ---------------------------------------------------------------- input

    def _on_escape(self) -> None:
        self.userExit()

    def _on_left(self) -> None:
        if not self._game_over:
            self._player.try_move_left()

    def _on_right(self) -> None:
        if not self._game_over:
            self._player.try_move_right()

    def _on_jump(self) -> None:
        if not self._game_over:
            self._player.try_jump()

    def _on_restart(self) -> None:
        if self._game_over:
            self._hud.destroy()
            self._build_world()

    # ---------------------------------------------------------------- main loop

    def _update(self, task: Task) -> int:
        if self._game_over:
            return Task.cont

        dt = globalClock.get_dt()
        dt = min(dt, 0.05)           # clamp to avoid physics tunnelling on lag

        # Update gameplay objects
        self._player.update(dt)
        self._road.update(self._player.y)
        self._obstacles.update(self._player.y)
        self._police.update(dt, self._player.y, self._player.run_speed)

        # Score = distance in whole metres
        self._score = int(self._player.y * C.SCORE_PER_METER)

        # Camera
        self._follow_cam.update(dt)

        # Police catch distance
        pd = self._police.distance_to_player(self._player.y)

        # HUD
        self._hud.update(self._score, self._player.run_speed, pd)

        # Collision check
        if self._obstacles.check_collision(self._player):
            self._trigger_game_over()

        elif pd < C.POLICE_CATCH_DIST:
            self._trigger_game_over()

        return Task.cont

    # ---------------------------------------------------------------- game over

    def _trigger_game_over(self) -> None:
        self._game_over = True
        self._hud.show_gameover(self._score)

