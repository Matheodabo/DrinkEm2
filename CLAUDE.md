# Party Game — Project Notes

## What this is
A desktop party game built in Python with pygame. Game #1 is a Flappy Bird-style
game with social drinking mechanics layered on top. More mini-games may come later,
so keep the core game loosely coupled from menus/shop/save systems.

## Core design (Game 1: Flappy)
- Flappy Bird mechanics: one input (spacebar/click) to flap, gravity, scrolling pipes, score = pipes passed.
- **3 backgrounds**, selectable before a round starts.
- **Beer icons** spawn randomly mid-run. Each beer collected = 1 "sip" the player
  can assign to other players after the round. A post-round award screen shows
  sips earned and lets the player dole them out (just display/assign by name — no
  networking, everyone is in the same room).
- **Bottle caps** also spawn as collectibles. Caps are persistent currency, saved
  between sessions.
- **Shop**: spend caps on characters/outfits (skins). Start with 2–3 skins using
  placeholder art; real art comes later.

## Tech stack
- Python 3.11+, pygame
- Save data: single JSON file (caps balance, owned skins, equipped skin, high score)
- Placeholder art first (colored shapes / simple sprites). Do not block progress on art.

## Conventions
- Scene/state pattern: MainMenu, Game, RoundResults (sip screen), Shop — each a class
  with handle_input / update / draw.
- All tunable values (gravity, flap strength, pipe gap, spawn rates) in one
  `config.py` so balancing doesn't require hunting through code.
- Assets in `/assets`, organized by `backgrounds/`, `characters/`, `icons/`, `sounds/`.
- Commit at the end of every milestone with a clear message.

## Milestones
- [x] 1. Repo setup, this file, playable bird + pipes + score + game over
- [x] 2. Three backgrounds + pre-round background selector
- [x] 3. Beer icon spawning/collection + post-round sip award screen
- [ ] 4. Bottle cap collectible + persistent JSON save
- [ ] 5. Shop UI + 2–3 skins (placeholder art)
- [ ] 6. Polish: sounds, menu flow, pause, small visual juice

## Session workflow (important)
- Work on ONE milestone per session unless it finishes early.
- At the end of every session: check off completed milestones above, and update
  the "Next session" section below with exact next steps and any open decisions.
- Keep commits small and descriptive.

## Next session
Start milestone 4: bottle cap collectible + persistent JSON save.
- Caps spawn during a round (config.CAP_SPAWN_CHANCE), separate from beers, collected like beers.
- Caps are PERSISTENT currency: add collected caps to save_data["caps"] on round end and
  write save.json (save already persists; just feed caps in). Show cap total in HUD + game over.
- Add a bottle-cap drawing to art.py (mirror art.draw_beer). Reuse the Beer entity pattern for a
  Cap entity in scenes/game.py (consider refactoring Beer/Cap into a shared Collectible base).
- save.json already round-trips high_score/caps/owned_skins/equipped_skin/last_bg/players.

## Flow / architecture notes (current)
- Scenes return either a string or a (name, payload) tuple from next_scene(); main.make_scene routes.
  Scene names: "player_setup", "bg_select", "game", "results".
- Startup: player_setup if save["players"] empty, else bg_select.
- Roster persists in save["players"]; edit anytime via "P" on the stage selector.
- Game collects beers -> self.sips. On death with sips>0 AND players present -> ("results", sips);
  otherwise normal play-again / Esc-to-stage. RoundResults assigns sips -> back to bg_select.
- Shared placeholder art lives in art.py (art.draw_beer) so HUD/entity/results stay visually consistent.

## Open decisions
- Player names for sip assignment: entered at game start? (lean yes, simple text entry)
- Window size / fullscreen toggle
