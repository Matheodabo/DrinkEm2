import sys
import json
import os
import pygame

import config
from scenes.background_select import BackgroundSelect
from scenes.game import Game
from scenes.round_results import RoundResults
from scenes.player_setup import PlayerSetup
from scenes.shop import Shop

SAVE_PATH = os.path.join(os.path.dirname(__file__), "save.json")

DEFAULT_SAVE = {
    "high_score": 0,
    "caps": 0,
    "owned": [],            # owned cosmetic ids
    "equipped": {},         # slot -> cosmetic id
    "last_bg": config.DEFAULT_BACKGROUND,
    "players": [],
}


def load_save():
    if os.path.exists(SAVE_PATH):
        try:
            with open(SAVE_PATH) as f:
                data = json.load(f)
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


def make_scene(name, screen, save_data, payload=None):
    if name == "player_setup":
        return PlayerSetup(screen, save_data)
    if name == "bg_select":
        return BackgroundSelect(screen, save_data)
    if name == "game":
        return Game(screen, save_data, background=payload)
    if name == "results":
        return RoundResults(screen, save_data, payload)
    if name == "shop":
        return Shop(screen, save_data)
    return BackgroundSelect(screen, save_data)


def main():
    pygame.init()
    screen = pygame.display.set_mode((config.WINDOW_WIDTH, config.WINDOW_HEIGHT))
    pygame.display.set_caption(config.TITLE)
    pygame.key.start_text_input()   # ensure TEXTINPUT events for name entry
    clock = pygame.time.Clock()

    save_data = load_save()
    # first launch (or empty roster) starts at player setup
    start_scene = "bg_select" if save_data.get("players") else "player_setup"
    current_scene = make_scene(start_scene, screen, save_data)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                current_scene.handle_input(event)

        current_scene.update()
        current_scene.draw()
        pygame.display.flip()
        clock.tick(config.FPS)

        next_result = current_scene.next_scene()
        if next_result is not None:
            write_save(save_data)
            # next_result is either a string or a (name, payload) tuple
            if isinstance(next_result, tuple):
                next_name, payload = next_result
            else:
                next_name, payload = next_result, None
            current_scene = make_scene(next_name, screen, save_data, payload)

    write_save(save_data)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
