from abc import ABC, abstractmethod

from ..color import Color
from ..grid import Grid


class Shape(ABC):
    @abstractmethod
    def draw(self, grid: Grid, x: int = 0, y: int = 0) -> None:
        pass


class StyledShape(Shape):
    def __init__(
        self,
        width: int,
        height: int,
        fill: str = "",
        border: str = "",
        fill_color: Color | None = None,
        border_color: Color | None = None,
        border_top: str = "",
        border_left: str = "",
        border_right: str = "",
        border_bottom: str = "",
    ) -> None:
        if width <= 0 or height <= 0:
            msg = "width and height must be positive"
            raise ValueError(msg)
        self.width = width
        self.height = height
        self.fill = fill
        self.border = border
        self.fill_color = fill_color
        self.border_color = border_color
        self.border_top = border_top
        self.border_left = border_left
        self.border_right = border_right
        self.border_bottom = border_bottom

    def _border_char(
        self, x: int, y: int, left: int = 0, right: int = 0
    ) -> str:
        if y == 0 and self.border_top:
            return self.border_top
        if y == self.height - 1 and self.border_bottom:
            return self.border_bottom
        if x == 0 and self.border_left:
            return self.border_left
        if x == self.width - 1 and self.border_right:
            return self.border_right
        return self.border
