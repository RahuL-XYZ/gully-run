"""
game.py
Main Panda3D application class for Gully Run.
"""
from __future__ import annotations

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import WindowProperties, NodePath

from . import constants as C
from .player import Player
from .road import RoadManager
from .camera import FollowCamera
from .obstacles import ObstacleManager
from .police import Police
from .hud import HUD
from .lighting import LightingManager
from .audio import AudioManager


class GullyRun(ShowBase):
    """
    Top-level Panda3D game application for Gully Run.
    Orchestrates the game loop, input handling, physics updates,
    collision detection, camera tracking, audio, and game-over state.
    """

    def __init__(self) -> None:
        super().__init__()

        # ── Window Setup ───────────────────────────────────────────────────
        props = WindowProperties()
        props.set_title(C.WINDOW_TITLE)
        props.set_size(C.WIN_W, C.WIN_H)
        self.win.request_properties(props)

        self.set_background_color(*C.COL_BG)
        self.disable_mouse()

        # ── Hardware Shaders & Dynamic Shadows ─────────────────────────────
        self.render.set_shader_auto()

        # ── Persistent Scene & Lighting ────────────────────────────────────
        self._lighting = LightingManager(self.render)
        self.world_root = self.render.attach_new_node("world_root")

        # ── Audio Manager ──────────────────────────────────────────────────
        self._audio = AudioManager(self)
        self._audio.play_bg_music()

        # ── 2D Interface ───────────────────────────────────────────────────
        self._hud = HUD()

        # ── Build Initial Gameplay World ───────────────────────────────────
        self._build_world()

        # ── Key Bindings ───────────────────────────────────────────────────
        self.accept("escape", self._on_escape)
        self.accept("a", self._on_left)
        self.accept("arrow_left", self._on_left)
        self.accept("d", self._on_right)
        self.accept("arrow_right", self._on_right)
        self.accept("space", self._on_jump)
        self.accept("r", self._on_restart)

        # ── Main Game Loop Task ────────────────────────────────────────────
        self.task_mgr.add(self._update, "gully_run_update")

    # ---------------------------------------------------------------- world build

    def _build_world(self) -> None:
        """Initialize or reset all gameplay entities under world_root."""
        if hasattr(self, "world_root") and not self.world_root.is_empty():
            self.world_root.remove_node()

        self.world_root = self.render.attach_new_node("world_root")

        # Instantiate modular game components
        self._player = Player(self.world_root)
        self._road = RoadManager(self.world_root)
        self._obstacles = ObstacleManager(self.world_root)
        self._police = Police(self.world_root, self._player.y, self._player.target_x)
        self._follow_cam = FollowCamera(self.camera, self._player.root)

        self._score = 0
        self._game_over = False
        self._hud.hide_gameover()

    # ---------------------------------------------------------------- input

    def _on_escape(self) -> None:
        self.userExit()

    def _on_left(self) -> None:
        if not self._game_over:
            if self._player.try_move_left():
                self._audio.play_lane_switch()

    def _on_right(self) -> None:
        if not self._game_over:
            if self._player.try_move_right():
                self._audio.play_lane_switch()

    def _on_jump(self) -> None:
        if not self._game_over:
            if self._player.try_jump():
                self._audio.play_jump()

    def _on_restart(self) -> None:
        if self._game_over:
            self._audio.play_bg_music()
            self._build_world()

    # ---------------------------------------------------------------- game loop

    def _update(self, task: Task) -> int:
        dt = globalClock.get_dt()
        dt = min(dt, 0.05)  # Cap delta time to prevent physics tunnels on lag spikes

        if self._game_over:
            # During game over, pursuer catches the stopped runner
            self._police.catch_player(self._player.y, dt)
            return Task.cont

        # 1. Update Player movement and physics
        self._player.update(dt)

        # 2. Update Endless Road recycling
        self._road.update(self._player.y)

        # 3. Update Obstacles
        self._obstacles.update(self._player.y)

        # 4. Update Police Pursuer
        self._police.update(dt, self._player.y, self._player.root.get_x())

        # 5. Update Lighting / Shadow position tracking
        self._lighting.update(self._player.y)

        # 6. Update Score (Distance traveled in meters)
        self._score = max(0, int(self._player.y * C.SCORE_PER_METER))

        # 7. Update Follow Camera
        self._follow_cam.update(dt)

        # 8. Check Pursuer proximity & update HUD
        police_dist = self._police.distance_to_player(self._player.y)
        self._hud.update(self._score, self._player.run_speed, police_dist)

        # 9. Collision Check
        if self._obstacles.check_collision(self._player):
            self._trigger_game_over()

        return Task.cont

    # ---------------------------------------------------------------- game over

    def _trigger_game_over(self) -> None:
        self._game_over = True
        self._audio.play_gameover()
        self._hud.show_gameover(self._score)
