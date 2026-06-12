import pygame
import math
import config


def _lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


ROW_H = 40
ROW_W = 320
ROW_GAP = 7
INPUT_Y = 138
ADD_BTN_Y = 192
ROWS_TOP = 244


class PlayerSetup:
    """Roster entry. Two ways to add players so typing is never required:
      * click '+ Add Player' (adds 'Player N') — pure mouse, always works
      * type a name + Enter — needs the window to have keyboard focus
    Click a name to remove it; Start to begin.
    """

    def __init__(self, screen, save_data):
        self.screen = screen
        self.save_data = save_data
        self.players = list(save_data.get("players", []))
        self.text = ""
        self._got_textinput = False
        self._done = False
        self._cursor_t = 0.0
        self._pulse = 0.0
        self._error = ""
        self._error_t = 0
        self._last_input = "(none yet)"   # live diagnostic of received input

        self._bg = self._bake_bg()
        self.font_title = pygame.font.SysFont(None, 56)
        self.font_input = pygame.font.SysFont(None, 38)
        self.font_row = pygame.font.SysFont(None, 32)
        self.font_btn = pygame.font.SysFont(None, 30)
        self.font_hint = pygame.font.SysFont(None, 24)

    def _bake_bg(self):
        surf = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        for y in range(config.WINDOW_HEIGHT):
            t = y / (config.WINDOW_HEIGHT - 1)
            surf.fill(_lerp_color(config.COLOR_PARTY_TOP, config.COLOR_PARTY_BOT, t),
                      (0, y, config.WINDOW_WIDTH, 1))
        return surf

    # ----------------------------------------------------------------- input
    def handle_input(self, event):
        if event.type == pygame.TEXTINPUT:
            self._got_textinput = True
            self._last_input = f"text '{event.text}'"
            ch = event.text
            if ch and ch.isprintable() and len(self.text) < config.MAX_NAME_LEN:
                self.text += ch
            return

        if event.type == pygame.KEYDOWN:
            self._last_input = f"key {pygame.key.name(event.key)}"
            if event.key == pygame.K_RETURN:
                self._submit()
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif (not self._got_textinput and event.unicode
                    and event.unicode.isprintable() and event.unicode not in ("\r", "\n")):
                if len(self.text) < config.MAX_NAME_LEN:
                    self.text += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._last_input = "mouse click"
            if self._add_button_rect().collidepoint(event.pos):
                self._add_default_player()
                return
            if self._start_button_rect().collidepoint(event.pos) and self.players:
                self._done = True
                return
            idx = self._row_at(event.pos)
            if idx is not None:
                self.players.pop(idx)
                self._sync()

    def _submit(self):
        name = self.text.strip()
        if name:
            self._add_name(name)
            self.text = ""
        elif self.players:
            self._done = True   # empty enter with a roster = start

    def _add_name(self, name):
        if len(self.players) >= config.MAX_PLAYERS:
            self._flash("Roster full")
        elif name.lower() in (p.lower() for p in self.players):
            self._flash("Name already added")
        else:
            self.players.append(name)
            self._sync()

    def _add_default_player(self):
        if len(self.players) >= config.MAX_PLAYERS:
            self._flash("Roster full")
            return
        used = set(self.players)
        n = 1
        while f"Player {n}" in used:
            n += 1
        self.players.append(f"Player {n}")
        self._sync()

    def _flash(self, msg):
        self._error = msg
        self._error_t = 90

    def _sync(self):
        self.save_data["players"] = list(self.players)

    # --------------------------------------------------------------- geometry
    def _row_rect(self, i):
        top = ROWS_TOP + i * (ROW_H + ROW_GAP)
        x = (config.WINDOW_WIDTH - ROW_W) // 2
        return pygame.Rect(x, top, ROW_W, ROW_H)

    def _row_at(self, pos):
        for i in range(len(self.players)):
            if self._row_rect(i).collidepoint(pos):
                return i
        return None

    def _add_button_rect(self):
        w, h = 200, 38
        return pygame.Rect((config.WINDOW_WIDTH - w) // 2, ADD_BTN_Y, w, h)

    def _start_button_rect(self):
        w, h = 200, 46
        return pygame.Rect((config.WINDOW_WIDTH - w) // 2,
                           config.WINDOW_HEIGHT - 64, w, h)

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
        self.screen.blit(title, title.get_rect(centerx=cx, top=40))

        sub = self.font_hint.render("Click  + Add Player ,  or type a name + Enter",
                                    True, (210, 210, 225))
        self.screen.blit(sub, sub.get_rect(centerx=cx, top=98))

        self._draw_input(cx)
        self._draw_add_button()
        self._draw_rows()
        self._draw_start_button()
        self._draw_footer(cx)

    def _draw_input(self, cx):
        box = pygame.Rect(cx - ROW_W // 2, INPUT_Y, ROW_W, 44)
        pygame.draw.rect(self.screen, (255, 255, 255, 30), box, border_radius=8)
        pygame.draw.rect(self.screen, config.COLOR_WHITE, box, 2, border_radius=8)

        text_surf = self.font_input.render(self.text, True, config.COLOR_WHITE)
        self.screen.blit(text_surf, text_surf.get_rect(midleft=(box.left + 14, box.centery)))

        if self._cursor_t < 0.5:
            cursor_x = box.left + 16 + text_surf.get_width() + 2
            pygame.draw.line(self.screen, config.COLOR_WHITE,
                             (cursor_x, box.top + 10), (cursor_x, box.bottom - 10), 2)

        if self._error_t > 0:
            err = self.font_hint.render(self._error, True, config.COLOR_RED)
            err.set_alpha(min(255, self._error_t * 4))
            self.screen.blit(err, err.get_rect(midleft=(box.right + 10, box.centery)))

    def _draw_add_button(self):
        rect = self._add_button_rect()
        full = len(self.players) >= config.MAX_PLAYERS
        base = (70, 130, 200) if not full else (80, 80, 100)
        pygame.draw.rect(self.screen, base, rect, border_radius=8)
        pygame.draw.rect(self.screen, config.COLOR_WHITE, rect, 2, border_radius=8)
        label = self.font_btn.render("+ Add Player", True, config.COLOR_WHITE)
        self.screen.blit(label, label.get_rect(center=rect.center))

    def _draw_rows(self):
        for i, name in enumerate(self.players):
            rect = self._row_rect(i)
            panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            panel.fill((255, 255, 255, 22))
            self.screen.blit(panel, rect.topleft)

            num = self.font_row.render(f"{i + 1}.", True, config.COLOR_BEER_HIGHLIGHT)
            self.screen.blit(num, num.get_rect(midleft=(rect.left + 12, rect.centery)))
            nm = self.font_row.render(name, True, config.COLOR_WHITE)
            self.screen.blit(nm, nm.get_rect(midleft=(rect.left + 46, rect.centery)))

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
            centerx=cx, bottom=self._start_button_rect().top - 8))

        # live input diagnostic — if typing shows "(none yet)", the window isn't
        # receiving keys (click it to focus). Helps pinpoint focus issues.
        diag = self.font_hint.render(f"last input: {self._last_input}", True, (150, 150, 170))
        self.screen.blit(diag, diag.get_rect(centerx=cx, bottom=config.WINDOW_HEIGHT - 6))

    # --------------------------------------------------------- scene protocol
    def next_scene(self):
        if self._done:
            self._sync()
            return ("bg_select", None)
        return None
