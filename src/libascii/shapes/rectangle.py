from typing import override

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

        dirty_cells = grid._dirty_cells

        if fill:
            for y in range(1, last_y):
                row = grid.content[y]
                color_row = grid.colors[y]
                for x in range(1, last_x):
                    row[x] = fill
                    color_row[x] = fill_color
                    dirty_cells.add((x, y))

        top_row = grid.content[0]
        top_color_row = grid.colors[0]
        top_char = border_top or border
        for x in range(width):
            top_row[x] = top_char
            top_color_row[x] = border_color
            dirty_cells.add((x, 0))

        if height > 1:
            bottom_row = grid.content[last_y]
            bottom_color_row = grid.colors[last_y]
            bottom_char = border_bottom or border
            for x in range(width):
                bottom_row[x] = bottom_char
                bottom_color_row[x] = border_color
                dirty_cells.add((x, last_y))

        if width > 1:
            left_char = border_left or border
            right_char = border_right or border
            for y in range(1, last_y):
                row = grid.content[y]
                color_row = grid.colors[y]
                row[0] = left_char
                color_row[0] = border_color
                row[last_x] = right_char
                color_row[last_x] = border_color
                dirty_cells.add((0, y))
                dirty_cells.add((last_x, y))
