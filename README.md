# Gully Run 🏃 – Playable Prototype

A stylized 3-D endless runner set in a fictional Indian city built with **Python + Panda3D**.

---

## Requirements

| Tool | Version |
|------|---------|
| Python | ≥ 3.10 |
| Panda3D | ≥ 1.10.14 |

---

## Setup

```bash
# 1. Clone / enter the project folder
cd gully-run

# 2. (Recommended) Create and activate a virtual environment
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## Run the game

```bash
python main.py
```

Or, if you've installed the package (`pip install -e .`):

```bash
python -m gully_run.game
```

---

## Controls

| Key | Action |
|-----|--------|
| **A** / **←** | Move left one lane |
| **D** / **→** | Move right one lane |
| **Space** | Jump |
| **R** | Restart (after game-over) |
| **Esc** | Quit |

---

## Project layout

```
gully-run/
├── main.py                   ← entry-point
├── pyproject.toml
├── requirements.txt
└── src/
    └── gully_run/
        ├── __init__.py
        ├── constants.py      ← all tunable values in one place
        ├── game.py           ← ShowBase application / game loop
        ├── player.py         ← player movement & jump physics
        ├── camera.py         ← smooth follow camera
        ├── road.py           ← endless scrolling road + scenery
        ├── obstacles.py      ← obstacle spawning & AABB collision
        ├── police.py         ← police pursuer AI
        ├── hud.py            ← score, speed readout & game-over overlay
        └── lighting.py       ← ambient / directional / neon point lights
```

---

## Visual style

- Dark purple sky background
- Coloured box stand-ins for: player (cyan), police (magenta), obstacles (amber)
- Street scenery: buildings (purple/teal), chai stalls (orange), auto-rickshaws (cyan)
- Neon accent strips on buildings; lane markings in yellow

---

## Roadmap

- [ ] Replace box placeholders with proper 3-D models / rigged character
- [ ] Add sound effects and background music
- [ ] Animated police lights / siren
- [ ] Coin / power-up collectables
- [ ] High-score persistence
- [ ] Android packaging with `p3d-android`

