from __future__ import annotations

import importlib
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .camera import Camera
    from .chars import CharLib
    from .color import Color
    from .game import Game
    from .grid import Grid
    from .shapes.ellipse import Ellipse
    from .shapes.line import Line
    from .shapes.rectangle import Rectangle
    from .shapes.shape import Shape
    from .shapes.triangle import Triangle
    from .sound import Sound

__all__ = [
    "Camera",
    "Color",
    "Grid",
    "CharLib",
    "Game",
    "Shape",
    "Rectangle",
    "Ellipse",
    "Triangle",
    "Line",
    "Sound",
]

_IMPORT_MAP = {
    "Camera": (".camera", "Camera"),
    "Color": (".color", "Color"),
    "Grid": (".grid", "Grid"),
    "CharLib": (".chars", "CharLib"),
    "Game": (".game", "Game"),
    "Shape": (".shapes.shape", "Shape"),
    "Rectangle": (".shapes.rectangle", "Rectangle"),
    "Ellipse": (".shapes.ellipse", "Ellipse"),
    "Triangle": (".shapes.triangle", "Triangle"),
    "Line": (".shapes.line", "Line"),
    "Sound": (".sound", "Sound"),
}


def __getattr__(name: str) -> object:
    entry = _IMPORT_MAP.get(name)
    if entry is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_path, attr = entry
    module = importlib.import_module(module_path, __name__)
    return getattr(module, attr)
