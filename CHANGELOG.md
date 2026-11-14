# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `Game.run(callback)` pumps frames at `fps` and calls `refresh()` each frame
- `Game.camera` / `Game.set_camera()`; `Game` accepts `camera: Camera | None` and passes it to `renderer.render`
- `SceneManager.clear()` exits all scenes and empties the stack 
- `Shape.draw(grid, x=0, y=0)` and all shapes accept an optional draw offset
- `draw_text()` accepts a single `str` (split on `"\n"`) in addition to `list[str]`
- `Color.from_hex()` accepts `#RGB` shorthand (e.g. `#f00`) in addition to `#RRGGBB`
- A `TerminalRenderer`
- `ParticleSystem.update()` filters in place instead of reallocing a list.

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
- Replace `Grid.dirty_region()` with `Grid.dirty_regions()` returning a list of rectangles. `Game.refresh()` renders each region separately so scattered cells no longer force the whole grid to be redrawn.
- `CharLib.get_char()` raises `ValueError` (not `KeyError`) for unknown category/name
- `import libascii` does not import tkinter or simpleaudio (improve load time)

### Fixed

- `TerminalRenderer.start()` no longer blocks indefinitely

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
