"""
game.py
Main Panda3D application class for Gully Run.
Orchestrates game loop, input handling, physics updates, collectibles,
power-ups (Magnet, Turbo, 2X), collision detection, camera tracking,
audio playback, pause menu, and persistent high scores.
"""
from __future__ import annotations

import json
from pathlib import Path

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
from .collectibles import CollectibleManager


HIGHSCORE_PATH = Path(__file__).resolve().parent.parent.parent / "highscore.json"


class GullyRun(ShowBase):
    """
    Top-level Panda3D game application for Gully Run.
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

        # ── Persistent High Score ──────────────────────────────────────────
        self.highscore = self._load_highscore()

        # ── Persistent Scene & Lighting ────────────────────────────────────
        self._lighting = LightingManager(self.render)
        self.world_root = self.render.attach_new_node("world_root")

        # ── Audio Manager ──────────────────────────────────────────────────
        self._audio = AudioManager(self)
        self._audio.play_bg_music()

        # ── 2D Interface ───────────────────────────────────────────────────
        self._hud = HUD(self.highscore)

        # ── Power-Up Timers & Inventory ────────────────────────────────────
        self.coins = 0
        self.magnet_timer = 0.0
        self.turbo_timer = 0.0
        self.multiplier_timer = 0.0
        self.is_paused = False

        # ── Build Initial Gameplay World ───────────────────────────────────
        self._build_world()

        # ── Key Bindings ───────────────────────────────────────────────────
        self.accept("escape", self._on_escape)
        self.accept("a", self._on_left)
        self.accept("arrow_left", self._on_left)
        self.accept("d", self._on_right)
        self.accept("arrow_right", self._on_right)
        self.accept("w", self._on_jump)
        self.accept("arrow_up", self._on_jump)
        self.accept("space", self._on_jump)
        self.accept("s", self._on_crouch)
        self.accept("arrow_down", self._on_crouch)
        self.accept("p", self._on_pause)
        self.accept("r", self._on_restart)

        # ── Main Game Loop Task ────────────────────────────────────────────
        self.task_mgr.add(self._update, "gully_run_update")

    # ---------------------------------------------------------------- highscore

    def _load_highscore(self) -> int:
        try:
            if HIGHSCORE_PATH.exists():
                with open(HIGHSCORE_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return int(data.get("highscore", 0))
        except Exception as e:
            print(f"[Highscore Warning] Could not load: {e}")
        return 0

    def _save_highscore(self) -> None:
        try:
            with open(HIGHSCORE_PATH, "w", encoding="utf-8") as f:
                json.dump({"highscore": self.highscore}, f, indent=2)
        except Exception as e:
            print(f"[Highscore Warning] Could not save: {e}")

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
        self._collectibles = CollectibleManager(self.world_root)
        self._police = Police(self.world_root, self._player.y, self._player.target_x)
        self._follow_cam = FollowCamera(self.camera, self._player.root)

        self._score = 0
        self.coins = 0
        self.magnet_timer = 0.0
        self.turbo_timer = 0.0
        self.multiplier_timer = 0.0
        self.is_paused = False
        self._game_over = False

        self._hud.hide_gameover()
        self._hud.hide_pause()
        self._hud.set_best_score(self.highscore)

    # ---------------------------------------------------------------- input

    def _on_escape(self) -> None:
        self.userExit()

    def _on_pause(self) -> None:
        if not self._game_over:
            self.is_paused = not self.is_paused
            if self.is_paused:
                self._hud.show_pause()
            else:
                self._hud.hide_pause()

    def _on_left(self) -> None:
        if not self._game_over and not self.is_paused:
            if self._player.try_move_left():
                self._audio.play_lane_switch()

    def _on_right(self) -> None:
        if not self._game_over and not self.is_paused:
            if self._player.try_move_right():
                self._audio.play_lane_switch()

    def _on_jump(self) -> None:
        if not self._game_over and not self.is_paused:
            if self._player.try_jump():
                self._audio.play_jump()

    def _on_crouch(self) -> None:
        if not self._game_over and not self.is_paused:
            if self._player.try_crouch():
                self._audio.play_crouch()

    def _on_restart(self) -> None:
        if self._game_over or self.is_paused:
            self._audio.play_bg_music()
            self._build_world()

    # ---------------------------------------------------------------- game loop

    def _update(self, task: Task) -> int:
        if self.is_paused:
            return Task.cont

        dt = globalClock.get_dt()
        dt = min(dt, 0.05)  # Cap delta time to prevent physics tunnels on lag spikes

        if self._game_over:
            # During game over, pursuer catches the stopped runner
            self._police.catch_player(self._player.y, dt)
            return Task.cont

        # 1. Update Power-Up Countdown Timers
        if self.magnet_timer > 0.0:
            self.magnet_timer = max(0.0, self.magnet_timer - dt)
        if self.turbo_timer > 0.0:
            self.turbo_timer = max(0.0, self.turbo_timer - dt)
        if self.multiplier_timer > 0.0:
            self.multiplier_timer = max(0.0, self.multiplier_timer - dt)

        # 2. Player Movement (with Turbo speed boost if active)
        if self.turbo_timer > 0.0:
            # Invincible Turbo boost: +30% sprint speed and glowing scale
            speed_mult = 1.30
            self._player.root.set_color_scale(1.2, 0.9, 0.4, 1.0)
        else:
            speed_mult = 1.00
            self._player.root.set_color_scale(1.0, 1.0, 1.0, 1.0)

        self._player.update(dt * speed_mult)

        # 3. Endless Road recycling
        self._road.update(self._player.y)

        # 4. Obstacles
        self._obstacles.update(self._player.y)

        # 5. Collectibles (Coins & Power-ups)
        is_magnet = (self.magnet_timer > 0.0)
        coins_gained, powerup_type = self._collectibles.update(
            dt, self._player.y, self._player.pos, magnet_active=is_magnet
        )

        if coins_gained > 0:
            if self.multiplier_timer > 0.0:
                coins_gained *= 2
            self.coins += coins_gained
            self._audio.play_coin()

        if powerup_type is not None:
            self._audio.play_powerup()
            if powerup_type == "magnet":
                self.magnet_timer = C.MAGNET_DURATION
            elif powerup_type == "turbo":
                self.turbo_timer = C.TURBO_DURATION
            elif powerup_type == "2x":
                self.multiplier_timer = C.MULTIPLIER_DURATION

        # 6. Police Pursuer (falls behind during Turbo)
        pursuer_speed = self._player.run_speed if self.turbo_timer <= 0.0 else self._player.run_speed * 0.85
        self._police.update(dt, self._player.y, self._player.root.get_x())

        # 7. Lighting / Shadow position tracking
        self._lighting.update(self._player.y)

        # 8. Score Calculation (Distance traveled in meters)
        distance_meters = int(self._player.y * C.SCORE_PER_METER)
        if self.multiplier_timer > 0.0:
            self._score = max(self._score, int(distance_meters * 1.5))
        else:
            self._score = max(0, distance_meters)

        # 9. Follow Camera
        self._follow_cam.update(dt)

        # 10. Active Power-up Banner on HUD
        active_powerup: tuple[str, float] | None = None
        if self.turbo_timer > 0.0:
            active_powerup = ("turbo", self.turbo_timer)
        elif self.magnet_timer > 0.0:
            active_powerup = ("magnet", self.magnet_timer)
        elif self.multiplier_timer > 0.0:
            active_powerup = ("2x", self.multiplier_timer)

        # 11. HUD Update
        police_dist = self._police.distance_to_player(self._player.y)
        self._hud.update(self._score, self.coins, self._player.run_speed, police_dist, active_powerup)

        # 12. Collision Check (Turbo provides complete invincibility!)
        if self.turbo_timer <= 0.0:
            if self._obstacles.check_collision(self._player):
                self._trigger_game_over()

        return Task.cont

    # ---------------------------------------------------------------- game over

    def _trigger_game_over(self) -> None:
        self._game_over = True
        self._audio.play_gameover()

        # Check high score
        is_new_record = False
        if self._score > self.highscore:
            self.highscore = self._score
            self._save_highscore()
            self._hud.set_best_score(self.highscore)
            is_new_record = True

        self._hud.show_gameover(self._score, self.coins, self.highscore, is_new_record)
