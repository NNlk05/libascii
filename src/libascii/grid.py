from typing import override

from .color import Color


class Grid:
    __slots__ = (
        "width",
        "height",
        "filler",
        "_content",
        "_colors",
        "_dirty_flags",
        "_dirty_count",
        "_fully_dirty",
        "_dirty",
        "_dirty_min_x",
        "_dirty_min_y",
        "_dirty_max_x",
        "_dirty_max_y",
        "_clean_chars",
        "_clean_colors",
    )

    def __init__(self, width: int, height: int, filler: str = " ") -> None:
        if width <= 0 or height <= 0:
            msg = "width and height must be positive"
            raise ValueError(msg)
        self.width = width
        self.height = height
        self.filler = filler
        self._clean_chars: list[str] = [filler] * width
        self._clean_colors: list[Color | None] = [None] * width
        self._content: list[list[str]] = [
            list(self._clean_chars) for _ in range(height)
        ]
        self._colors: list[list[Color | None]] = [
            list(self._clean_colors) for _ in range(height)
        ]
        self._dirty_flags: list[list[bool]] = [
            [False] * width for _ in range(height)
        ]
        self._dirty_count: int = 0
        self._fully_dirty: bool = False
        self._dirty: bool = False
        self._dirty_min_x: int = 0
        self._dirty_min_y: int = 0
        self._dirty_max_x: int = 0
        self._dirty_max_y: int = 0

    @property
    def content(self) -> tuple[tuple[str, ...], ...]:
        return tuple(tuple(row) for row in self._content)

    @property
    def colors(self) -> tuple[tuple[Color | None, ...], ...]:
        return tuple(tuple(row) for row in self._colors)

    @property
    def dirty(self) -> bool:
        return self._fully_dirty or self._dirty or self._dirty_count > 0

    @property
    def dirty_cells(self) -> frozenset[tuple[int, int]]:
        return frozenset(
            (x, y)
            for y, row in enumerate(self._dirty_flags)
            for x, flag in enumerate(row)
            if flag
        )

    def mark_clean(self) -> None:
        self._dirty_flags = [[False] * self.width for _ in range(self.height)]
        self._dirty_count = 0
        self._fully_dirty = False
        self._dirty = False
        self._dirty_min_x = 0
        self._dirty_min_y = 0
        self._dirty_max_x = 0
        self._dirty_max_y = 0

    def mark_cells_clean(self, cells: list[tuple[int, int]]) -> None:
        height = self.height
        width = self.width
        dirty_flags = self._dirty_flags
        for x, y in cells:
            if 0 <= x < width and 0 <= y < height and dirty_flags[y][x]:
                dirty_flags[y][x] = False
                self._dirty_count -= 1
        if self._dirty_count == 0:
            self._dirty = False
            self._fully_dirty = False
            self._dirty_min_x = 0
            self._dirty_min_y = 0
            self._dirty_max_x = 0
            self._dirty_max_y = 0
        elif self._dirty:
            min_x = max_x = min_y = max_y = 0
            found = False
            for y, row in enumerate(self._dirty_flags):
                for x, flag in enumerate(row):
                    if not flag:
                        continue
                    if not found:
                        min_x = max_x = x
                        min_y = max_y = y
                        found = True
                    else:
                        if x < min_x:
                            min_x = x
                        if x > max_x:
                            max_x = x
                        if y < min_y:
                            min_y = y
                        if y > max_y:
                            max_y = y
            if found:
                self._dirty_min_x = min_x
                self._dirty_max_x = max_x
                self._dirty_min_y = min_y
                self._dirty_max_y = max_y

    def _expand_dirty(self, x0: int, y0: int, x1: int, y1: int) -> None:
        if not self._dirty:
            self._dirty = True
            self._dirty_min_x = x0
            self._dirty_max_x = x1
            self._dirty_min_y = y0
            self._dirty_max_y = y1
        else:
            if x0 < self._dirty_min_x:
                self._dirty_min_x = x0
            if x1 > self._dirty_max_x:
                self._dirty_max_x = x1
            if y0 < self._dirty_min_y:
                self._dirty_min_y = y0
            if y1 > self._dirty_max_y:
                self._dirty_max_y = y1

    def dirty_region(self) -> tuple[int, int, int, int] | None:
        if self._fully_dirty:
            return (0, 0, self.width, self.height)
        if self._dirty_count == 0:
            return None
        return (
            self._dirty_min_x,
            self._dirty_min_y,
            self._dirty_max_x - self._dirty_min_x + 1,
            self._dirty_max_y - self._dirty_min_y + 1,
        )

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
        if not self._dirty_flags[y][x]:
            self._dirty_flags[y][x] = True
            self._dirty_count += 1
        self._expand_dirty(x, y, x, y)

    def set_many(
        self, cells: list[tuple[int, int, str, Color | None]]
    ) -> None:
        content = self._content
        colors = self._colors
        width = self.width
        height = self.height
        dirty_flags = self._dirty_flags
        min_x = max_x = min_y = max_y = 0
        added = False
        for x, y, char, color in cells:
            if 0 <= x < width and 0 <= y < height:
                content[y][x] = char
                colors[y][x] = color
                if not dirty_flags[y][x]:
                    dirty_flags[y][x] = True
                    self._dirty_count += 1
                if not added:
                    min_x = max_x = x
                    min_y = max_y = y
                    added = True
                else:
                    if x < min_x:
                        min_x = x
                    if x > max_x:
                        max_x = x
                    if y < min_y:
                        min_y = y
                    if y > max_y:
                        max_y = y
        if added:
            self._expand_dirty(min_x, min_y, max_x, max_y)

    def set_many_unchecked(
        self, cells: list[tuple[int, int, str, Color | None]]
    ) -> None:
        content = self._content
        colors = self._colors
        dirty_flags = self._dirty_flags
        min_x = max_x = min_y = max_y = 0
        added = False
        for x, y, char, color in cells:
            content[y][x] = char
            colors[y][x] = color
            if not dirty_flags[y][x]:
                dirty_flags[y][x] = True
                self._dirty_count += 1
            if not added:
                min_x = max_x = x
                min_y = max_y = y
                added = True
            else:
                if x < min_x:
                    min_x = x
                if x > max_x:
                    max_x = x
                if y < min_y:
                    min_y = y
                if y > max_y:
                    max_y = y
        if added:
            self._expand_dirty(min_x, min_y, max_x, max_y)

    def set_text(
        self,
        x: int,
        y: int,
        text: str,
        color: Color | None = None,
    ) -> None:
        if not (0 <= y < self.height):
            msg = (
                f"coordinates ({x}, {y}) out of bounds for grid "
                f"{self.width}x{self.height}"
            )
            raise IndexError(msg)
        width = self.width
        text_len = len(text)
        if x >= width or x + text_len <= 0:
            return
        x_start = max(0, x)
        x_end = min(width, x + text_len)
        sub = text[x_start - x : x_end - x]
        span = x_end - x_start
        self._content[y][x_start:x_end] = list(sub)
        self._colors[y][x_start:x_end] = [color] * span
        dirty_flags = self._dirty_flags
        x_max = x_end - 1
        for col in range(x_start, x_end):
            if not dirty_flags[y][col]:
                dirty_flags[y][col] = True
                self._dirty_count += 1
        self._expand_dirty(x_start, y, x_max, y)

    def blit_rows(
        self,
        x: int,
        y: int,
        chars: list[list[str]],
        colors: list[list[Color | None]] | None = None,
    ) -> None:
        height = len(chars)
        if height == 0:
            return
        width = len(chars[0])
        if width == 0:
            return
        grid_w = self.width
        grid_h = self.height
        if x >= grid_w or x + width <= 0:
            return
        if y >= grid_h or y + height <= 0:
            return

        x_start = max(0, x)
        x_end = min(grid_w, x + width)
        span = x_end - x_start
        col_start = x_start - x
        col_end = x_end - x

        y_start = max(0, y)
        y_end = min(grid_h, y + height)

        content = self._content
        grid_colors = self._colors

        for gy in range(y_start, y_end):
            row_idx = gy - y
            content[gy][x_start:x_end] = chars[row_idx][col_start:col_end]
            if colors is not None and row_idx < len(colors):
                grid_colors[gy][x_start:x_end] = colors[row_idx][
                    col_start:col_end
                ]
            else:
                grid_colors[gy][x_start:x_end] = [None] * span

        x_max = x_end - 1
        y_max = y_end - 1
        dirty_flags = self._dirty_flags
        for gy in range(y_start, y_end):
            for gx in range(x_start, x_end):
                if not dirty_flags[gy][gx]:
                    dirty_flags[gy][gx] = True
                    self._dirty_count += 1
        self._expand_dirty(x_start, y_start, x_max, y_max)

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
        if char == self.filler and color is None:
            clean_chars = self._clean_chars
            clean_colors = self._clean_colors
            for y in range(self.height):
                content[y][:] = clean_chars
                colors[y][:] = clean_colors
        else:
            row_chars = [char] * width
            row_colors = [color] * width
            for y in range(self.height):
                content[y][:] = row_chars
                colors[y][:] = row_colors
        self._fully_dirty = True
        self._dirty = True

    def clear(self) -> None:
        self.fill(self.filler, None)

    @override
    def __repr__(self) -> str:
        return (
            f"Grid(width={self.width}, height={self.height}, "
            f"filler={self.filler!r})"
        )
