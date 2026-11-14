from typing import override

from ..color import Color
from ..grid import Grid
from .shape import StyledShape


class Triangle(StyledShape):
    @override
    def draw(self, grid: Grid, x: int = 0, y: int = 0) -> None:
        if self.height == 0 or self.width == 0:
            return
        ox, oy = x, y

        top = (self.width // 2, 0)
        bottom_left = (0, self.height - 1)
        bottom_right = (self.width - 1, self.height - 1)

        def edge_x(
            a: tuple[int, int],
            b: tuple[int, int],
            y: int,
        ) -> float | None:
            (x0, y0), (x1, y1) = a, b
            if y0 == y1 or y < min(y0, y1) or y > max(y0, y1):
                return None
            return x0 + (x1 - x0) * (y - y0) / (y1 - y0)

        edges = (
            (top, bottom_left),
            (top, bottom_right),
            (bottom_left, bottom_right),
        )

        fill = self.fill
        fill_color = self.fill_color
        border_color = self.border_color
        border_bottom = self.border_bottom
        border_left = self.border_left
        border_right = self.border_right
        border = self.border

        cells: list[tuple[int, int, str, Color | None]] = []

        for y in range(self.height):
            xs = []
            for a, b in edges:
                ex = edge_x(a, b, y)
                if ex is not None:
                    xs.append(ex)
            if len(xs) < 2:
                continue
            left = int(round(min(xs)))
            right = int(round(max(xs)))
            for x in range(left, right + 1):
                gx = x + ox
                gy = y + oy
                if not (0 <= gx < grid.width and 0 <= gy < grid.height):
                    continue
                on_border = (
                    gx == left + ox
                    or gx == right + ox
                    or gy == self.height - 1 + oy
                )
                if on_border:
                    ch = self._border_char(x, y, left, right)
                    c = border_color
                else:
                    ch = fill
                    c = fill_color
                cells.append((gx, gy, ch, c))

        if cells:
            grid.set_many_unchecked(cells)

    @override
    def _border_char(
        self, x: int, y: int, left: int = 0, right: int = 0
    ) -> str:
        if y == self.height - 1 and self.border_bottom:
            return self.border_bottom
        if x == left and self.border_left:
            return self.border_left
        if x == right and self.border_right:
            return self.border_right
        return self.border
