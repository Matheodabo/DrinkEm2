# All tunable game values live here — change them without touching game logic.

# Window
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 640
FPS = 60
TITLE = "Party Bird"

# Physics
GRAVITY = 0.5
FLAP_STRENGTH = -9.0
TERMINAL_VELOCITY = 12.0

# Bird
BIRD_X = 80
BIRD_RADIUS = 18

# Pipes
PIPE_WIDTH = 70
PIPE_GAP = 160          # vertical gap between top and bottom pipe
PIPE_SPEED = 3.0
PIPE_SPAWN_INTERVAL = 90  # frames between new pipe pairs
PIPE_COLOR = (34, 139, 34)
PIPE_OUTLINE_COLOR = (20, 90, 20)

# Scrolling ground
GROUND_HEIGHT = 60
GROUND_SPEED = PIPE_SPEED

# Spawning ranges (how far off-screen pipes start and gap center variation)
PIPE_GAP_CENTER_MIN = 150   # pixels from top
PIPE_GAP_CENTER_MAX = WINDOW_HEIGHT - GROUND_HEIGHT - 150

# Collectibles
BEER_RADIUS = 14
BEER_SPAWN_CHANCE = 0.004   # per frame probability once a round is live
CAP_RADIUS = 10
CAP_SPAWN_CHANCE = 0.002

# Colors (placeholders until real art lands)
COLOR_SKY = (113, 197, 207)
COLOR_GROUND = (210, 180, 140)
COLOR_GROUND_STRIPE = (190, 160, 120)
COLOR_BIRD = (255, 220, 50)
COLOR_BIRD_OUTLINE = (200, 160, 20)
COLOR_BEER = (255, 180, 0)
COLOR_CAP = (192, 192, 192)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (220, 50, 50)
COLOR_DARK = (30, 30, 30)
COLOR_OVERLAY = (0, 0, 0, 160)  # RGBA for semi-transparent overlays

# ── Backgrounds ──────────────────────────────────────────────────────────────
# Each entry: id, display_name, and all the colors/params that define it.
# Game.draw() reads the active background dict — no if/else chains needed.

BACKGROUNDS = [
    {
        "id": "day",
        "name": "Sunny Day",
        "sky_top":    (100, 180, 255),
        "sky_bot":    (180, 230, 255),
        "cloud_color": (255, 255, 255),
        "ground":     (120, 200, 80),
        "ground_stripe": (100, 175, 65),
        "pipe":       (50, 160, 50),
        "pipe_outline": (30, 110, 30),
        "sun_moon":   (255, 230, 50),   # sun
        "accent":     (255, 220, 80),
    },
    {
        "id": "night",
        "name": "Night Out",
        "sky_top":    (10, 10, 40),
        "sky_bot":    (30, 30, 80),
        "cloud_color": (60, 60, 100),
        "ground":     (25, 60, 25),
        "ground_stripe": (20, 45, 20),
        "pipe":       (20, 100, 20),
        "pipe_outline": (10, 60, 10),
        "sun_moon":   (240, 240, 200),  # moon
        "accent":     (150, 150, 255),
    },
    {
        "id": "sunset",
        "name": "Golden Hour",
        "sky_top":    (220, 80, 40),
        "sky_bot":    (255, 180, 80),
        "cloud_color": (255, 140, 80),
        "ground":     (160, 100, 40),
        "ground_stripe": (130, 80, 30),
        "pipe":       (180, 90, 30),
        "pipe_outline": (120, 55, 15),
        "sun_moon":   (255, 220, 50),
        "accent":     (255, 100, 50),
    },
]

DEFAULT_BACKGROUND = "day"
