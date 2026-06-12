import pygame
import random
import math
import config
import art


def _lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


class Bird:
    def __init__(self):
        self.x = config.BIRD_X
        self.y = config.WINDOW_HEIGHT // 2
        self.vel_y = 0.0
        self.alive = True
        self.angle = 0.0

    def flap(self):
        self.vel_y = config.FLAP_STRENGTH

    def update(self):
        self.vel_y = min(self.vel_y + config.GRAVITY, config.TERMINAL_VELOCITY)
        self.y += self.vel_y
        target_angle = max(-30, min(90, self.vel_y * 4))
        self.angle += (target_angle - self.angle) * 0.2

    def get_rect(self):
        r = config.BIRD_RADIUS
        return pygame.Rect(self.x - r + 4, self.y - r + 4, r * 2 - 8, r * 2 - 8)

    def draw(self, surface):
        cx, cy = int(self.x), int(self.y)
        r = config.BIRD_RADIUS
        pygame.draw.circle(surface, config.COLOR_BIRD, (cx, cy), r)
        pygame.draw.circle(surface, config.COLOR_BIRD_OUTLINE, (cx, cy), r, 2)
        ex = cx + int(r * 0.4 * math.cos(math.radians(-self.angle)))
        ey = cy + int(r * 0.4 * math.sin(math.radians(-self.angle))) - 3
        pygame.draw.circle(surface, config.COLOR_WHITE, (ex, ey), 5)
        pygame.draw.circle(surface, config.COLOR_BLACK, (ex + 1, ey), 2)
        wx = cx - int(r * 0.3)
        wy = cy + int(r * 0.2)
        pygame.draw.ellipse(surface, config.COLOR_BIRD_OUTLINE, (wx - 8, wy - 4, 14, 8))


class Pipe:
    def __init__(self, x, bg):
        self.bg = bg
        gap_center = random.randint(config.PIPE_GAP_CENTER_MIN, config.PIPE_GAP_CENTER_MAX)
        half = config.PIPE_GAP // 2
        self.top_rect = pygame.Rect(x, 0, config.PIPE_WIDTH, gap_center - half)
        self.bot_rect = pygame.Rect(x, gap_center + half,
                                    config.PIPE_WIDTH,
                                    config.WINDOW_HEIGHT - (gap_center + half))
        self.passed = False

    def update(self):
        self.top_rect.x -= int(config.PIPE_SPEED)
        self.bot_rect.x -= int(config.PIPE_SPEED)

    def is_off_screen(self):
        return self.top_rect.right < 0

    def collides(self, bird_rect):
        return bird_rect.colliderect(self.top_rect) or bird_rect.colliderect(self.bot_rect)

    def draw(self, surface):
        pc = self.bg["pipe"]
        po = self.bg["pipe_outline"]
        for rect in (self.top_rect, self.bot_rect):
            pygame.draw.rect(surface, pc, rect)
            pygame.draw.rect(surface, po, rect, 2)
            is_top = (rect.top == 0)
            cap_y = rect.bottom - 20 if is_top else rect.top
            cap = pygame.Rect(rect.x - 4, cap_y, config.PIPE_WIDTH + 8, 20)
            pygame.draw.rect(surface, pc, cap)
            pygame.draw.rect(surface, po, cap, 2)


class Beer:
    """A collectible beer mug that drifts left and bobs gently."""

    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)        # base height; visual bobs around this
        self.bob = random.uniform(0, math.tau)
        self.collected = False

    def update(self):
        self.x -= config.PIPE_SPEED
        self.bob += 0.12

    def render_y(self):
        return self.y + math.sin(self.bob) * 4

    def is_off_screen(self):
        return self.x < -2 * config.BEER_RADIUS

    def get_rect(self):
        r = config.BEER_RADIUS
        w = int(r * 1.6)
        h = int(r * 2.2)
        return pygame.Rect(int(self.x - w / 2), int(self.render_y() - h / 2), w, h)

    def draw(self, surface):
        art.draw_beer(surface, self.x, self.render_y())


class Game:
    """Milestone 3 — beers spawn, get collected into 'sips', then the sip-award screen."""

    COUNTDOWN = 3

    def __init__(self, screen, save_data, background=None):
        self.screen = screen
        self.save_data = save_data
        if background is None:
            bg_id = save_data.get("last_bg", config.DEFAULT_BACKGROUND)
            background = next(
                (b for b in config.BACKGROUNDS if b["id"] == bg_id),
                config.BACKGROUNDS[0]
            )
        self.bg = background
        self._sky_surf = self._bake_sky()

        self.font_large = pygame.font.SysFont(None, 72)
        self.font_med = pygame.font.SysFont(None, 42)
        self.font_small = pygame.font.SysFont(None, 30)
        self.font_hud = pygame.font.SysFont(None, 36)
        self._reset()

    def _bake_sky(self):
        sky_h = config.WINDOW_HEIGHT - config.GROUND_HEIGHT
        surf = pygame.Surface((config.WINDOW_WIDTH, sky_h))
        for y in range(sky_h):
            t = y / max(sky_h - 1, 1)
            color = _lerp_color(self.bg["sky_top"], self.bg["sky_bot"], t)
            pygame.draw.line(surf, color, (0, y), (config.WINDOW_WIDTH - 1, y))
        return surf

    def _reset(self):
        self.bird = Bird()
        self.pipes = []
        self.beers = []
        self.popups = []          # floating "+1" effects on collect
        self.pipe_timer = 0
        self.beer_cooldown = 0
        self.score = 0
        self.sips = 0
        self.state = "countdown"
        self.countdown_val = self.COUNTDOWN
        self.countdown_timer = 0
        self.dead_timer = 0
        self.ground_offset = 0.0
        self._go_to_select = False
        self._go_to_results = False

    def _has_players(self):
        return bool(self.save_data.get("players"))

    # ------------------------------------------------------------------ input
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self._on_action()
            elif event.key == pygame.K_ESCAPE and self.state == "dead" and self.dead_timer > 30:
                # Esc changes stage — but if you owe sips and have players, you must assign them
                if self.sips > 0 and self._has_players():
                    self._go_to_results = True
                else:
                    self._go_to_select = True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._on_action()

    def _on_action(self):
        if self.state == "countdown":
            pass
        elif self.state == "playing":
            self.bird.flap()
        elif self.state == "dead":
            if self.dead_timer > 60:
                if self.sips > 0 and self._has_players():
                    self._go_to_results = True
                else:
                    self._reset()

    # ----------------------------------------------------------------- update
    def update(self):
        if self.state == "countdown":
            self._update_countdown()
        elif self.state == "playing":
            self._update_playing()
        elif self.state == "dead":
            self.dead_timer += 1
        self._update_popups()

    def _update_countdown(self):
        self.countdown_timer += 1
        if self.countdown_timer >= 60:
            self.countdown_timer = 0
            self.countdown_val -= 1
            if self.countdown_val <= 0:
                self.state = "playing"

    def _update_playing(self):
        self.bird.update()
        self.ground_offset = (self.ground_offset + config.GROUND_SPEED) % 40

        # pipes
        self.pipe_timer += 1
        if self.pipe_timer >= config.PIPE_SPAWN_INTERVAL:
            self.pipe_timer = 0
            self.pipes.append(Pipe(config.WINDOW_WIDTH + 10, self.bg))

        for pipe in self.pipes:
            pipe.update()
            if not pipe.passed and pipe.top_rect.right < config.BIRD_X:
                pipe.passed = True
                self.score += 1
        self.pipes = [p for p in self.pipes if not p.is_off_screen()]

        # beers
        self._update_beers()

        # collision: pipes
        bird_rect = self.bird.get_rect()
        for pipe in self.pipes:
            if pipe.collides(bird_rect):
                self._die()
                return

        # collision: ceiling / floor
        ground_y = config.WINDOW_HEIGHT - config.GROUND_HEIGHT
        if self.bird.y - config.BIRD_RADIUS < 0 or self.bird.y + config.BIRD_RADIUS > ground_y:
            self._die()

    def _update_beers(self):
        if self.beer_cooldown > 0:
            self.beer_cooldown -= 1

        # spawn
        if (self.beer_cooldown == 0
                and len(self.beers) < config.BEER_MAX_ACTIVE
                and random.random() < config.BEER_SPAWN_CHANCE):
            y = random.randint(config.BEER_SPAWN_Y_MIN, config.BEER_SPAWN_Y_MAX)
            self.beers.append(Beer(config.WINDOW_WIDTH + 20, y))
            self.beer_cooldown = config.BEER_MIN_GAP_FRAMES

        bird_rect = self.bird.get_rect()
        for beer in self.beers:
            beer.update()
            if not beer.collected and beer.get_rect().colliderect(bird_rect):
                beer.collected = True
                self.sips += 1
                self.popups.append({"x": beer.x, "y": beer.render_y(), "t": 32})

        self.beers = [b for b in self.beers if not b.collected and not b.is_off_screen()]

    def _update_popups(self):
        for p in self.popups:
            p["t"] -= 1
            p["y"] -= 1.2
        self.popups = [p for p in self.popups if p["t"] > 0]

    def _die(self):
        self.bird.alive = False
        self.state = "dead"
        self.dead_timer = 0
        if self.score > self.save_data.get("high_score", 0):
            self.save_data["high_score"] = self.score

    # ------------------------------------------------------------------- draw
    def draw(self):
        self._draw_background()
        for pipe in self.pipes:
            pipe.draw(self.screen)
        for beer in self.beers:
            beer.draw(self.screen)
        self._draw_ground()
        self.bird.draw(self.screen)
        self._draw_popups()
        self._draw_hud()

        if self.state == "countdown":
            self._draw_countdown()
        elif self.state == "dead":
            self._draw_game_over()

    def _draw_background(self):
        self.screen.blit(self._sky_surf, (0, 0))
        self._draw_clouds()

    def _draw_clouds(self):
        cc = self.bg["cloud_color"]
        clouds = [(60, 80), (200, 50), (340, 100), (420, 65)]
        for cx, cy in clouds:
            for dx, dy, rw, rh in [(-14, 0, 22, 12), (0, -8, 18, 10), (14, 0, 22, 12)]:
                pygame.draw.ellipse(self.screen, cc,
                                    (cx + dx - rw, cy + dy - rh, rw * 2, rh * 2))

    def _draw_ground(self):
        gy = config.WINDOW_HEIGHT - config.GROUND_HEIGHT
        pygame.draw.rect(self.screen, self.bg["ground"],
                         (0, gy, config.WINDOW_WIDTH, config.GROUND_HEIGHT))
        stripe_w = 40
        offset = int(self.ground_offset)
        x = -stripe_w + offset % stripe_w
        while x < config.WINDOW_WIDTH:
            pygame.draw.rect(self.screen, self.bg["ground_stripe"],
                             (x, gy + 10, stripe_w // 2, config.GROUND_HEIGHT - 10))
            x += stripe_w

    def _draw_popups(self):
        for p in self.popups:
            alpha = int(255 * (p["t"] / 32))
            surf = self.font_small.render("+1", True, config.COLOR_BEER_HIGHLIGHT)
            surf.set_alpha(alpha)
            self.screen.blit(surf, surf.get_rect(center=(int(p["x"]), int(p["y"]))))

    def _draw_hud(self):
        # score, centered top
        score_surf = self.font_large.render(str(self.score), True, config.COLOR_WHITE)
        score_rect = score_surf.get_rect(centerx=config.WINDOW_WIDTH // 2, top=20)
        shadow = self.font_large.render(str(self.score), True, config.COLOR_DARK)
        self.screen.blit(shadow, score_rect.move(2, 2))
        self.screen.blit(score_surf, score_rect)

        # sip counter, top-left with a little mug
        art.draw_beer(self.screen, 26, 30, r=12)
        sip_surf = self.font_hud.render(f"x {self.sips}", True, config.COLOR_WHITE)
        sip_shadow = self.font_hud.render(f"x {self.sips}", True, config.COLOR_DARK)
        self.screen.blit(sip_shadow, (44, 16))
        self.screen.blit(sip_surf, (42, 14))

    def _draw_countdown(self):
        label = str(self.countdown_val) if self.countdown_val > 0 else "GO!"
        surf = self.font_large.render(label, True, config.COLOR_WHITE)
        rect = surf.get_rect(center=(config.WINDOW_WIDTH // 2, config.WINDOW_HEIGHT // 2))
        shadow = self.font_large.render(label, True, config.COLOR_DARK)
        self.screen.blit(shadow, rect.move(3, 3))
        self.screen.blit(surf, rect)

    def _draw_game_over(self):
        overlay = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        cx = config.WINDOW_WIDTH // 2
        y = config.WINDOW_HEIGHT // 2 - 120

        title = self.font_large.render("Game Over", True, config.COLOR_RED)
        self.screen.blit(title, title.get_rect(centerx=cx, top=y))
        y += 78

        score_txt = self.font_med.render(f"Score: {self.score}", True, config.COLOR_WHITE)
        self.screen.blit(score_txt, score_txt.get_rect(centerx=cx, top=y))
        y += 42

        hi = self.save_data.get("high_score", 0)
        hi_txt = self.font_med.render(f"Best: {hi}", True, (255, 215, 0))
        self.screen.blit(hi_txt, hi_txt.get_rect(centerx=cx, top=y))
        y += 50

        # sips earned line, with a mug
        if self.sips > 0:
            label = self.font_med.render(f"{self.sips} sips collected!", True,
                                         config.COLOR_BEER_HIGHLIGHT)
            lrect = label.get_rect(centerx=cx + 14, top=y)
            self.screen.blit(label, lrect)
            art.draw_beer(self.screen, lrect.left - 18, lrect.centery, r=12)
            y += 56

        if self.dead_timer > 60:
            if self.sips > 0 and self._has_players():
                hint = self.font_small.render("Space — divvy up your sips!", True, config.COLOR_WHITE)
            else:
                hint = self.font_small.render(
                    "Space — play again   Esc — change stage", True, config.COLOR_WHITE)
            self.screen.blit(hint, hint.get_rect(centerx=cx, top=y))

    # --------------------------------------------------------- scene protocol
    def next_scene(self):
        if self._go_to_results:
            return ("results", self.sips)
        if self._go_to_select:
            return ("bg_select", None)
        return None
