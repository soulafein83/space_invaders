# AGENTS.md

Space Invaders clone: Python + Arcade (dep: `arcade>=3,<4`, developed against arcade 3.3.3). Flat layout, single windowed game — no packages, no tests, no CI. Project docs (`error.md`, `plan.md`) are written in Polish. Do not read `plan.md` or `error.md` proactively — their key points are already summarized here; open them only when a new, unexplained error occurs.

## Running

- `pip install -r requirements.txt`, then `python main.py` (a gitignored `venv/` exists at the repo root; project docs use `./venv/bin/python`). This venv has no `venv/bin/pip` entrypoint — install with `venv/bin/python -m pip install -r requirements.txt`.
- Needs a display — it opens a 1200×1000 window. `GameView` is only constructed after the start screen is clicked, so importing modules headless does not exercise most of the code.
- There is no test/lint/typecheck setup. Verify changes by running the game.

## Layout

- `main.py` — entrypoint: font registration, window, start view.
- `game_view.py` — all main game logic (`GameView`).
- `instruction_view.py` — start screen; left-click creates `GameView` and calls `setup()`.
- `constants.py` — every tunable (sprite scale ×6, speeds, screen size, `GAME_OVER`/`PLAY_GAME`).
- `enemy_invader.py`, `enemy_bullet.py` — sprite subclasses with 2-frame animation.
- `highscore.py` — JSON high score saved next to the code (`highscore.json`, gitignored); `load_high_score()` returns 0 on missing/invalid file.
- `images/` — Kenney sprites; sounds come from arcade's bundled `:resources:sounds/...` paths.
- `error.md` — the authoritative log of every verified arcade 3.3.3 gotcha listed below; `plan.md` — the fix plan (all items done as of 2026-10-30).

## Arcade 3.x gotchas (verified against 3.3.3)

- Overriding `Sprite.update()` requires `super().update(delta_time)` first, or `change_x`/`change_y` are never applied (this is why enemy bullets must call it).
- `SpriteList.clear()` swaps the internal list, so a `for` loop keeps iterating the old one — always `break` after clearing inside a loop.
- In 3.3.3 `arcade.types.Rect(0,0,w,h)` (4-arg) and `Point2(...)` are not classes — use `arcade.types.Viewport(left, bottom, w, h)` and `pyglet.math.Vec2`.
- The "Kenney Rocket" font must be registered in `main.py` via `arcade.load_font(":system:fonts/ttf/Kenney/Kenney_Rocket.ttf")` before creating the window. `arcade.load_kenney_fonts()` does not exist in 3.3.3, and without the load `font_name="Kenney Rocket"` silently falls back to the system font.
- `:resources:sounds/...` sound paths resolve correctly — do not "fix" them to `:resources:assets/sounds/...` (that form does not resolve).
- The CRT filter (`arcade.experimental.CRTFilter`) is experimental and only works when the window is exactly 1200×1000. The try/except in `GameView.__init__` and the per-frame enable/disable in `on_draw` are intentional — keep the fallback. The `on_draw` check is two-way (re-enables when the window returns to 1200×1000) and must also require `self.crt_filter is not None`, otherwise a failed filter creation crashes every frame.
- The camera letterboxes via `Camera2D.match_window(aspect=...)` + centered viewport + zoom; raw mouse coordinates are *not* world coordinates — use `self.camera.unproject((x, y))`.

## Game logic invariants (regression-prone)

- Dead enemies stay in `enemy_list` for 0.5 s while the explosion animates. Always check `enemy.dead` in movement, direction reversal, firing, and collision passes; never use `len(enemy_list)` as the live-enemy count.
- The formation is built column by column from the top row (row 0 = y=720; scores 10→20→30 top to bottom). Firing picks the *lowest* live enemy per column — the list is iterated backwards for that reason.
- One bullet = one kill (`break` after the first live hit), and `break` after the player-hit `clear()` — otherwise multiple lives are lost in one frame.
- Replays go through `GameView.setup()`, which rebuilds all sprite lists. Flow: game over → Space → `InstructionView` → click or Space → fresh `GameView().setup()`.
- Pause (P) is checked at the top of `on_update` and must stay there, ahead of the death-pause countdown. Every player input path (mouse motion, `shoot()`, keyboard movement) must also check `self.paused`; P itself must still work while paused.
- Space is dual-purpose by design: GAME_OVER → restart (to `InstructionView`); during play → fire. The GAME_OVER branch in `on_key_press` must `return` before any play handling.
