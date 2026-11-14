from typing import override

from ..color import Color
from ..grid import Grid
from .shape import StyledShape


class Rectangle(StyledShape):
    @override
    def draw(self, grid: Grid) -> None:
        width = self.width
        height = self.height
        if width == 0 or height == 0:
            return

        fill = self.fill
        fill_color = self.fill_color
        border = self.border
        border_color = self.border_color
        border_top = self.border_top
        border_bottom = self.border_bottom
        border_left = self.border_left
        border_right = self.border_right
        last_y = height - 1
        last_x = width - 1

        cells: list[tuple[int, int, str, Color | None]] = []

        if fill:
            for y in range(1, last_y):
                for x in range(1, last_x):
                    cells.append((x, y, fill, fill_color))

        top_char = border_top or border
        for x in range(width):
            cells.append((x, 0, top_char, border_color))

        if height > 1:
            bottom_char = border_bottom or border
            for x in range(width):
                cells.append((x, last_y, bottom_char, border_color))

        if width > 1:
            left_char = border_left or border
            right_char = border_right or border
            for y in range(1, last_y):
                cells.append((0, y, left_char, border_color))
                cells.append((last_x, y, right_char, border_color))

        if cells:
            grid.set_many_unchecked(cells)
