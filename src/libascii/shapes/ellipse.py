from typing import override

from math import ceil, floor, sqrt

from ..color import Color
from ..grid import Grid
from .shape import StyledShape


_ELLIPSE_EPSILON = 1e-9


class Ellipse(StyledShape):
    @override
    def draw(self, grid: Grid, x: int = 0, y: int = 0) -> None:
        width = self.width
        height = self.height
        if width == 0 or height == 0:
            return
        ox, oy = x, y

        key = (width, height)
        if getattr(self, "_ellipse_cache_key", None) != key:
            cx = (width - 1) / 2
            cy = (height - 1) / 2
            rx = max((width - 1) / 2, _ELLIPSE_EPSILON)
            ry = max((height - 1) / 2, _ELLIPSE_EPSILON)
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
            self._ellipse_cache_key = key
            self._ellipse_intervals = intervals
        intervals = self._ellipse_intervals

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

        cells: list[tuple[int, int, str, Color | None]] = []

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
                    c = border_color
                else:
                    ch = fill
                    c = fill_color
                gx = x + ox
                gy = y + oy
                if not (0 <= gx < grid.width and 0 <= gy < grid.height):
                    continue
                cells.append((gx, gy, ch, c))

        if cells:
            grid.set_many_unchecked(cells)
