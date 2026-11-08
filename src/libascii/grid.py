from libascii.color import Color


class Grid:
    def __init__(self, width: int, height: int, filler: str = " ") -> None:
        if width <= 0 or height <= 0:
            msg = "width and height must be positive"
            raise ValueError(msg)
        self.width = width
        self.height = height
        self.filler = filler
        self._content: list[list[str]] = [
            [filler for _ in range(width)] for _ in range(height)
        ]
        self._colors: list[list[Color | None]] = [
            [None for _ in range(width)] for _ in range(height)
        ]
        self._dirty: bool = False

    @property
    def content(self) -> list[list[str]]:
        return self._content

    @property
    def colors(self) -> list[list[Color | None]]:
        return self._colors

    @property
    def dirty(self) -> bool:
        return self._dirty

    def mark_clean(self) -> None:
        self._dirty = False

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def _check_bounds(self, x: int, y: int) -> None:
        if not self.in_bounds(x, y):
            msg = (
                f"coordinates ({x}, {y}) out of bounds for grid "
                f"{self.width}x{self.height}"
            )
            raise IndexError(msg)

    def set(
        self,
        x: int,
        y: int,
        char: str = "",
        color: Color | None = None,
    ) -> None:
        self._check_bounds(x, y)
        self._content[y][x] = char
        self._colors[y][x] = color
        self._dirty = True

    def set_many(
        self, cells: list[tuple[int, int, str, Color | None]]
    ) -> None:
        content = self._content
        colors = self._colors
        width = self.width
        height = self.height
        for x, y, char, color in cells:
            if 0 <= x < width and 0 <= y < height:
                content[y][x] = char
                colors[y][x] = color
        self._dirty = True

    def get(self, x: int, y: int) -> tuple[str, Color | None]:
        self._check_bounds(x, y)
        return self._content[y][x], self._colors[y][x]

    def __getitem__(self, key: tuple[int, int]) -> tuple[str, Color | None]:
        return self.get(*key)

    def __setitem__(
        self,
        key: tuple[int, int],
        value: tuple[str, Color | None],
    ) -> None:
        x, y = key
        char, color = value
        self.set(x, y, char, color)

    def fill(self, char: str = "", color: Color | None = None) -> None:
        content = self._content
        colors = self._colors
        width = self.width
        for y in range(self.height):
            content[y] = [char] * width
            colors[y] = [color] * width
        self._dirty = True

    def clear(self) -> None:
        self.fill(self.filler, None)

    def __repr__(self) -> str:
        return (
            f"Grid(width={self.width}, height={self.height}, "
            f"filler={self.filler!r})"
        )
