from ..color import Color
from ..grid import Grid
from .shape import Shape


class Line(Shape):
    def __init__(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        char: str = "#",
        color: Color = Color(""),
    ) -> None:
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.char = char
        self.color = color

    def draw(self, grid: Grid) -> None:
        x0, y0 = self.x1, self.y1
        x1, y1 = self.x2, self.y2
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy

        while True:
            grid.set(x0, y0, self.char, self.color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
