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
- [ ] 3. Beer icon spawning/collection + post-round sip award screen
- [ ] 4. Bottle cap collectible + persistent JSON save
- [ ] 5. Shop UI + 2–3 skins (placeholder art)
- [ ] 6. Polish: sounds, menu flow, pause, small visual juice

## Session workflow (important)
- Work on ONE milestone per session unless it finishes early.
- At the end of every session: check off completed milestones above, and update
  the "Next session" section below with exact next steps and any open decisions.
- Keep commits small and descriptive.

## Next session
Start milestone 3: beer icon spawning/collection + post-round sip award screen.
- Beer icons spawn randomly during a live round (config.BEER_SPAWN_CHANCE per frame).
- Collecting a beer adds 1 sip to the round total; show count in HUD.
- After death, transition to RoundResults scene: display sips earned, list player names
  (entered at game start or carried from a lobby screen), let the player assign each sip
  to a name via arrow keys / click, then return to BackgroundSelect.

## Open decisions
- Player names for sip assignment: entered at game start? (lean yes, simple text entry)
- Window size / fullscreen toggle
