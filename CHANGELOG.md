# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Lots of optimization

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

>[!WARNING] I wiped my work and accidentally published 0.2.0. Please use 0.2.1

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
      