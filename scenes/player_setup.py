import pygame
import math
import config


def _lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


ROW_H = 44
ROW_W = 320
ROW_GAP = 8


class PlayerSetup:
    """Roster entry: type names, Enter to add, Enter on empty box to start."""

    def __init__(self, screen, save_data):
        self.screen = screen
        self.save_data = save_data
        self.players = list(save_data.get("players", []))
        self.text = ""
        self._done = False
        self._cursor_t = 0.0
        self._pulse = 0.0
        self._error = ""      # transient message (e.g. duplicate)
        self._error_t = 0

        self._bg = self._bake_bg()
        self.font_title = pygame.font.SysFont(None, 56)
        self.font_input = pygame.font.SysFont(None, 40)
        self.font_row = pygame.font.SysFont(None, 36)
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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._submit()
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode and event.unicode.isprintable() and event.unicode not in ("\r", "\n"):
                if len(self.text) < config.MAX_NAME_LEN:
                    self.text += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # click a player row to remove it; click Start to begin
            idx = self._row_at(event.pos)
            if idx is not None:
                self.players.pop(idx)
                self._sync()
            elif self._start_button_rect().collidepoint(event.pos) and self.players:
                self._done = True

    def _submit(self):
        name = self.text.strip()
        if name:
            if len(self.players) >= config.MAX_PLAYERS:
                self._flash("Roster full")
            elif name.lower() in (p.lower() for p in self.players):
                self._flash("Name already added")
            else:
                self.players.append(name)
                self._sync()
            self.text = ""
        elif self.players:
            self._done = True   # empty enter with a roster = start

    def _flash(self, msg):
        self._error = msg
        self._error_t = 90

    def _sync(self):
        self.save_data["players"] = list(self.players)

    # --------------------------------------------------------------- geometry
    def _rows_top(self):
        return 250

    def _row_rect(self, i):
        top = self._rows_top() + i * (ROW_H + ROW_GAP)
        x = (config.WINDOW_WIDTH - ROW_W) // 2
        return pygame.Rect(x, top, ROW_W, ROW_H)

    def _row_at(self, pos):
        for i in range(len(self.players)):
            if self._row_rect(i).collidepoint(pos):
                return i
        return None

    def _start_button_rect(self):
        w, h = 200, 46
        return pygame.Rect((config.WINDOW_WIDTH - w) // 2,
                           config.WINDOW_HEIGHT - 66, w, h)

    # ---------------------------------------------------------------- update
    def update(self):
        self._cursor_t = (self._cursor_t + 0.05) % 1.0
        self._pulse = (self._pulse + 0.06) % (2 * math.pi)
        if self._error_t > 0:
            self._error_t -= 1

    # ------------------------------------------------------------------ draw
    def draw(self):
        self.screen.blit(self._bg, (0, 0))
        cx = config.WINDOW_WIDTH // 2

        title = self.font_title.render("Who's Playing?", True, config.COLOR_WHITE)
        self.screen.blit(title, title.get_rect(centerx=cx, top=48))

        sub = self.font_hint.render("Type a name, press Enter to add", True, (210, 210, 225))
        self.screen.blit(sub, sub.get_rect(centerx=cx, top=110))

        self._draw_input(cx)
        self._draw_rows()
        self._draw_start_button()
        self._draw_footer(cx)

    def _draw_input(self, cx):
        box = pygame.Rect(cx - ROW_W // 2, 150, ROW_W, 50)
        pygame.draw.rect(self.screen, (255, 255, 255, 30), box, border_radius=8)
        pygame.draw.rect(self.screen, config.COLOR_WHITE, box, 2, border_radius=8)

        display = self.text
        text_surf = self.font_input.render(display, True, config.COLOR_WHITE)
        self.screen.blit(text_surf, text_surf.get_rect(midleft=(box.left + 14, box.centery)))

        # blinking cursor
        if self._cursor_t < 0.5:
            cursor_x = box.left + 16 + text_surf.get_width() + 2
            pygame.draw.line(self.screen, config.COLOR_WHITE,
                             (cursor_x, box.top + 12), (cursor_x, box.bottom - 12), 2)

        if self._error_t > 0:
            err = self.font_hint.render(self._error, True, config.COLOR_RED)
            err.set_alpha(min(255, self._error_t * 4))
            self.screen.blit(err, err.get_rect(centerx=cx, top=box.bottom + 6))

    def _draw_rows(self):
        for i, name in enumerate(self.players):
            rect = self._row_rect(i)
            panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            panel.fill((255, 255, 255, 22))
            self.screen.blit(panel, rect.topleft)

            num = self.font_row.render(f"{i + 1}.", True, config.COLOR_BEER_HIGHLIGHT)
            self.screen.blit(num, num.get_rect(midleft=(rect.left + 12, rect.centery)))
            nm = self.font_row.render(name, True, config.COLOR_WHITE)
            self.screen.blit(nm, nm.get_rect(midleft=(rect.left + 48, rect.centery)))

            # remove "x"
            x_surf = self.font_row.render("✕", True, (230, 120, 120))
            self.screen.blit(x_surf, x_surf.get_rect(midright=(rect.right - 14, rect.centery)))

    def _draw_start_button(self):
        rect = self._start_button_rect()
        ready = bool(self.players)
        base = config.COLOR_GREEN if ready else (80, 80, 100)
        pulse = int(20 * math.sin(self._pulse)) if ready else 0
        color = tuple(min(255, c + pulse) for c in base)
        pygame.draw.rect(self.screen, color, rect, border_radius=8)
        pygame.draw.rect(self.screen, config.COLOR_WHITE, rect, 2, border_radius=8)
        label = self.font_input.render("Start", True, config.COLOR_WHITE)
        self.screen.blit(label, label.get_rect(center=rect.center))

    def _draw_footer(self, cx):
        count = self.font_hint.render(
            f"{len(self.players)}/{config.MAX_PLAYERS} players   •   click a name to remove",
            True, (200, 200, 215))
        self.screen.blit(count, count.get_rect(
            centerx=cx, bottom=self._start_button_rect().top - 10))

    # --------------------------------------------------------- scene protocol
    def next_scene(self):
        if self._done:
            self._sync()
            return ("bg_select", None)
        return None
