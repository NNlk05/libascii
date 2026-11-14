from __future__ import annotations

import importlib
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .camera import Camera
    from .chars import CharLib
    from .color import Color
    from .collision import grid_cell_overlap, point_in_rect, rect_overlap
    from .game import Game
    from .grid import Grid
    from .input import ActionMap
    from .particle import Particle, ParticleSystem
    from .scene import Scene, SceneManager
    from .shapes.ellipse import Ellipse
    from .shapes.line import Line
    from .shapes.rectangle import Rectangle
    from .shapes.shape import Shape
    from .shapes.triangle import Triangle
    from .sound import Sound
    from .sprite import Sprite
    from .text import align, draw_text, wrap
    from .tilemap import Tilemap
    from .renderers.terminal import TerminalRenderer

_IMPORT_MAP_ENTRIES = [
    ("Camera", ".camera", "Camera"),
    ("Color", ".color", "Color"),
    ("Grid", ".grid", "Grid"),
    ("CharLib", ".chars", "CharLib"),
    ("Game", ".game", "Game"),
    ("Shape", ".shapes.shape", "Shape"),
    ("Rectangle", ".shapes.rectangle", "Rectangle"),
    ("Ellipse", ".shapes.ellipse", "Ellipse"),
    ("Triangle", ".shapes.triangle", "Triangle"),
    ("Line", ".shapes.line", "Line"),
    ("Sound", ".sound", "Sound"),
    ("Sprite", ".sprite", "Sprite"),
    ("Tilemap", ".tilemap", "Tilemap"),
    ("ActionMap", ".input", "ActionMap"),
    ("Particle", ".particle", "Particle"),
    ("ParticleSystem", ".particle", "ParticleSystem"),
    ("Scene", ".scene", "Scene"),
    ("SceneManager", ".scene", "SceneManager"),
    ("rect_overlap", ".collision", "rect_overlap"),
    ("point_in_rect", ".collision", "point_in_rect"),
    ("grid_cell_overlap", ".collision", "grid_cell_overlap"),
    ("wrap", ".text", "wrap"),
    ("align", ".text", "align"),
    ("draw_text", ".text", "draw_text"),
    ("TerminalRenderer", ".renderers.terminal", "TerminalRenderer"),
]

__all__ = [name for name, _, _ in _IMPORT_MAP_ENTRIES]

_IMPORT_MAP = {
    name: (module_path, attr)
    for name, module_path, attr in _IMPORT_MAP_ENTRIES
}


def __getattr__(name: str) -> object:
    entry = _IMPORT_MAP.get(name)
    if entry is None:
        msg = f"module {__name__!r} has no attribute {name!r}"
        raise AttributeError(msg)
    module_path, attr = entry
    module = importlib.import_module(module_path, __name__)
    value = getattr(module, attr)
    setattr(sys.modules[__name__], name, value)
    return value
