import pygame
import math
import config

# Thumbnail dimensions
THUMB_W = 120
THUMB_H = 160
THUMB_GAP = 24
CARD_RADIUS = 12


def _lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def _draw_sky_gradient(surface, rect, top_color, bot_color):
    for y in range(rect.height):
        t = y / max(rect.height - 1, 1)
        color = _lerp_color(top_color, bot_color, t)
        pygame.draw.line(surface, color, (rect.x, rect.y + y), (rect.x + rect.width - 1, rect.y + y))


def _build_thumbnail(bg: dict) -> pygame.Surface:
    surf = pygame.Surface((THUMB_W, THUMB_H))

    ground_h = 28
    sky_rect = pygame.Rect(0, 0, THUMB_W, THUMB_H - ground_h)
    _draw_sky_gradient(surf, sky_rect, bg["sky_top"], bg["sky_bot"])

    # sun / moon
    pygame.draw.circle(surf, bg["sun_moon"], (THUMB_W - 22, 22), 12)

    # clouds (simple ellipses)
    cc = bg["cloud_color"]
    for cx, cy, rw, rh in [(30, 30, 20, 10), (60, 20, 14, 7), (80, 35, 18, 9)]:
        pygame.draw.ellipse(surf, cc, (cx - rw, cy - rh, rw * 2, rh * 2))

    # pipes (one pair)
    pw = 16
    gap = 44
    px = THUMB_W // 2 - pw // 2
    mid = (THUMB_H - ground_h) // 2
    top_h = mid - gap // 2
    bot_y = mid + gap // 2
    bot_h = (THUMB_H - ground_h) - bot_y
    pygame.draw.rect(surf, bg["pipe"], (px, 0, pw, top_h))
    pygame.draw.rect(surf, bg["pipe_outline"], (px, 0, pw, top_h), 2)
    # pipe cap top
    pygame.draw.rect(surf, bg["pipe"], (px - 3, top_h - 8, pw + 6, 8))
    pygame.draw.rect(surf, bg["pipe_outline"], (px - 3, top_h - 8, pw + 6, 8), 2)
    pygame.draw.rect(surf, bg["pipe"], (px, bot_y, pw, bot_h))
    pygame.draw.rect(surf, bg["pipe_outline"], (px, bot_y, pw, bot_h), 2)
    # pipe cap bottom
    pygame.draw.rect(surf, bg["pipe"], (px - 3, bot_y, pw + 6, 8))
    pygame.draw.rect(surf, bg["pipe_outline"], (px - 3, bot_y, pw + 6, 8), 2)

    # bird
    bx, by = px - 22, mid
    pygame.draw.circle(surf, config.COLOR_BIRD, (bx, by), 9)
    pygame.draw.circle(surf, config.COLOR_BIRD_OUTLINE, (bx, by), 9, 2)

    # ground
    gy = THUMB_H - ground_h
    pygame.draw.rect(surf, bg["ground"], (0, gy, THUMB_W, ground_h))
    stripe_w = 16
    for sx in range(0, THUMB_W, stripe_w):
        pygame.draw.rect(surf, bg["ground_stripe"], (sx, gy + 4, stripe_w // 2, ground_h - 4))

    return surf


class BackgroundSelect:
    """Pre-round scene: choose one of three backgrounds with left/right arrows."""

    def __init__(self, screen, save_data):
        self.screen = screen
        self.save_data = save_data

        self.options = config.BACKGROUNDS
        # restore last choice or fall back to first
        default_id = save_data.get("last_bg", config.DEFAULT_BACKGROUND)
        self.selected = next(
            (i for i, b in enumerate(self.options) if b["id"] == default_id), 0
        )

        self.thumbnails = [_build_thumbnail(bg) for bg in self.options]
        self.font_title = pygame.font.SysFont(None, 52)
        self.font_name = pygame.font.SysFont(None, 34)
        self.font_hint = pygame.font.SysFont(None, 26)

        # animation
        self._anim_t = 0.0          # 0..1, slides toward selected card
        self._anim_from = self.selected
        self._confirmed = False
        self._edit_players = False

        # pulse for confirm button
        self._pulse = 0.0

    # ----------------------------------------------------------------- input
    def handle_input(self, event):
        if self._confirmed:
            return
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self._move(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._move(1)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._confirm()
            elif event.key == pygame.K_p:
                self._edit_players = True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            # check if a card was clicked
            for i, rect in enumerate(self._card_rects()):
                if rect.collidepoint(mx, my):
                    if i == self.selected:
                        self._confirm()
                    else:
                        self._move_to(i)
                    break

    def _move(self, delta):
        self._move_to((self.selected + delta) % len(self.options))

    def _move_to(self, idx):
        if idx == self.selected:
            return
        self._anim_from = self.selected
        self.selected = idx
        self._anim_t = 0.0

    def _confirm(self):
        self.save_data["last_bg"] = self.options[self.selected]["id"]
        self._confirmed = True

    # ---------------------------------------------------------------- update
    def update(self):
        if self._anim_t < 1.0:
            self._anim_t = min(1.0, self._anim_t + 0.12)
        self._pulse = (self._pulse + 0.05) % (2 * math.pi)

    # ------------------------------------------------------------------ draw
    def draw(self):
        self._draw_bg_preview()
        self._draw_overlay()
        self._draw_cards()
        self._draw_title()
        self._draw_hint()

    def _draw_bg_preview(self):
        """Full-screen tinted preview of the selected background."""
        bg = self.options[self.selected]
        # gradient sky fill
        for y in range(config.WINDOW_HEIGHT):
            t = y / (config.WINDOW_HEIGHT - 1)
            color = _lerp_color(bg["sky_top"], bg["sky_bot"], t)
            pygame.draw.line(self.screen, color, (0, y), (config.WINDOW_WIDTH - 1, y))
        # ground strip
        gy = config.WINDOW_HEIGHT - config.GROUND_HEIGHT
        pygame.draw.rect(self.screen, bg["ground"],
                         (0, gy, config.WINDOW_WIDTH, config.GROUND_HEIGHT))

    def _draw_overlay(self):
        """Dark vignette so the UI pops."""
        ov = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 80))
        self.screen.blit(ov, (0, 0))

    def _card_rects(self):
        """Return Rect for each card centered on screen."""
        n = len(self.options)
        total_w = n * THUMB_W + (n - 1) * THUMB_GAP
        start_x = (config.WINDOW_WIDTH - total_w) // 2
        cy = config.WINDOW_HEIGHT // 2 + 20
        rects = []
        for i in range(n):
            x = start_x + i * (THUMB_W + THUMB_GAP)
            rects.append(pygame.Rect(x, cy - THUMB_H // 2, THUMB_W, THUMB_H))
        return rects

    def _draw_cards(self):
        rects = self._card_rects()
        for i, (bg, thumb, rect) in enumerate(zip(self.options, self.thumbnails, rects)):
            is_sel = (i == self.selected)

            # lift selected card
            lift = -16 if is_sel else 0
            draw_rect = rect.move(0, lift)

            # shadow
            shadow_surf = pygame.Surface((THUMB_W + 8, THUMB_H + 8), pygame.SRCALPHA)
            shadow_surf.fill((0, 0, 0, 100 if is_sel else 50))
            self.screen.blit(shadow_surf, (draw_rect.x - 4, draw_rect.y + 6))

            # card background (rounded via clip trick)
            card_surf = pygame.Surface((THUMB_W, THUMB_H), pygame.SRCALPHA)
            card_surf.blit(thumb, (0, 0))
            # dim unselected
            if not is_sel:
                dim = pygame.Surface((THUMB_W, THUMB_H), pygame.SRCALPHA)
                dim.fill((0, 0, 0, 100))
                card_surf.blit(dim, (0, 0))

            self.screen.blit(card_surf, draw_rect.topleft)

            # selected border (pulsing glow)
            if is_sel:
                glow = int(30 + 20 * math.sin(self._pulse))
                border_color = (255, 220 + glow, 50)
                pygame.draw.rect(self.screen, border_color, draw_rect, 3)

            # name label below card
            name_surf = self.font_name.render(bg["name"], True,
                                               config.COLOR_WHITE if is_sel else (180, 180, 180))
            name_rect = name_surf.get_rect(centerx=draw_rect.centerx, top=draw_rect.bottom + 8)
            self.screen.blit(name_surf, name_rect)

    def _draw_title(self):
        title = self.font_title.render("Choose Your Stage", True, config.COLOR_WHITE)
        shadow = self.font_title.render("Choose Your Stage", True, config.COLOR_DARK)
        tx = config.WINDOW_WIDTH // 2
        ty = 60
        self.screen.blit(shadow, shadow.get_rect(centerx=tx + 2, top=ty + 2))
        self.screen.blit(title, title.get_rect(centerx=tx, top=ty))

    def _draw_hint(self):
        pulse_alpha = int(180 + 60 * math.sin(self._pulse))
        if self._confirmed:
            text = "Loading..."
        else:
            text = "← → to browse   Space / Click to play"
        hint = self.font_hint.render(text, True, config.COLOR_WHITE)
        hint.set_alpha(pulse_alpha)
        self.screen.blit(hint, hint.get_rect(centerx=config.WINDOW_WIDTH // 2,
                                              bottom=config.WINDOW_HEIGHT - 20))

        # roster-edit shortcut
        if not self._confirmed:
            ptext = self.font_hint.render("P — edit players", True, config.COLOR_WHITE)
            ptext.set_alpha(150)
            self.screen.blit(ptext, ptext.get_rect(centerx=config.WINDOW_WIDTH // 2,
                                                    bottom=config.WINDOW_HEIGHT - 48))

    # --------------------------------------------------------- scene protocol
    def next_scene(self):
        if self._edit_players:
            return ("player_setup", None)
        if self._confirmed:
            return ("game", self.options[self.selected])
        return None
