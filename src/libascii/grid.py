from libascii.color import Color


class Grid:
    def __init__(self, width: int, height: int, filler: str = " ") -> None:
        self.width = width
        self.height = height
        self.filler = filler
        self.content: list[list[str]] = [
            [filler for _ in range(width)] for _ in range(height)
        ]
        self.colors: list[list[Color | None]] = [
            [None for _ in range(width)] for _ in range(height)
        ]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def set(
        self,
        x: int,
        y: int,
        char: str = "",
        color: Color | None = None,
    ) -> None:
        self.content[y][x] = char
        self.colors[y][x] = color

    def set_many(
        self, cells: list[tuple[int, int, str, Color | None]]
    ) -> None:
        for x, y, char, color in cells:
            self.set(x, y, char, color)

    def get(self, x: int, y: int) -> tuple[str, Color | None]:
        return self.content[y][x], self.colors[y][x]

    def fill(self, char: str = "", color: Color | None = None) -> None:
        for y in range(self.height):
            for x in range(self.width):
                self.content[y][x] = char
                self.colors[y][x] = color

    def clear(self) -> None:
        self.fill(self.filler, None)
