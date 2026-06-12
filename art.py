"""Shared placeholder vector art, drawn directly with pygame primitives.

Two families live here:
  * collectibles  — draw_beer / draw_cap / draw_cig_box / draw_fidget
  * the bird + accessories — draw_bird_base, draw_dressed_bird, and one
    draw_<item> per cosmetic (hats, eyewear, neck, face, legs).

Keeping every sprite in one module means an item looks identical in the HUD,
as an in-flight pickup, on a shop card, and worn by the bird in-game. Swap
these for real sprites later without touching game/scene logic — just keep
the function signatures.
"""
import math
import pygame
import config

C = config  # shorthand


# ─────────────────────────────────────────────────────────── collectibles ───
def draw_beer(surface, cx, cy, r=config.COLLECTIBLE_RADIUS):
    """A little beer mug centered on (cx, cy)."""
    cx, cy = int(cx), int(cy)
    w = int(r * 1.5)
    h = int(r * 2.0)
    left = cx - w // 2
    top = cy - h // 2
    body = pygame.Rect(left, top + r // 2, w, h - r // 2)
    pygame.draw.rect(surface, C.COLOR_BEER_GLASS, body, border_radius=3)
    pygame.draw.rect(surface, C.COLOR_BEER_GLASS_DARK, body, 2, border_radius=3)
    handle = pygame.Rect(body.right - 2, body.top + 4, max(6, r), max(6, h - r))
    pygame.draw.ellipse(surface, C.COLOR_BEER_GLASS_DARK, handle, 3)
    foam = pygame.Rect(left - 2, top, w + 4, r)
    pygame.draw.ellipse(surface, C.COLOR_BEER_FOAM, foam)
    pygame.draw.ellipse(surface, (225, 220, 210), foam, 1)
    hl = pygame.Rect(left + 3, body.top + 3, max(2, w // 6), body.height - 8)
    pygame.draw.rect(surface, C.COLOR_BEER_HIGHLIGHT, hl, border_radius=2)


def draw_cap(surface, cx, cy, r=config.COLLECTIBLE_RADIUS):
    """A crimped bottle cap (the currency)."""
    cx, cy = int(cx), int(cy)
    rad = max(6, int(r * 0.9))
    # crimped edge
    for i in range(12):
        a = math.tau * i / 12
        x = cx + int(math.cos(a) * rad)
        y = cy + int(math.sin(a) * rad)
        pygame.draw.circle(surface, (150, 30, 30), (x, y), 2)
    pygame.draw.circle(surface, (205, 60, 60), (cx, cy), rad)
    pygame.draw.circle(surface, (150, 30, 30), (cx, cy), rad, 2)
    pygame.draw.circle(surface, (235, 110, 110), (cx, cy), rad - 4)
    pygame.draw.circle(surface, (255, 240, 210), (cx, cy), 2)


def draw_cig_box(surface, cx, cy, r=config.COLLECTIBLE_RADIUS):
    """A small cigarette box with a few sticks poking out."""
    cx, cy = int(cx), int(cy)
    w = int(r * 1.4)
    h = int(r * 1.8)
    box = pygame.Rect(cx - w // 2, cy - h // 2, w, h)
    # cigarettes first so the box overlaps their base
    for i in range(3):
        x = box.left + 4 + i * ((w - 8) // 2)
        pygame.draw.rect(surface, (250, 250, 245), (x, box.top - 6, 4, 9))
        pygame.draw.rect(surface, (245, 160, 50), (x, box.top - 6, 4, 3))
    pygame.draw.rect(surface, (235, 235, 240), box, border_radius=2)
    pygame.draw.rect(surface, (120, 120, 130), box, 2, border_radius=2)
    pygame.draw.rect(surface, (200, 45, 45), (box.left, box.top, w, h // 3),
                     border_top_left_radius=2, border_top_right_radius=2)


def draw_fidget(surface, cx, cy, r=config.COLLECTIBLE_RADIUS, angle=0.0):
    """A three-lobed fidget spinner; pass an angle to spin it."""
    cx, cy = int(cx), int(cy)
    arm = int(r * 0.9)
    lobe = max(4, int(r * 0.5))
    colors = [(230, 60, 60), (60, 160, 230), (235, 200, 60)]
    for i in range(3):
        a = angle + math.tau * i / 3
        x = cx + int(math.cos(a) * arm)
        y = cy + int(math.sin(a) * arm)
        pygame.draw.circle(surface, colors[i], (x, y), lobe)
        pygame.draw.circle(surface, (40, 40, 40), (x, y), lobe, 1)
        pygame.draw.circle(surface, (230, 230, 230), (x, y), max(2, lobe // 3))
    pygame.draw.circle(surface, (90, 90, 95), (cx, cy), max(4, int(r * 0.45)))
    pygame.draw.circle(surface, (200, 200, 205), (cx, cy), max(2, int(r * 0.26)))


# ───────────────────────────────────────────────────────────── the bird ───
def draw_bird_base(surface, cx, cy, r, angle=0.0):
    cx, cy = int(cx), int(cy)
    pygame.draw.circle(surface, C.COLOR_BIRD, (cx, cy), r)
    pygame.draw.circle(surface, C.COLOR_BIRD_OUTLINE, (cx, cy), r, 2)
    # beak
    beak = [(cx + r - 2, cy - 3), (cx + r + 7, cy), (cx + r - 2, cy + 3)]
    pygame.draw.polygon(surface, (240, 140, 30), beak)
    pygame.draw.polygon(surface, (200, 110, 20), beak, 1)
    # eye (tracks tilt a little)
    ex = cx + int(r * 0.4 * math.cos(math.radians(-angle)))
    ey = cy + int(r * 0.4 * math.sin(math.radians(-angle))) - 3
    pygame.draw.circle(surface, C.COLOR_WHITE, (ex, ey), 5)
    pygame.draw.circle(surface, C.COLOR_BLACK, (ex + 1, ey), 2)
    # wing hint
    wx = cx - int(r * 0.3)
    wy = cy + int(r * 0.2)
    pygame.draw.ellipse(surface, C.COLOR_BIRD_OUTLINE, (wx - 8, wy - 4, 14, 8))


# accessory draw order in front of the body (legs are drawn behind it)
_FRONT_SLOT_ORDER = ("neck", "face", "eyes", "hat")


def draw_dressed_bird(surface, cx, cy, r, cosmetics, angle=0.0):
    """Draw the bird wearing a list of cosmetic dicts (each with 'slot' & 'draw')."""
    cx, cy = int(cx), int(cy)
    for c in cosmetics:
        if c.get("slot") == "legs":
            _draw_item(surface, c["draw"], cx, cy, r)
    draw_bird_base(surface, cx, cy, r, angle)
    for slot in _FRONT_SLOT_ORDER:
        for c in cosmetics:
            if c.get("slot") == slot:
                _draw_item(surface, c["draw"], cx, cy, r)


def _draw_item(surface, name, cx, cy, r):
    fn = globals().get("draw_" + name)
    if fn is not None:
        fn(surface, cx, cy, r)


# ─────────────────────────────────────────────────────────── accessories ───
# Each takes (surface, cx, cy, r) where (cx,cy) is the bird center, r its radius.

def draw_top_hat(surface, cx, cy, r):
    top = cy - r
    crown = pygame.Rect(cx - int(r * 0.7), top - int(r * 1.15), int(r * 1.4), int(r * 1.15))
    brim = pygame.Rect(cx - int(r * 1.1), top - 2, int(r * 2.2), 7)
    pygame.draw.ellipse(surface, (25, 25, 30), brim)
    pygame.draw.rect(surface, (25, 25, 30), crown, border_radius=2)
    band = pygame.Rect(crown.left, crown.bottom - 8, crown.width, 6)
    pygame.draw.rect(surface, (190, 40, 40), band)


def draw_party_hat(surface, cx, cy, r):
    top = cy - r
    apex = (cx, top - int(r * 1.35))
    left = (cx - int(r * 0.7), top + 3)
    right = (cx + int(r * 0.7), top + 3)
    pygame.draw.polygon(surface, (80, 160, 230), [apex, left, right])
    pygame.draw.polygon(surface, (40, 110, 180), [apex, left, right], 1)
    pygame.draw.line(surface, (255, 220, 80),
                     (cx - int(r * 0.3), top - int(r * 0.3)),
                     (cx + int(r * 0.15), top - int(r * 0.55)), 3)
    pygame.draw.line(surface, (255, 120, 180),
                     (cx - int(r * 0.05), top - int(r * 0.05)),
                     (cx + int(r * 0.4), top - int(r * 0.25)), 3)
    pygame.draw.circle(surface, (255, 120, 180), apex, 5)


def draw_cap_hat(surface, cx, cy, r):
    top = cy - r
    dome = pygame.Rect(cx - int(r * 0.8), top - int(r * 0.7), int(r * 1.6), int(r * 0.95))
    pygame.draw.ellipse(surface, (200, 50, 50), dome)
    pygame.draw.ellipse(surface, (150, 30, 30), dome, 1)
    brim = [(cx + int(r * 0.35), top + 3), (cx + int(r * 1.25), top + 5),
            (cx + int(r * 0.35), top + 10)]
    pygame.draw.polygon(surface, (170, 35, 35), brim)
    pygame.draw.circle(surface, (120, 20, 20), (cx, top - int(r * 0.62)), 3)


def draw_crown(surface, cx, cy, r):
    top = cy - r + 2
    base = pygame.Rect(cx - int(r * 0.7), top - 6, int(r * 1.4), 8)
    pts = [(cx - int(r * 0.7), top - 6), (cx - int(r * 0.7), top - 16),
           (cx - int(r * 0.35), top - 8), (cx, top - 20),
           (cx + int(r * 0.35), top - 8), (cx + int(r * 0.7), top - 16),
           (cx + int(r * 0.7), top - 6)]
    pygame.draw.polygon(surface, (240, 200, 40), pts)
    pygame.draw.rect(surface, (240, 200, 40), base)
    pygame.draw.rect(surface, (200, 160, 20), base, 1)
    pygame.draw.circle(surface, (220, 60, 60), (cx, top - 9), 2)


def draw_glasses(surface, cx, cy, r):
    ey = cy - 4
    rad = max(5, int(r * 0.42))
    front = (cx + int(r * 0.5), ey)
    back = (cx - int(r * 0.15), ey)
    for c in (front, back):
        pygame.draw.circle(surface, (40, 40, 40), c, rad, 2)
    pygame.draw.line(surface, (40, 40, 40), (back[0] + rad, ey), (front[0] - rad, ey), 2)
    pygame.draw.line(surface, (40, 40, 40), (back[0] - rad, ey), (cx - r, ey - 2), 2)


def draw_sunglasses(surface, cx, cy, r):
    ey = cy - 4
    rad = max(5, int(r * 0.45))
    front = (cx + int(r * 0.5), ey)
    back = (cx - int(r * 0.12), ey)
    for c in (front, back):
        pygame.draw.circle(surface, (20, 20, 30), c, rad)
        pygame.draw.circle(surface, (70, 70, 90), c, rad, 1)
        pygame.draw.line(surface, (120, 120, 160),
                         (c[0] - rad // 2, ey - rad // 2), (c[0] - rad // 3, ey), 1)
    pygame.draw.line(surface, (20, 20, 30), (back[0] + rad, ey), (front[0] - rad, ey), 3)
    pygame.draw.line(surface, (20, 20, 30), (back[0] - rad, ey), (cx - r, ey - 2), 2)


def draw_goggles(surface, cx, cy, r):
    ey = cy - 3
    rad = max(6, int(r * 0.5))
    front = (cx + int(r * 0.45), ey)
    back = (cx - int(r * 0.15), ey)
    pygame.draw.line(surface, (120, 40, 40), (front[0], ey - rad), (cx - r, ey - rad + 2), 4)
    pygame.draw.line(surface, (120, 40, 40), (front[0], ey + rad), (cx - r, ey + rad - 2), 4)
    for c in (front, back):
        pygame.draw.circle(surface, (160, 200, 220), c, rad)
        pygame.draw.circle(surface, (80, 80, 90), c, rad, 3)
    pygame.draw.line(surface, (80, 80, 90), (back[0] + rad, ey), (front[0] - rad, ey), 3)


def draw_bowtie(surface, cx, cy, r):
    ny = cy + int(r * 0.85)
    nx = cx + int(r * 0.2)
    left = [(nx, ny), (nx - 11, ny - 7), (nx - 11, ny + 7)]
    right = [(nx, ny), (nx + 11, ny - 7), (nx + 11, ny + 7)]
    pygame.draw.polygon(surface, (200, 40, 40), left)
    pygame.draw.polygon(surface, (200, 40, 40), right)
    pygame.draw.circle(surface, (150, 20, 20), (nx, ny), 3)


def draw_chain(surface, cx, cy, r):
    ny = cy + int(r * 0.7)
    rect = pygame.Rect(cx - int(r * 0.7), ny - 8, int(r * 1.4), 22)
    pygame.draw.arc(surface, (240, 210, 60), rect, 3.4, 6.0, 3)
    pygame.draw.circle(surface, (240, 210, 60), (cx + int(r * 0.05), ny + 10), 3)


def draw_mustache(surface, cx, cy, r):
    my = cy + 5
    mx = cx + int(r * 0.5)
    pygame.draw.ellipse(surface, (70, 45, 25), (mx - 10, my - 3, 10, 7))
    pygame.draw.ellipse(surface, (70, 45, 25), (mx, my - 3, 10, 7))


def draw_pants(surface, cx, cy, r):
    py = cy + int(r * 0.55)
    body = pygame.Rect(cx - int(r * 0.6), py, int(r * 1.2), int(r * 0.95))
    pygame.draw.rect(surface, (60, 90, 180), body, border_radius=3)
    pygame.draw.rect(surface, (40, 60, 130), body, 1, border_radius=3)
    pygame.draw.line(surface, (40, 60, 130), (cx, py + 5), (cx, body.bottom), 2)
    pygame.draw.line(surface, (60, 90, 180), (cx - int(r * 0.4), py), (cx - int(r * 0.3), cy - 2), 3)
    pygame.draw.line(surface, (60, 90, 180), (cx + int(r * 0.4), py), (cx + int(r * 0.3), cy - 2), 3)
