"""
audio.py
Audio manager for Gully Run.
Handles background music, jump sound effects, lane-change whooshes, and game-over audio.
Includes procedural synthesizer to generate high-quality audio files automatically
if custom sound files haven't been provided yet.
"""
from __future__ import annotations

import math
import struct
import wave
from pathlib import Path
from panda3d.core import Filename
from direct.showbase.ShowBase import ShowBase


AUDIO_DIR = Path(__file__).resolve().parent.parent.parent / "assets" / "audio"


def _generate_wav(path: Path, sample_rate: int, duration: float, generator_fn) -> None:
    """Helper to synthesize a 16-bit mono WAV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    n_samples = int(sample_rate * duration)
    data = bytearray()

    for i in range(n_samples):
        t = i / sample_rate
        sample = generator_fn(t, duration)
        # Clamp to 16-bit signed range [-32767, 32767]
        sample = max(-1.0, min(1.0, sample))
        int_sample = int(sample * 32760)
        data.extend(struct.pack("<h", int_sample))

    with wave.open(str(path), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(data)


def ensure_audio_assets() -> None:
    """Create lightweight default sound assets if not already present."""
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    jump_path = AUDIO_DIR / "jump.wav"
    if not jump_path.exists():
        # Upward pitch sweep (220 Hz -> 680 Hz) with exponential decay
        def jump_gen(t: float, dur: float) -> float:
            freq = 240.0 + 440.0 * (t / dur)
            env = math.exp(-t * 8.0)
            return math.sin(2.0 * math.pi * freq * t) * env * 0.75

        _generate_wav(jump_path, 22050, 0.22, jump_gen)

    gameover_path = AUDIO_DIR / "gameover.wav"
    if not gameover_path.exists():
        # Descending distorted buzzer + siren impact (550 Hz -> 110 Hz)
        def gameover_gen(t: float, dur: float) -> float:
            freq = 520.0 * math.exp(-t * 2.8) + 110.0
            noise = (math.sin(t * 1234.5) % 0.2)
            wave_val = math.sin(2.0 * math.pi * freq * t)
            # Square-wave saturation for punchy arcade hit
            square = 1.0 if wave_val > 0 else -1.0
            env = math.exp(-t * 2.2)
            return (square * 0.5 + noise * 0.2) * env * 0.85

        _generate_wav(gameover_path, 22050, 0.95, gameover_gen)

    switch_path = AUDIO_DIR / "lane_switch.wav"
    if not switch_path.exists():
        # Quick subtle blip for lane transitions (440 Hz -> 320 Hz)
        def switch_gen(t: float, dur: float) -> float:
            freq = 460.0 - 180.0 * (t / dur)
            env = math.exp(-t * 22.0)
            return math.sin(2.0 * math.pi * freq * t) * env * 0.45

        _generate_wav(switch_path, 22050, 0.08, switch_gen)

    music_path = AUDIO_DIR / "bg_music.wav"
    if not music_path.exists():
        # Upbeat rhythmic 4-bar looping arcade bassline & kick beat (128 BPM)
        def music_gen(t: float, dur: float) -> float:
            bpm = 128.0
            beat_dur = 60.0 / bpm
            beat_pos = (t % beat_dur) / beat_dur
            bar_t = t % (beat_dur * 4.0)

            # 1. Bass drum kick on every beat
            kick_env = math.exp(-beat_pos * 18.0)
            kick_freq = 140.0 * math.exp(-beat_pos * 24.0) + 45.0
            kick = math.sin(2.0 * math.pi * kick_freq * beat_pos) * kick_env * 0.7

            # 2. Rhythmic bassline (A minor / Pentatonic notes: A2, C3, D3, E3)
            notes = [110.0, 110.0, 130.8, 146.8, 164.8, 146.8, 130.8, 110.0]
            step = int((t % (beat_dur * 4.0)) / (beat_dur / 2.0)) % len(notes)
            bass_freq = notes[step]
            step_pos = (t % (beat_dur / 2.0)) / (beat_dur / 2.0)
            bass_env = math.exp(-step_pos * 6.0)
            bass = math.sin(2.0 * math.pi * bass_freq * t) * bass_env * 0.45

            # 3. Hi-hat on the off-beats
            hihat_env = 0.0
            if 0.4 < beat_pos < 0.7:
                hp = (beat_pos - 0.4) / 0.3
                hihat_env = math.exp(-hp * 20.0) * (math.sin(t * 8921.0) % 0.3)

            return (kick + bass + hihat_env) * 0.65

        _generate_wav(music_path, 22050, 7.5, music_gen)


class AudioManager:
    """
    Coordinates playback of background music and sound effects.
    Gracefully handles missing audio drivers or muted configurations.
    """

    def __init__(self, base: ShowBase) -> None:
        self.base = base
        self._bg_music = None
        self._sfx_jump = None
        self._sfx_gameover = None
        self._sfx_switch = None

        # Ensure default audio files exist on disk
        ensure_audio_assets()

        # Load audio resources through Panda3D loader using Panda's Virtual File System
        try:
            music_file = AUDIO_DIR / "bg_music.wav"
            if music_file.exists():
                fn = Filename.from_os_specific(str(music_file))
                self._bg_music = base.loader.load_music(fn)
                if self._bg_music:
                    self._bg_music.set_loop(True)
                    self._bg_music.set_volume(0.55)

            jump_file = AUDIO_DIR / "jump.wav"
            if jump_file.exists():
                fn = Filename.from_os_specific(str(jump_file))
                self._sfx_jump = base.loader.load_sfx(fn)
                if self._sfx_jump:
                    self._sfx_jump.set_volume(0.75)

            gameover_file = AUDIO_DIR / "gameover.wav"
            if gameover_file.exists():
                fn = Filename.from_os_specific(str(gameover_file))
                self._sfx_gameover = base.loader.load_sfx(fn)
                if self._sfx_gameover:
                    self._sfx_gameover.set_volume(0.90)

            switch_file = AUDIO_DIR / "lane_switch.wav"
            if switch_file.exists():
                fn = Filename.from_os_specific(str(switch_file))
                self._sfx_switch = base.loader.load_sfx(fn)
                if self._sfx_switch:
                    self._sfx_switch.set_volume(0.40)
        except Exception as e:
            print(f"[Audio Warning] Could not initialize some audio assets: {e}")

    # ---------------------------------------------------------------- controls

    def play_bg_music(self) -> None:
        """Start playing the background music loop."""
        if self._bg_music and self._bg_music.status() != self._bg_music.PLAYING:
            self._bg_music.play()

    def stop_bg_music(self) -> None:
        """Stop background music."""
        if self._bg_music:
            self._bg_music.stop()

    def play_jump(self) -> None:
        """Play jump sound effect."""
        if self._sfx_jump:
            self._sfx_jump.play()

    def play_gameover(self) -> None:
        """Play crash / game-over sound effect and stop music."""
        self.stop_bg_music()
        if self._sfx_gameover:
            self._sfx_gameover.play()

    def play_lane_switch(self) -> None:
        """Play lane-change whoosh sound."""
        if self._sfx_switch:
            self._sfx_switch.play()

    def set_music_volume(self, vol: float) -> None:
        if self._bg_music:
            self._bg_music.set_volume(max(0.0, min(1.0, vol)))

    def set_sfx_volume(self, vol: float) -> None:
        vol = max(0.0, min(1.0, vol))
        for sfx in (self._sfx_jump, self._sfx_gameover, self._sfx_switch):
            if sfx:
                sfx.set_volume(vol)
