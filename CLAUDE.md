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
- [x] 4. Bottle cap collectible + persistent JSON save
- [x] 5. Shop UI + skins/accessories (placeholder art)
- [ ] 6. Polish: sounds, menu flow, pause, small visual juice

## Session workflow (important)
- Work on ONE milestone per session unless it finishes early.
- At the end of every session: check off completed milestones above, and update
  the "Next session" section below with exact next steps and any open decisions.
- Keep commits small and descriptive.

## Next session
Start milestone 6: polish — sounds, menu flow, pause, small visual juice.
- Sounds: flap, collect (beer vs cap distinct), crash, button click. Put .wav/.ogg in assets/sounds/,
  load centrally, add a global mute toggle persisted in save.
- A proper MainMenu landing scene (currently startup goes straight to player_setup/bg_select).
- Pause (P or Esc) during live play with resume/quit-to-menu.
- Juice: screen shake on crash, particle burst on collect, parallax clouds, score pop scale.

## Flow / architecture notes (current)
- Scenes return a string or (name, payload) tuple from next_scene(); main.make_scene routes.
  Scene names: "player_setup", "bg_select", "game", "results", "shop".
- Startup: player_setup if save["players"] empty, else bg_select.
- From bg_select: P -> player_setup, S -> shop. Both return to bg_select.
- Collectibles are data-driven in config.COLLECTIBLES (sprite/reward/amount/weight/spin). reward is
  "sip" (round-local -> RoundResults) or "caps" (persistent currency). Kinds: beer/cap/cigbox/fidget.
  Game.Collectible is the single entity class; spawn is weighted-random via _spawn_kind().
- Caps bank into save["caps"] once in Game._die() (idempotent via caps_banked flag).
- Cosmetics: cosmetics.py catalog (id/name/slot/price/draw). One item per slot
  (hat/eyes/neck/face/legs). save["owned"] (ids) + save["equipped"] (slot->id).
  cosmetics.equipped_list(save) -> dicts; Bird(worn) renders via art.draw_dressed_bird.
- Shop: buy (deduct caps, auto-equip), toggle equip/unequip, scrollable 2-col grid + fitting-room
  preview bird. Reachable via S on bg_select.
- ALL sprites are vector-drawn in art.py: collectibles (draw_beer/cap/cig_box/fidget) and accessories
  (draw_top_hat/party_hat/cap_hat/crown/glasses/sunglasses/goggles/bowtie/chain/mustache/pants).
  Swap for real sprites by keeping the (surface, cx, cy, r) signatures.
- save["owned_skins"]/["equipped_skin"] from earlier are obsolete; new code uses owned/equipped.

## How to run / test
- Run: `python3 main.py` (uses pygame-ce; standard pygame needs SDL2 headers we don't have).
- Keyboard + mouse only — NO game controller needed. Flap = Space or left-click.
- Multiplayer = local hot-seat (one screen): set a roster in PlayerSetup, then after a run with
  beers you assign sips to players on the RoundResults screen. Nothing networked.
- Headless smoke test pattern (no window): set SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy and drive
  scenes by feeding pygame KEYDOWN/MOUSEBUTTONDOWN events, asserting on save/scene state.

## Open decisions
- Player names for sip assignment: entered at game start? (lean yes, simple text entry)
- Window size / fullscreen toggle
