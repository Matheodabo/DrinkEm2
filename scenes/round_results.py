import pygame
import math
import config
import art


def _lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


ROW_H = 52
ROW_W = 360
ROW_GAP = 10


class RoundResults:
    """Post-round sip-award screen: assign each collected sip to a player."""

    def __init__(self, screen, save_data, sips):
        self.screen = screen
        self.save_data = save_data
        self.sips = int(sips or 0)

        names = save_data.get("players", [])
        # [name, assigned_count] rows
        self.rows = [[n, 0] for n in names]
        self.remaining = self.sips
        self.selected = 0
        self._done = False
        self._pulse = 0.0

        self._bg = self._bake_bg()
        self.font_title = pygame.font.SysFont(None, 60)
        self.font_sub = pygame.font.SysFont(None, 34)
        self.font_row = pygame.font.SysFont(None, 38)
        self.font_hint = pygame.font.SysFont(None, 26)

    def _bake_bg(self):
        surf = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        for y in range(config.WINDOW_HEIGHT):
            t = y / (config.WINDOW_HEIGHT - 1)
            surf.fill(_lerp_color(config.COLOR_PARTY_TOP, config.COLOR_PARTY_BOT, t),
                      (0, y, config.WINDOW_WIDTH, 1))
        return surf

    # ----------------------------------------------------------------- input
    def handle_input(self, event):
        if self._done or not self.rows:
            if not self.rows:
                self._done = True
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self.selected = (self.selected - 1) % len(self.rows)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.selected = (self.selected + 1) % len(self.rows)
            elif event.key in (pygame.K_RIGHT, pygame.K_SPACE, pygame.K_PLUS, pygame.K_EQUALS):
                self._assign(self.selected)
            elif event.key in (pygame.K_LEFT, pygame.K_BACKSPACE, pygame.K_MINUS):
                self._unassign(self.selected)
            elif event.key == pygame.K_RETURN:
                self._done = True

        if event.type == pygame.MOUSEBUTTONDOWN:
            idx = self._row_at(event.pos)
            if idx is not None:
                self.selected = idx
                if event.button == 1:
                    self._assign(idx)
                elif event.button == 3:
                    self._unassign(idx)
            else:
                # clicking the Done button area
                if self._done_button_rect().collidepoint(event.pos):
                    self._done = True

    def _assign(self, idx):
        if self.remaining > 0:
            self.rows[idx][1] += 1
            self.remaining -= 1

    def _unassign(self, idx):
        if self.rows[idx][1] > 0:
            self.rows[idx][1] -= 1
            self.remaining += 1

    # --------------------------------------------------------------- geometry
    def _rows_top(self):
        n = len(self.rows)
        block_h = n * ROW_H + (n - 1) * ROW_GAP
        return max(190, config.WINDOW_HEIGHT // 2 - block_h // 2 + 20)

    def _row_rect(self, i):
        top = self._rows_top() + i * (ROW_H + ROW_GAP)
        x = (config.WINDOW_WIDTH - ROW_W) // 2
        return pygame.Rect(x, top, ROW_W, ROW_H)

    def _row_at(self, pos):
        for i in range(len(self.rows)):
            if self._row_rect(i).collidepoint(pos):
                return i
        return None

    def _done_button_rect(self):
        w, h = 200, 44
        return pygame.Rect((config.WINDOW_WIDTH - w) // 2,
                           config.WINDOW_HEIGHT - 64, w, h)

    # ---------------------------------------------------------------- update
    def update(self):
        self._pulse = (self._pulse + 0.06) % (2 * math.pi)

    # ------------------------------------------------------------------ draw
    def draw(self):
        self.screen.blit(self._bg, (0, 0))
        self._draw_header()
        self._draw_rows()
        self._draw_done_button()
        self._draw_hint()

    def _draw_header(self):
        cx = config.WINDOW_WIDTH // 2
        title = self.font_title.render("Round Over!", True, config.COLOR_WHITE)
        self.screen.blit(title, title.get_rect(centerx=cx, top=40))

        sub = self.font_sub.render(f"{self.sips} sips collected", True,
                                   config.COLOR_BEER_HIGHLIGHT)
        srect = sub.get_rect(centerx=cx + 14, top=104)
        self.screen.blit(sub, srect)
        art.draw_beer(self.screen, srect.left - 16, srect.centery, r=12)

        # remaining-to-assign
        if self.remaining > 0:
            rem_color = config.COLOR_WHITE
            rem_text = f"{self.remaining} left to assign"
        else:
            rem_color = config.COLOR_GREEN
            rem_text = "All sips assigned!"
        rem = self.font_sub.render(rem_text, True, rem_color)
        self.screen.blit(rem, rem.get_rect(centerx=cx, top=144))

    def _draw_rows(self):
        for i, (name, count) in enumerate(self.rows):
            rect = self._row_rect(i)
            is_sel = (i == self.selected)

            # row background
            bg_color = (255, 255, 255, 40) if is_sel else (255, 255, 255, 18)
            panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            panel.fill(bg_color)
            self.screen.blit(panel, rect.topleft)
            if is_sel:
                glow = int(30 + 20 * math.sin(self._pulse))
                pygame.draw.rect(self.screen, (255, 220 + glow - 30, 80), rect, 3,
                                 border_radius=6)

            # name
            name_surf = self.font_row.render(name, True, config.COLOR_WHITE)
            self.screen.blit(name_surf, name_surf.get_rect(
                midleft=(rect.left + 16, rect.centery)))

            # assigned beers as little mugs (cap the icons, then show xN)
            icon_x = rect.right - 28
            shown = min(count, 4)
            for k in range(shown):
                art.draw_beer(self.screen, icon_x - k * 22, rect.centery, r=10)
            if count > 4:
                extra = self.font_hint.render(f"x{count}", True, config.COLOR_BEER_HIGHLIGHT)
                self.screen.blit(extra, extra.get_rect(
                    midright=(icon_x - 4 * 22 - 6, rect.centery)))
            elif count == 0:
                dash = self.font_hint.render("—", True, (200, 200, 200))
                self.screen.blit(dash, dash.get_rect(midright=(rect.right - 16, rect.centery)))

    def _draw_done_button(self):
        rect = self._done_button_rect()
        ready = (self.remaining == 0)
        base = config.COLOR_GREEN if ready else (90, 90, 110)
        pulse = int(20 * math.sin(self._pulse)) if ready else 0
        color = tuple(min(255, c + pulse) for c in base)
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, config.COLOR_WHITE, rect, 2, border_radius=8)
        label = self.font_sub.render("Done", True, config.COLOR_WHITE)
        self.screen.blit(label, label.get_rect(center=rect.center))

    def _draw_hint(self):
        text = "↑↓ select   → assign   ← take back   Enter / Done to finish"
        hint = self.font_hint.render(text, True, (220, 220, 230))
        self.screen.blit(hint, hint.get_rect(
            centerx=config.WINDOW_WIDTH // 2, bottom=config.WINDOW_HEIGHT - 70))

    # --------------------------------------------------------- scene protocol
    def next_scene(self):
        if self._done:
            return ("bg_select", None)
        return None
