from ..grid import Grid
from .shape import StyledShape


class Rectangle(StyledShape):
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
