# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- `Game.run()` now wrap the frame loop in `try/finally` calling `self.stop()` so that a callback exception no longer leaves the Tk mainloop running or a terminal in raw mode with the cursor hidden, etc. removed the manual `refresh()` call so `refresh` is called exactly once per frame by the renderer frame loop. added a `threading.Lock` (`_refresh_lock`) serializing concurrent `refresh()` calls (Terminal `InputDriver` thread vs main thread).
- `HeadlessRenderer.tick()`: now calls `update()` so `refresh` (and other frame bindings!) dispatch exactly once per frame instead of twice. removed an incorrect `@override`.
- `SceneManager.push()`/`pop()`/`replace()`/`clear()` now calls `enter()`/`exit()` before mutating the stack, so a failed `enter()`/`exit()` leaves the stack structurally correct instead of a half-entered or lost scene.
- `ActionMap`: all mutation (`key_down`/`key_up`/`tick`/`bind_action`/`unbind_action`/`close`) and read (`is_pressed`/`was_pressed`/`is_held`/etc) paths are now guarded by a `threading.Lock`, eliminating wrong `is_held()` and unreliable `was_pressed()` under access from multiple threads.
- `Grid.set_many_unchecked()`: validates every cell's bounds upfront and raises `IndexError` before writing, so negative coordinates no longer silently corrupt adjacent cells becuase Python negative indexing.
## [0.5.0] - 2026-11-20

### Added

- `Game.run(callback)` pumps frames at `fps` and calls `refresh()` each frame
- `Game.camera` / `Game.set_camera()`; `Game` accepts `camera: Camera | None` and passes it to `renderer.render`
- `SceneManager.clear()` exits all scenes and empties the stack 
- `Shape.draw(grid, x=0, y=0)` and all shapes accept an optional draw offset
- `draw_text()` accepts a single `str` (split on `"\n"`) in addition to `list[str]`
- `Color.from_hex()` accepts `#RGB` shorthand (e.g. `#f00`) in addition to `#RRGGBB`
- A `TerminalRenderer`
- `ParticleSystem.update()` filters in place instead of reallocing a list.
- `Game.run(callback)` pumps frames at `fps` and calls `refresh()` each frame
- `Game.camera` / `Game.set_camera()`; `Game` accepts `camera: Camera | None` and passes it to `renderer.render`
- `SceneManager.clear()` exits all scenes and empties the stack 
- `Shape.draw(grid, x=0, y=0)` and all shapes accept an optional draw offset
- `draw_text()` accepts a single `str` (split on `"\n"`) in addition to `list[str]`
- `Color.from_hex()` accepts `#RGB` shorthand (e.g. `#f00`) in addition to `#RRGGBB`
- A `TerminalRenderer`
- `ParticleSystem.update()` filters in place instead of reallocing a list.
- `Renderer.update()` non-blocking frame pump on `Renderer` ABC

### Changed

- `ParticleSystem.update()` filters dead particles in place
- `Sprite` caches mirrored frames; invalidates on flip/frame change
- `Sprite.from_xpm_string()` validates input
- `Triangle.draw()` batches cells into a single `set_many_unchecked` call
- `Ellipse.draw()` hoists lookups out of the cell loop and caches intervals
- `Ellipse`/`Rectangle`/`Line`/`Triangle` apply the `x`/`y` draw offset
- `StyledShape.fill_color`/`border_color` default to `None` instead of `Color("")`
- `TerminalRenderer._row_runs` compares colors by value (`==`) not identity (`is`)
- Terminal input thread `select` timeout is tied to the remaining frame interval
- `TerminalRenderer.start()` no longer blocks joining the input thread
- `wrap()` builds lines with a word list + `" ".join()` and uses `str.split()`
- `align()` truncates lines longer than `width` to exactly `width` columns
- `wrap("", width)` still returns `[]`; `wrap(text, width)` with `width <= 0` raises `ValueError`
- `SceneManager.replace()` raises `IndexError` on an empty stack, matching `pop()`
- `Camera.follow()` centers using `(viewport - 1) // 2` (API-28)
- `__all__` and `_IMPORT_MAP` are generated from a single source
- Lazy `__getattr__` caches resolved attributes on the module
- `Grid._dirty_cells` replaced with a 2D dirty-flag array + counts (`_dirty_flags` and `_dirty_count`), eliminating the overhead of per-cell tuples
- `Grid.content`/`Grid.colors` return `tuple(tuple(...))` views instead of raw lists, stopping external mutation bypassing dirty tracking.
- `Grid.mark_cells_clean()` no longer iterates all dirty cells to recompute a bounding box. bbox fields are removed entirely.
- `CharLib.get_char()` raises `ValueError` (not `KeyError`) for unknown category/name
- `import libascii` does not import tkinter or playsound3
- `Grid.dirty_region()` replaced with `Grid.dirty_regions()` returning per-row dirty rectangles; `Game.refresh()` renders each separately so scattered cells no longer force the whole grid to be redrawn.
- `_InputDriver` no longer holds a `TerminalRenderer` reference; frame/key/mouse bindings are now injected.
- Terminal setup/restore exceptions narrowed. Terminal state restored via `atexit`/`finally`.
- Terminal `_NAMED_COLORS` bright variants use distinct RGB values instead of duplicating normal colors.
- `StyledShape._border_char` uses `left`/`right` boundary params. `Triangle` no longer overrides semantics.
- `Tilemap.tile_grid`/`tileset` encapsulated behind read-only properties.
- `expand_keybinding`/`keybinding_to_events`: `{a,b}` choices emit separate key combos (not modifiers). Unknown `[modifier]` validated. The combination count is capped at 64.
- `Game.refresh()` renders the debug line as a separate region instead of folding it into dirty tracking.
- `sound.py` reduced `cast()` usage.
- Magic numbers replaced with named constants: `_FRAME_INTERVAL_MS` (tk), `_ELLIPSE_EPSILON` (ellipse), `_MAX_READ_BYTES` (terminal).
- `TkRenderer.start()` no longer blocks on `root.mainloop()`; returns immediately after scheduling `_tick` via `root.after()`
- `Game.run()` drives the frame loop calling `renderer.update()` each frame; previously unreachable with the default `TkRenderer`
- `Game.start()`/`stop()` are non-blocking; `with Game(...) as game:` no longer blocks with `TkRenderer`
- `Game.refresh()` is now called automatically each frame by the renderer frame loop, so that `start()`/`stop()`,  along with `with Game(...) as game:` render without needing a manual call to `refresh()`
- `Renderer`/`BindingMixin` moved to `src/libascii/_renderers/base.py`; `renderers/__init__.py` lazy-loads concrete renderers via `__getattr__` so `import libascii.renderers` does not import `tkinter`
- `TkRenderer` imported lazily inside `Game.__init__` only when no renderer is provided
- `Grid._expand_dirty(x0, y0, x1, y1)` now tracks a dirty bounding box instead of being a no-op
- `Grid.mark_clean()` resets dirty flags in-place instead of reallocating the `width × height` 2D list each frame
- `Grid.fill()` resets dirty flags in-place and `_dirty_count = 0` before marking fully dirty
- `Grid.mark_clean()` resets only cells dirtied since the last clean instead of scanning the whole grid.
- `Grid.dirty_cells()` now builds its frozenset from the dirty-cell list (O(n dirty cells)) instead of scanning the whole grid (O(w×h)).
- `Grid.dirty_regions()` groups dirty rows with overlapping x- into multiple rectangles instead of one, so scattered cells no longer force to redraw the whole grid.
- `TkRenderer._apply_colors()` skips rows that were not wiped or had a color change, avoiding scanning all cells when colors are unchanged.
- `ParticleSystem.update()` now compacts dead particles in place with a write index, avoiding a list allocation on every frame with particle deaths.
- `Grid.mark_cells_clean()` resets `_fully_dirty` and bounding box when dirty count reaches zero
- `Game.refresh()` calls `grid.mark_clean()` when `dirty_regions()` returns empty but the grid is dirty, preventing a stuck-dirty state
- `set_text()` raises `IndexError` for out-of-bounds `x` as well as `y`, matching `set`/`get` (previously clipped `x` silently)
- `__setitem__()` accepts `(x, y, char, color)` tuples matching `set_many()` (previously `(char, color)`)
- `Line.color` defaults to `None` instead of `Color("")`, matching other shapes
- Fixed `Rectangle.draw()` so that the border-character selection is handled by `StyledShape._border_char()`
- `TerminalRenderer.render()` applies `camera` offset/viewport in `_render_full()`, matching `TkRenderer`
- `TerminalRenderer.on_key_down()`/`on_key_up()` expand keybindings via `expand_keybinding()` so everything work identically across renderers
- `TerminalRenderer._dispatch_key()`/`_dispatch_mouse()` no longer swallow exceptions (as per the Zen of Python)
- `draw_text()` raises `IndexError` for out-of-bounds `y`, to match `set_text()`
- `Grid.fill()` skips dirty marking when the grid is the same as the fill char/color. Also added `force` parameter to force a redraw.
- `TerminalRenderer._hide_cursor()`/`_show_cursor()` no longer swallow all `Exception`s. Changed to`OSError`.
- `Game.unbind_action(name)` added to remove a action binding.
- `Game.is_pressed()`/`was_pressed()`/`is_held()` added to align with `ActionMap`, alongside with `action_is_pressed()`/`action_was_pressed()`/`action_is_held()` as aliases.

### Fixed

- `Game.run()` loop unreachable with default `TkRenderer` (blocked on `mainloop()`)
- Stuck-dirty state when `dirty_regions()` returned `[]` while `grid.dirty` was `True`
- Import-light guarantee: `import libascii` no longer imports `tkinter` or `playsound3`
- `TerminalRenderer.start()` no longer blocks indefinitely
- `TerminalRenderer.start()` no longer renders an empty grid.
- `demos/tetris.py`: `run()` now keeps the program alive with a loop.
- `TkRenderer.render()` rebuilds the widget's line structure (aka newlines between rows) when the row cache length changes, to fix a collapsed one-line widget that made `clear()`/`draw()` frames to pile everything onto the first row.

## [0.4.0] - 2026-11-08

### Added

- A particle system
- Collision system
- A stack-based `Scene`  system for creating, managing, and enter/exiting scenes
- More tests
- Text utils in `text.py`
- `font_size` pram in `Game` for controlling font size

### Changed

- Some dict keys in `libascii.chars` have been renamed (`BLACK` to `FILLED` and all `WHITE` to `OUTLINE`) to better fit now the grid is colored.

### [0.3.0] - 2026-11-07

### Added

- Tests
- A `_show_debug` flag to show debug info
- A `Camera` class; for only displaying a small part ("viewport") of the whole grid
- A `Spite` class for creating sprites, includes serialize and deserialize from a XPM-like format.
- A `Tilemap` class for creating a tilesets and tilemaps for displaying on the grid
- A `ActionMap` class for better and cleaner binding of keys

### Changed

- Lots of optimization, including dirty flag on grid to prevent unnecessary rendering

## [0.2.2] - 2026-11-07

### Fixed

- `TkRender` now no longer bubble key presses

## [0.2.1] - 2026-11-07

### Changed

- `Game` is now backend-agnostic: rendering is handled by a `Renderer`
  (`libascii._renderers.Renderer`). `TkRenderer` (using tkinter) is the default. a
  `HeadlessRenderer` is used for tests.
- `Game` callbacks receive Python arguments (key `str`, cell `(x, y)`)
  instead of `tk.Event` objects.
- `Game` is now a context manager(`with Game(...) as game:`).
- `Game.fps` is validated to be positive; `Renderer.set_fps` validates too.
- `Grid.set`/`Grid.get` now raise `IndexError` when out of bounds. added
  `__getitem__`/`__setitem__` and `__repr__`. `content`/`colors`
  are exposed via read-only properties.
- `Grid`, `Rectangle`, `Ellipse`, `Triangle` reject negative width/height.
- `Color` now has `__eq__`, `__hash__`, and `__repr__`.
- `Rectangle`, `Ellipse`, `Triangle` share a `StyledShape` base class; mutable
  `Color("")` defaults replaced with `None` in `__init__`.
- `Sound.from_wav` removed (constructor already accepts a path).
- `chars.get_char(category, name)` added as a typed accessor for `CharLib`.
- `__init__.py` simplified: removed redundant `@overload` declarations;
  added `__all__`.

## [0.2.0] - 2026-11-07

> [!WARNING] I wiped my work and accidentally published 0.2.0. Please use 0.2.1

### Changed

- `Game` is now backend-agnostic: rendering is handled by a `Renderer`
  (`libascii._renderers.Renderer`). `TkRenderer` (using tkinter) is the default. a
  `HeadlessRenderer` is used for tests.
- `Game` callbacks receive Python arguments (key `str`, cell `(x, y)`)
  instead of `tk.Event` objects.
- `Game` is now a context manager(`with Game(...) as game:`).
- `Game.fps` is validated to be positive; `Renderer.set_fps` validates too.
- `Grid.set`/`Grid.get` now raise `IndexError` when out of bounds. added
  `__getitem__`/`__setitem__` and `__repr__`. `content`/`colors`
  are exposed via read-only properties.
- `Grid`, `Rectangle`, `Ellipse`, `Triangle` reject negative width/height.
- `Color` now has `__eq__`, `__hash__`, and `__repr__`.
- `Rectangle`, `Ellipse`, `Triangle` share a `StyledShape` base class; mutable
  `Color("")` defaults replaced with `None` in `__init__`.
- `Sound.from_wav` removed (constructor already accepts a path).
- `chars.get_char(category, name)` added as a typed accessor for `CharLib`.
- `__init__.py` simplified: removed redundant `@overload` declarations;
  added `__all__`.

## [0.1.1] - 2026-11-06

## Added

- Added README

### Fixed

- Bumped deps
- Fixed leftover "asciilib" from rename

## [0.1.0] - 2026-11-06

### Added

The base and core package `libascii`

- `src/libascii` - package root
  - `libascii.__init__` - a `__init__.py` file containing a lazy loader.
  - `libascii.chars` - A library of ASCII and Unicode characters to use.
  - `libascii.color` - A `Color` class for defining colors for the rest of the package.
  - `libascii.game` - the basic `Game` class for creating a game.
  - `libascii.grid` - Bare `Grid` class representing the `Game` grid.
  - `libascii.sound` - A `Sound` class which acts as a wrapper around `simpleaudio`.
    - `libascii.shapes` - Shapes to draw on the `Game` canvas
      - `libascii.shapes.__init__.py` - Re-exporting various shape classes from different files.
      - `libascii.shapes.ellipse` - Ellipses
      - `libascii.shapes.rectangle` - Rectangles
      - `libascii.shapes.shape` - Base shape class
      - `libascii.shapes.triangle` - Triangles
