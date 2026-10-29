"""
constants.py
Game-wide tunable constants for Gully Run.
"""

# ── Window ──────────────────────────────────────────────────────────────────
WINDOW_TITLE = "Gully Run - 3D Endless Runner"
WIN_W, WIN_H = 1280, 720

# ── Road / Lanes ─────────────────────────────────────────────────────────────
LANE_WIDTH       = 3.2          # world-unit width of one lane
NUM_LANES        = 3
ROAD_WIDTH       = LANE_WIDTH * NUM_LANES   # 9.6 units
ROAD_SEGMENT_LEN = 48.0         # length of one tiled road segment
NUM_SEGMENTS     = 6            # active road segments

# Lane X positions (centred on 0)
LANE_X = [
    -LANE_WIDTH,   # lane 0 – left
    0.0,           # lane 1 – centre
     LANE_WIDTH,   # lane 2 – right
]

# ── Player ───────────────────────────────────────────────────────────────────
PLAYER_START_LANE = 1          # start in centre lane
PLAYER_RUN_SPEED  = 15.0       # forward units / second
SPEED_INCREMENT   = 0.4        # added every SPEED_UP_INTERVAL seconds
SPEED_UP_INTERVAL = 6.0
MAX_RUN_SPEED     = 32.0       # top speed cap
LANE_SWITCH_SPEED = 14.0       # lateral lerp rate
JUMP_VELOCITY     = 10.5       # initial upward velocity
GRAVITY           = -24.0      # downward acceleration

# ── Camera ───────────────────────────────────────────────────────────────────
# Follow camera sits behind and above player
CAM_OFFSET_Y     = -9.5        # behind player
CAM_OFFSET_Z     =  4.8        # above player
CAM_PITCH        = -14.0       # look slightly down
CAM_SMOOTH       = 8.0         # lerp factor for follow

# ── Police pursuer ───────────────────────────────────────────────────────────
# Placed between camera and player so pursuer is prominently visible on screen!
POLICE_BEHIND_DIST   = 4.6     # distance behind player
POLICE_CATCH_DIST    = 1.0     # trigger game over if police overtakes

# ── Obstacles ────────────────────────────────────────────────────────────────
OBSTACLE_START_Y     = 36.0    # safe running distance before first obstacle
OBSTACLE_SPAWN_DIST  = 60.0    # spawn horizon ahead of player
OBSTACLE_MIN_GAP     = 14.0    # distance between consecutive obstacle rows
OBSTACLE_MAX_PER_ROW = 2       # max lanes blocked at once (always leaves >= 1 lane)

# ── Score ────────────────────────────────────────────────────────────────────
SCORE_PER_METER  = 1           # score per world unit travelled

# ── Colours (R, G, B, A) ─────────────────────────────────────────────────────
COL_BG           = (0.04, 0.02, 0.08, 1.0)   # midnight purple sky
COL_ROAD         = (0.10, 0.10, 0.12, 1.0)   # dark asphalt
COL_LANE_MARK    = (0.95, 0.82, 0.15, 1.0)   # Indian street yellow markings
COL_CURB         = (0.80, 0.20, 0.10, 1.0)   # red/white curbs
COL_PLAYER       = (0.00, 0.95, 0.95, 1.0)   # neon cyan runner
COL_POLICE       = (0.85, 0.15, 0.35, 1.0)   # deep crimson/magenta uniform
COL_POLICE_SIREN_A = (1.00, 0.05, 0.20, 1.0) # emergency red
COL_POLICE_SIREN_B = (0.05, 0.40, 1.00, 1.0) # emergency blue
COL_OBSTACLE_LOW = (0.95, 0.45, 0.05, 1.0)   # barricade amber
COL_OBSTACLE_TALL= (0.80, 0.15, 0.15, 1.0)   # stall maroon
COL_BUILDING_A   = (0.14, 0.06, 0.22, 1.0)   # deep plum building
COL_BUILDING_B   = (0.06, 0.14, 0.20, 1.0)   # dark teal building
COL_CHAI         = (0.90, 0.45, 0.10, 1.0)   # warm chai stall orange
COL_RICK_YELLOW  = (0.95, 0.80, 0.05, 1.0)   # classic auto-rickshaw yellow roof
COL_RICK_GREEN   = (0.05, 0.55, 0.25, 1.0)   # classic auto-rickshaw green body
COL_NEON_CYAN    = (0.00, 0.95, 1.00, 1.0)
COL_NEON_MAG     = (1.00, 0.10, 0.70, 1.0)
COL_TEXT         = (1.00, 1.00, 1.00, 1.0)
