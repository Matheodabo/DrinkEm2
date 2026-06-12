"""Stub — wired up in a later milestone."""
import pygame
import config


class MainMenu:
    def __init__(self, screen, save_data):
        self.screen = screen
        self.save_data = save_data
        self._go_to_game = False

    def handle_input(self, event):
        if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self._go_to_game = True

    def update(self):
        pass

    def draw(self):
        self.screen.fill(config.COLOR_SKY)
        font = pygame.font.SysFont(None, 64)
        surf = font.render("PARTY BIRD", True, config.COLOR_WHITE)
        self.screen.blit(surf, surf.get_rect(center=(config.WINDOW_WIDTH // 2,
                                                      config.WINDOW_HEIGHT // 2 - 40)))
        small = pygame.font.SysFont(None, 32)
        hint = small.render("Press any key to play", True, config.COLOR_WHITE)
        self.screen.blit(hint, hint.get_rect(center=(config.WINDOW_WIDTH // 2,
                                                      config.WINDOW_HEIGHT // 2 + 30)))

    def next_scene(self):
        return "game" if self._go_to_game else None
