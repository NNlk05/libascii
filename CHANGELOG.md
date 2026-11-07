# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
      