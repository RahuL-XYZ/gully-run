"""
constants.py
Game-wide tunable constants for Gully Run.
"""

# ── Window ──────────────────────────────────────────────────────────────────
WINDOW_TITLE = "Gully Run"
WIN_W, WIN_H = 1280, 720

# ── Road / Lanes ─────────────────────────────────────────────────────────────
LANE_WIDTH      = 3.0          # world-unit width of one lane
NUM_LANES       = 3
ROAD_WIDTH      = LANE_WIDTH * NUM_LANES   # 9 units
ROAD_SEGMENT_LEN = 40.0        # length of one tiled road segment
NUM_SEGMENTS    = 6            # how many segments to keep alive at once

# Lane X positions (centred on 0)
LANE_X = [
    -LANE_WIDTH,   # lane 0 – left
    0.0,           # lane 1 – centre
     LANE_WIDTH,   # lane 2 – right
]

# ── Player ───────────────────────────────────────────────────────────────────
PLAYER_START_LANE = 1          # start in centre lane
PLAYER_RUN_SPEED  = 14.0       # forward units / second  (increases over time)
SPEED_INCREMENT   = 0.5        # added every SPEED_UP_INTERVAL seconds
SPEED_UP_INTERVAL = 5.0
LANE_SWITCH_SPEED = 12.0       # lateral units / second while sliding
JUMP_VELOCITY     = 10.0       # initial upward velocity
GRAVITY           = -22.0      # downward acceleration

# ── Camera ───────────────────────────────────────────────────────────────────
CAM_OFFSET_Y     = -10.0       # behind player (Panda3D Y = forward)
CAM_OFFSET_Z     =  5.0        # above player
CAM_PITCH        = -15.0       # look slightly down
CAM_SMOOTH       = 6.0         # lerp factor

# ── Obstacles ────────────────────────────────────────────────────────────────
OBSTACLE_SPAWN_DIST  = 50.0    # units ahead of player
OBSTACLE_MIN_GAP     = 12.0    # min distance between consecutive spawns
OBSTACLE_MAX_PER_ROW = 2       # max lanes blocked at once

# ── Police pursuer ───────────────────────────────────────────────────────────
POLICE_BEHIND_DIST   = 12.0    # starts this far behind player
POLICE_CATCH_DIST    = 1.5     # if closer than this → game over

# ── Score ────────────────────────────────────────────────────────────────────
SCORE_PER_METER  = 1           # score per world unit travelled

# ── Colours (R, G, B, A) 0-1 ─────────────────────────────────────────────────
COL_BG           = (0.05, 0.03, 0.10, 1)   # very dark purple sky
COL_ROAD         = (0.12, 0.12, 0.14, 1)
COL_LANE_MARK    = (0.9,  0.85, 0.2,  1)   # yellow lane markings
COL_PLAYER       = (0.0,  1.0,  1.0,  1)   # cyan
COL_POLICE       = (1.0,  0.2,  1.0,  1)   # magenta
COL_OBSTACLE     = (1.0,  0.5,  0.0,  1)   # amber
COL_BUILDING_A   = (0.15, 0.05, 0.25, 1)   # deep purple
COL_BUILDING_B   = (0.05, 0.15, 0.20, 1)   # dark teal
COL_CHAI         = (0.8,  0.4,  0.0,  1)   # warm orange chai stall
COL_NEON_CYAN    = (0.0,  1.0,  1.0,  1)
COL_NEON_MAG     = (1.0,  0.0,  1.0,  1)
COL_TEXT         = (1.0,  1.0,  1.0,  1)
COL_GAMEOVER_BG  = (0.0,  0.0,  0.0,  0.6)

