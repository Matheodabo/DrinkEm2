import sys
import json
import os
import pygame

import config
from scenes.main_menu import MainMenu
from scenes.game import Game

SAVE_PATH = os.path.join(os.path.dirname(__file__), "save.json")

DEFAULT_SAVE = {
    "high_score": 0,
    "caps": 0,
    "owned_skins": ["default"],
    "equipped_skin": "default",
}


def load_save():
    if os.path.exists(SAVE_PATH):
        try:
            with open(SAVE_PATH) as f:
                data = json.load(f)
            # merge any missing keys from default
            for k, v in DEFAULT_SAVE.items():
                data.setdefault(k, v)
            return data
        except (json.JSONDecodeError, OSError):
            pass
    return dict(DEFAULT_SAVE)


def write_save(data):
    try:
        with open(SAVE_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except OSError:
        pass


def make_scene(name, screen, save_data):
    if name == "menu":
        return MainMenu(screen, save_data)
    if name == "game":
        return Game(screen, save_data)
    return MainMenu(screen, save_data)


def main():
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption(config.TITLE)
    clock = pygame.time.Clock()

    save_data = load_save()
    current_scene = make_scene("game", screen, save_data)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            else:
                current_scene.handle_input(event)

        current_scene.update()
        current_scene.draw()
        pygame.display.flip()
        clock.tick(config.FPS)

        # scene transitions
        next_name = current_scene.next_scene()
        if next_name is not None:
            write_save(save_data)
            current_scene = make_scene(next_name, screen, save_data)

    write_save(save_data)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
