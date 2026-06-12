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
