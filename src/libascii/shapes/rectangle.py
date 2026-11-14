from typing import override

from ..color import Color
from ..grid import Grid
from .shape import StyledShape


class Rectangle(StyledShape):
    @override
    def draw(self, grid: Grid, x: int = 0, y: int = 0) -> None:
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
            for y_i in range(1, last_y):
                for x_i in range(1, last_x):
                    cell_x = x + x_i
                    cell_y = y + y_i
                    if grid.in_bounds(cell_x, cell_y):
                        cells.append((cell_x, cell_y, fill, fill_color))

        top_char = border_top or border
        for x_i in range(width):
            cell_x = x + x_i
            cell_y = y
            if grid.in_bounds(cell_x, cell_y):
                cells.append((cell_x, cell_y, top_char, border_color))

        if height > 1:
            bottom_char = border_bottom or border
            for x_i in range(width):
                cell_x = x + x_i
                cell_y = y + last_y
                if grid.in_bounds(cell_x, cell_y):
                    cells.append((cell_x, cell_y, bottom_char, border_color))

        if width > 1:
            left_char = border_left or border
            right_char = border_right or border
            for y_i in range(1, last_y):
                cell_x = x
                cell_y = y + y_i
                if grid.in_bounds(cell_x, cell_y):
                    cells.append((cell_x, cell_y, left_char, border_color))
                cell_x = x + last_x
                if grid.in_bounds(cell_x, cell_y):
                    cells.append((cell_x, cell_y, right_char, border_color))

        if cells:
            grid.set_many_unchecked(cells)
