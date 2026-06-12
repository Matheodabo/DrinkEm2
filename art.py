"""Shared placeholder vector art, drawn directly with pygame primitives.

Keeping these in one place means the beer mug looks identical in the HUD,
as an in-flight collectible, and on the sip-award screen. Swap these for
real sprites later without touching game logic.
"""
import pygame
import config


def draw_beer(surface, cx, cy, r=config.BEER_RADIUS):
    """Draw a little beer mug centered on (cx, cy). `r` scales the whole thing."""
    cx, cy = int(cx), int(cy)
    w = int(r * 1.5)
    h = int(r * 2.0)
    left = cx - w // 2
    top = cy - h // 2

    # mug body (glass + amber fill)
    body = pygame.Rect(left, top + r // 2, w, h - r // 2)
    pygame.draw.rect(surface, config.COLOR_BEER_GLASS, body, border_radius=3)
    pygame.draw.rect(surface, config.COLOR_BEER_GLASS_DARK, body, 2, border_radius=3)

    # handle on the right
    handle = pygame.Rect(body.right - 2, body.top + 4, max(6, r), max(6, h - r))
    pygame.draw.ellipse(surface, config.COLOR_BEER_GLASS_DARK, handle, 3)

    # foam head
    foam = pygame.Rect(left - 2, top, w + 4, r)
    pygame.draw.ellipse(surface, config.COLOR_BEER_FOAM, foam)
    pygame.draw.ellipse(surface, (225, 220, 210), foam, 1)

    # glass highlight stripe
    hl = pygame.Rect(left + 3, body.top + 3, max(2, w // 6), body.height - 8)
    pygame.draw.rect(surface, config.COLOR_BEER_HIGHLIGHT, hl, border_radius=2)
