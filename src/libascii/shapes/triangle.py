from ..color import Color
from ..grid import Grid
from .shape import Shape


class Triangle(Shape):
    def __init__(
        self,
        width: int,
        height: int,
        fill: str = "",
        border: str = "",
        fill_color: Color = Color(""),
        border_color: Color = Color(""),
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
        self.border_left = border_left
        self.border_right = border_right
        self.border_bottom = border_bottom

    def draw(self, grid: Grid) -> None:
        if self.height == 0 or self.width == 0:
            return

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

        for y in range(self.height):
            xs = []
            for a, b in edges:
                x = edge_x(a, b, y)
                if x is not None:
                    xs.append(x)
            if len(xs) < 2:
                continue
            left = int(round(min(xs)))
            right = int(round(max(xs)))
            for x in range(left, right + 1):
                if x < 0 or x >= self.width:
                    continue
                on_border = x == left or x == right or y == self.height - 1
                if on_border:
                    grid.set(
                        x,
                        y,
                        self._border_char(x, y, left, right),
                        self.border_color,
                    )
                else:
                    grid.set(x, y, self.fill, self.fill_color)

    def _border_char(self, x: int, y: int, left: int, right: int) -> str:
        if y == self.height - 1 and self.border_bottom:
            return self.border_bottom
        if x == left and self.border_left:
            return self.border_left
        if x == right and self.border_right:
            return self.border_right
        return self.border
