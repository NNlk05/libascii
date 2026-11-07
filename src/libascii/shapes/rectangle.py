from ..color import Color
from ..grid import Grid
from .shape import Shape


class Rectangle(Shape):
    def __init__(
        self,
        width: int,
        height: int,
        fill: str = "",
        border: str = "",
        fill_color: Color = Color(""),
        border_color: Color = Color(""),
        border_top: str = "",
        border_left: str = "",
        border_right: str = "",
        border_bottom: str = "",
    ) -> None:
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

    def draw(self, grid: Grid) -> None:
        for y in range(self.height):
            for x in range(self.width):
                on_border = (
                    x == 0
                    or x == self.width - 1
                    or y == 0
                    or y == self.height - 1
                )
                if on_border:
                    grid.set(x, y, self._border_char(x, y), self.border_color)
                else:
                    grid.set(x, y, self.fill, self.fill_color)

    def _border_char(self, x: int, y: int) -> str:
        if y == 0 and self.border_top:
            return self.border_top
        if y == self.height - 1 and self.border_bottom:
            return self.border_bottom
        if x == 0 and self.border_left:
            return self.border_left
        if x == self.width - 1 and self.border_right:
            return self.border_right
        return self.border
