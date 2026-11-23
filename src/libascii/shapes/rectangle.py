from typing import override

from ..color import Color
from ..grid import Grid
from .shape import StyledShape


class Rectangle(StyledShape):
    @override
    def draw(self, grid: Grid, x: int = 0, y: int = 0) -> None:
        width = self.width
        height = self.height

        fill = self.fill
        fill_color = self.fill_color
        border_color = self.border_color
        last_y = height - 1
        last_x = width - 1

        cells: list[tuple[int, int, str, Color | None]] = []

        if fill:
            for y_i in range(height):
                for x_i in range(width):
                    cell_x = x + x_i
                    cell_y = y + y_i
                    if grid.in_bounds(cell_x, cell_y):
                        cells.append((cell_x, cell_y, fill, fill_color))

        for x_i in range(width):
            cell_x = x + x_i
            cell_y = y
            if grid.in_bounds(cell_x, cell_y):
                top_char = self._border_char(x_i, 0, left=0, right=last_x)
                if not top_char:
                    continue
                cells.append((cell_x, cell_y, top_char, border_color))

        if height > 1:
            for x_i in range(width):
                cell_x = x + x_i
                cell_y = y + last_y
                if grid.in_bounds(cell_x, cell_y):
                    bottom_char = self._border_char(
                        x_i, last_y, left=0, right=last_x
                    )
                    if not bottom_char:
                        continue
                    cells.append((cell_x, cell_y, bottom_char, border_color))

        if width > 1:
            for y_i in range(1, last_y):
                cell_x = x
                cell_y = y + y_i
                if grid.in_bounds(cell_x, cell_y):
                    left_char = self._border_char(0, y_i, left=0, right=last_x)
                    if not left_char:
                        continue
                    cells.append((cell_x, cell_y, left_char, border_color))
                cell_x = x + last_x
                if grid.in_bounds(cell_x, cell_y):
                    right_char = self._border_char(
                        last_x, y_i, left=0, right=last_x
                    )
                    if not right_char:
                        continue
                    cells.append((cell_x, cell_y, right_char, border_color))

        if cells:
            grid.set_many_unchecked(cells)
