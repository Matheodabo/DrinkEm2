import pygame
import math
import config
import art
import cosmetics


def _lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


COLS = 2
CARD_W = 156
CARD_H = 108
CARD_GAP_X = 16
CARD_GAP_Y = 12
GRID_TOP = 224
VISIBLE_ROWS = 3


class Shop:
    """Spend caps on accessories; equip one per slot. Bird wears them in-game."""

    def __init__(self, screen, save_data):
        self.screen = screen
        self.save_data = save_data
        self.items = cosmetics.COSMETICS

        self.selected = 0
        self.scroll = 0
        self._done = False
        self._pulse = 0.0
        self._flash = ""
        self._flash_t = 0

        self._bg = self._bake_bg()
        self.font_title = pygame.font.SysFont(None, 50)
        self.font_name = pygame.font.SysFont(None, 26)
        self.font_small = pygame.font.SysFont(None, 22)
        self.font_caps = pygame.font.SysFont(None, 38)
        self.font_hint = pygame.font.SysFont(None, 24)

    def _bake_bg(self):
        surf = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
        for y in range(config.WINDOW_HEIGHT):
            t = y / (config.WINDOW_HEIGHT - 1)
            surf.fill(_lerp_color(config.COLOR_PARTY_TOP, config.COLOR_PARTY_BOT, t),
                      (0, y, config.WINDOW_WIDTH, 1))
        return surf

    # ------------------------------------------------------------ save access
    @property
    def owned(self):
        return self.save_data.setdefault("owned", [])

    @property
    def equipped(self):
        return self.save_data.setdefault("equipped", {})

    def _is_owned(self, item):
        return item["id"] in self.owned

    def _is_equipped(self, item):
        return self.equipped.get(item["slot"]) == item["id"]

    # ----------------------------------------------------------------- input
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._done = True
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self._move(-1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._move(1)
            elif event.key in (pygame.K_UP, pygame.K_w):
                self._move(-COLS)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._move(COLS)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._activate(self.items[self.selected])

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            idx = self._card_at(event.pos)
            if idx is not None:
                self.selected = idx
                self._activate(self.items[idx])
            elif self._back_button_rect().collidepoint(event.pos):
                self._done = True

    def _move(self, delta):
        self.selected = max(0, min(len(self.items) - 1, self.selected + delta))
        self._ensure_visible()

    def _ensure_visible(self):
        row = self.selected // COLS
        if row < self.scroll:
            self.scroll = row
        elif row >= self.scroll + VISIBLE_ROWS:
            self.scroll = row - VISIBLE_ROWS + 1

    def _activate(self, item):
        if not self._is_owned(item):
            if self.save_data.get("caps", 0) >= item["price"]:
                self.save_data["caps"] -= item["price"]
                self.owned.append(item["id"])
                self.equipped[item["slot"]] = item["id"]   # auto-equip on buy
                self._set_flash(f"Bought {item['name']}!")
            else:
                self._set_flash("Not enough caps")
        else:
            # toggle equip/unequip within the slot
            if self._is_equipped(item):
                self.equipped.pop(item["slot"], None)
                self._set_flash(f"Removed {item['name']}")
            else:
                self.equipped[item["slot"]] = item["id"]
                self._set_flash(f"Equipped {item['name']}")

    def _set_flash(self, msg):
        self._flash = msg
        self._flash_t = 90

    # --------------------------------------------------------------- geometry
    def _grid_start_x(self):
        grid_w = COLS * CARD_W + (COLS - 1) * CARD_GAP_X
        return (config.WINDOW_WIDTH - grid_w) // 2

    def _card_rect(self, idx):
        row = idx // COLS
        col = idx % COLS
        x = self._grid_start_x() + col * (CARD_W + CARD_GAP_X)
        y = GRID_TOP + (row - self.scroll) * (CARD_H + CARD_GAP_Y)
        return pygame.Rect(x, y, CARD_W, CARD_H)

    def _is_row_visible(self, idx):
        row = idx // COLS
        return self.scroll <= row < self.scroll + VISIBLE_ROWS

    def _card_at(self, pos):
        for i in range(len(self.items)):
            if self._is_row_visible(i) and self._card_rect(i).collidepoint(pos):
                return i
        return None

    def _back_button_rect(self):
        return pygame.Rect(16, config.WINDOW_HEIGHT - 50, 96, 36)

    # ---------------------------------------------------------------- update
    def update(self):
        self._pulse = (self._pulse + 0.06) % (2 * math.pi)
        if self._flash_t > 0:
            self._flash_t -= 1

    # ------------------------------------------------------------------ draw
    def draw(self):
        self.screen.blit(self._bg, (0, 0))
        self._draw_header()
        self._draw_preview()
        self._draw_cards()
        self._draw_scrollbar()
        self._draw_footer()

    def _draw_header(self):
        title = self.font_title.render("Shop", True, config.COLOR_WHITE)
        self.screen.blit(title, (20, 16))

        # caps balance top-right
        caps = self.save_data.get("caps", 0)
        text = str(caps)
        tw = self.font_caps.size(text)[0]
        art.draw_cap(self.screen, config.WINDOW_WIDTH - 26, 34, r=12)
        label = self.font_caps.render(text, True, config.COLOR_WHITE)
        self.screen.blit(label, (config.WINDOW_WIDTH - 44 - tw, 18))

    def _draw_preview(self):
        # the dressed bird, showing everything currently equipped
        worn = cosmetics.equipped_list(self.save_data)
        cx, cy = 54, 150
        halo = pygame.Surface((96, 96), pygame.SRCALPHA)
        pygame.draw.circle(halo, (255, 255, 255, 25), (48, 48), 44)
        self.screen.blit(halo, (cx - 48, cy - 48))
        art.draw_dressed_bird(self.screen, cx, cy, 26, worn)

        tag = self.font_small.render("Your look", True, (220, 220, 230))
        self.screen.blit(tag, tag.get_rect(centerx=cx, top=cy + 40))

    def _draw_cards(self):
        for i, item in enumerate(self.items):
            if not self._is_row_visible(i):
                continue
            rect = self._card_rect(i)
            is_sel = (i == self.selected)
            owned = self._is_owned(item)
            equipped = self._is_equipped(item)

            panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            panel.fill((255, 255, 255, 36) if is_sel else (255, 255, 255, 18))
            self.screen.blit(panel, rect.topleft)

            border = None
            if equipped:
                border = config.COLOR_GREEN
            elif is_sel:
                glow = int(30 + 20 * math.sin(self._pulse))
                border = (255, min(255, 190 + glow), 80)
            if border:
                pygame.draw.rect(self.screen, border, rect, 3, border_radius=8)

            # item preview on a mini bird
            art.draw_dressed_bird(self.screen, rect.centerx, rect.top + 38, 18, [item])

            # name
            name = self.font_name.render(item["name"], True, config.COLOR_WHITE)
            self.screen.blit(name, name.get_rect(centerx=rect.centerx, top=rect.top + 62))

            # status line
            self._draw_status(rect, item, owned, equipped)

    def _draw_status(self, rect, item, owned, equipped):
        cy = rect.bottom - 16
        if equipped:
            s = self.font_small.render("Equipped", True, config.COLOR_GREEN)
            self.screen.blit(s, s.get_rect(center=(rect.centerx, cy)))
        elif owned:
            s = self.font_small.render("Tap to wear", True, (210, 210, 225))
            self.screen.blit(s, s.get_rect(center=(rect.centerx, cy)))
        else:
            afford = self.save_data.get("caps", 0) >= item["price"]
            color = config.COLOR_WHITE if afford else (230, 120, 120)
            s = self.font_small.render(str(item["price"]), True, color)
            total_w = s.get_width() + 18
            x0 = rect.centerx - total_w // 2
            art.draw_cap(self.screen, x0 + 7, cy, r=8)
            self.screen.blit(s, s.get_rect(midleft=(x0 + 18, cy)))

    def _draw_scrollbar(self):
        total_rows = (len(self.items) + COLS - 1) // COLS
        if total_rows <= VISIBLE_ROWS:
            return
        track = pygame.Rect(config.WINDOW_WIDTH - 8, GRID_TOP,
                            4, VISIBLE_ROWS * (CARD_H + CARD_GAP_Y) - CARD_GAP_Y)
        pygame.draw.rect(self.screen, (255, 255, 255, 40), track, border_radius=2)
        frac = VISIBLE_ROWS / total_rows
        knob_h = max(20, int(track.height * frac))
        knob_y = track.top + int((track.height - knob_h) * (self.scroll / (total_rows - VISIBLE_ROWS)))
        pygame.draw.rect(self.screen, (230, 230, 240), (track.x, knob_y, 4, knob_h), border_radius=2)

    def _draw_footer(self):
        # back button
        rect = self._back_button_rect()
        pygame.draw.rect(self.screen, (90, 90, 110), rect, border_radius=8)
        pygame.draw.rect(self.screen, config.COLOR_WHITE, rect, 2, border_radius=8)
        back = self.font_name.render("Back", True, config.COLOR_WHITE)
        self.screen.blit(back, back.get_rect(center=rect.center))

        # flash message
        if self._flash_t > 0:
            msg = self.font_hint.render(self._flash, True, config.COLOR_BEER_HIGHLIGHT)
            msg.set_alpha(min(255, self._flash_t * 5))
            self.screen.blit(msg, msg.get_rect(
                centerx=config.WINDOW_WIDTH // 2, centery=config.WINDOW_HEIGHT - 32))

        hint = self.font_hint.render("↑↓←→ browse   Enter buy/equip   Esc back",
                                     True, (210, 210, 225))
        self.screen.blit(hint, hint.get_rect(
            right=config.WINDOW_WIDTH - 12, bottom=config.WINDOW_HEIGHT - 8))

    # --------------------------------------------------------- scene protocol
    def next_scene(self):
        if self._done:
            return ("bg_select", None)
        return None
