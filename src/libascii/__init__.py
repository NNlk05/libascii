from __future__ import annotations

from typing import TYPE_CHECKING, Literal, overload

if TYPE_CHECKING:
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


@overload
def __getattr__(name: Literal["Color"]) -> type[Color]: ...


@overload
def __getattr__(name: Literal["Grid"]) -> type[Grid]: ...


@overload
def __getattr__(name: Literal["CharLib"]) -> CharLib: ...


@overload
def __getattr__(name: Literal["Game"]) -> type[Game]: ...


@overload
def __getattr__(name: Literal["Shape"]) -> type[Shape]: ...


@overload
def __getattr__(name: Literal["Rectangle"]) -> type[Rectangle]: ...


@overload
def __getattr__(name: Literal["Ellipse"]) -> type[Ellipse]: ...


@overload
def __getattr__(name: Literal["Triangle"]) -> type[Triangle]: ...


@overload
def __getattr__(name: Literal["Line"]) -> type[Line]: ...


@overload
def __getattr__(name: Literal["Sound"]) -> type[Sound]: ...


@overload
def __getattr__(name: str) -> object: ...


def __getattr__(name: str) -> object:
    match name:
        case "Color":
            from .color import Color

            return Color
        case "Grid":
            from .grid import Grid

            return Grid
        case "CharLib":
            from .chars import CharLib

            return CharLib
        case "Game":
            from .game import Game

            return Game
        case "Shape":
            from .shapes.shape import Shape

            return Shape
        case "Rectangle":
            from .shapes.rectangle import Rectangle

            return Rectangle
        case "Ellipse":
            from .shapes.ellipse import Ellipse

            return Ellipse
        case "Triangle":
            from .shapes.triangle import Triangle

            return Triangle
        case "Line":
            from .shapes.line import Line

            return Line
        case "Sound":
            from .sound import Sound

            return Sound
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
