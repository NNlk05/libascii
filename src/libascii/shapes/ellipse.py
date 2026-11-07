from math import ceil, floor, sqrt

from ..grid import Grid
from .shape import StyledShape


class Ellipse(StyledShape):
    def draw(self, grid: Grid) -> None:
        width = self.width
        height = self.height
        if width == 0 or height == 0:
            return

        cx = (width - 1) / 2
        cy = (height - 1) / 2
        rx = max((width - 1) / 2, 1e-9)
        ry = max((height - 1) / 2, 1e-9)
        rx2 = rx * rx
        ry2 = ry * ry

        intervals: list[tuple[int, int] | None] = []
        for y in range(height):
            dy = (y - cy) / ry
            dy2 = dy * dy
            if dy2 > 1:
                intervals.append(None)
                continue
            dx_max = rx * sqrt(1.0 - dy2)
            x_left = ceil(cx - dx_max)
            x_right = floor(cx + dx_max)
            if x_left < 0:
                x_left = 0
            if x_right >= width:
                x_right = width - 1
            if x_left > x_right:
                intervals.append(None)
            else:
                intervals.append((x_left, x_right))

        fill = self.fill
        fill_color = self.fill_color
        border_color = self.border_color
        border_top = self.border_top
        border_bottom = self.border_bottom
        border_left = self.border_left
        border_right = self.border_right
        border = self.border
        last_y = height - 1
        last_x = width - 1

        content = grid.content
        colors = grid.colors

        for y in range(height):
            interval = intervals[y]
            if interval is None:
                continue
            x_left, x_right = interval

            prev = intervals[y - 1] if y > 0 else None
            nxt = intervals[y + 1] if y < last_y else None

            for x in range(x_left, x_right + 1):
                on_border = False

                if x == x_left or x == x_right:
                    on_border = True
                top_outside = y == 0 or (
                    prev is not None and (x < prev[0] or x > prev[1])
                )
                bottom_outside = y == last_y or (
                    nxt is not None and (x < nxt[0] or x > nxt[1])
                )
                on_border = (
                    x == x_left
                    or x == x_right
                    or top_outside
                    or bottom_outside
                )

                if on_border:
                    if y == 0 and border_top:
                        ch = border_top
                    elif y == last_y and border_bottom:
                        ch = border_bottom
                    elif x == x_left and border_left:
                        ch = border_left
                    elif x == x_right and border_right:
                        ch = border_right
                    else:
                        ch = border
                    content[y][x] = ch
                    colors[y][x] = border_color
                else:
                    content[y][x] = fill
                    colors[y][x] = fill_color
