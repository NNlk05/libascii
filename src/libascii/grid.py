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
        "_dirty_cells_list",
        "_dirty_color_rows",
        "_fully_dirty",
        "_dirty",
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
        self._dirty_cells_list: list[tuple[int, int]] = []
        self._dirty_color_rows: set[int] = set()
        self._fully_dirty: bool = False
        self._dirty: bool = False

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
        if self._fully_dirty:
            width = self.width
            height = self.height
            return frozenset(
                (x, y) for x in range(width) for y in range(height)
            )
        dirty_flags = self._dirty_flags
        return frozenset(
            (x, y) for x, y in self._dirty_cells_list if dirty_flags[y][x]
        )

    @property
    def dirty_color_rows(self) -> set[int]:
        return set(self._dirty_color_rows)

    def mark_clean(self) -> None:
        dirty_flags = self._dirty_flags
        for x, y in self._dirty_cells_list:
            dirty_flags[y][x] = False
        self._dirty_cells_list.clear()
        self._dirty_color_rows.clear()
        self._dirty_count = 0
        self._fully_dirty = False
        self._dirty = False

    def mark_all_dirty(self) -> None:
        self._fully_dirty = True
        self._dirty = True
        self._dirty_count = self.width * self.height

    def mark_cells_clean(self, cells: list[tuple[int, int]]) -> None:
        height = self.height
        width = self.width
        dirty_flags = self._dirty_flags
        cleaned = False
        for x, y in cells:
            if 0 <= x < width and 0 <= y < height and dirty_flags[y][x]:
                dirty_flags[y][x] = False
                self._dirty_count -= 1
                cleaned = True
        if cleaned:
            self._dirty_cells_list[:] = [
                (x, y)
                for (x, y) in self._dirty_cells_list
                if dirty_flags[y][x]
            ]
            rows_with_dirty = {y for _, y in self._dirty_cells_list}
            self._dirty_color_rows = {
                row for row in self._dirty_color_rows if row in rows_with_dirty
            }
            if self._dirty_count == 0:
                self._dirty = False
                self._fully_dirty = False

    def _expand_dirty(self, x0: int, y0: int, x1: int, y1: int) -> None:
        self._dirty = True

    def dirty_regions(self) -> list[tuple[int, int, int, int]]:
        if self._fully_dirty:
            return [(0, 0, self.width, self.height)]
        if self._dirty_count == 0:
            return []
        row_x: dict[int, list[int]] = {}
        dirty_flags = self._dirty_flags
        for x, y in self._dirty_cells_list:
            if not dirty_flags[y][x]:
                continue
            entry = row_x.get(y)
            if entry is None:
                row_x[y] = [x, x]
            else:
                if x < entry[0]:
                    entry[0] = x
                if x > entry[1]:
                    entry[1] = x
        if not row_x:
            return []
        regions: list[tuple[int, int, int, int]] = []
        sorted_rows = sorted(row_x)
        start_y = sorted_rows[0]
        end_y = sorted_rows[0]
        min_x, max_x = row_x[start_y]
        for y in sorted_rows[1:]:
            r_min_x, r_max_x = row_x[y]
            if (
                y == end_y + 1
                and r_max_x >= min_x - 1
                and r_min_x <= max_x + 1
            ):
                end_y = y
                if r_min_x < min_x:
                    min_x = r_min_x
                if r_max_x > max_x:
                    max_x = r_max_x
            else:
                regions.append(
                    (
                        min_x,
                        start_y,
                        max_x - min_x + 1,
                        end_y - start_y + 1,
                    )
                )
                start_y = y
                end_y = y
                min_x, max_x = r_min_x, r_max_x
        regions.append(
            (
                min_x,
                start_y,
                max_x - min_x + 1,
                end_y - start_y + 1,
            )
        )
        return regions

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
        if len(char) != 1:
            msg = "char must be a single character"
            raise ValueError(msg)
        if self._content[y][x] == char and self._colors[y][x] == color:
            return
        self._content[y][x] = char
        self._colors[y][x] = color
        self._dirty_color_rows.add(y)
        if not self._dirty_flags[y][x]:
            self._dirty_flags[y][x] = True
            self._dirty_count += 1
            self._dirty_cells_list.append((x, y))
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
                self._dirty_color_rows.add(y)
                if not dirty_flags[y][x]:
                    dirty_flags[y][x] = True
                    self._dirty_count += 1
                    self._dirty_cells_list.append((x, y))
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
        width = self.width
        height = self.height
        for x, y, _, _ in cells:
            if x < 0 or y < 0 or x >= width or y >= height:
                msg = (
                    f"coordinates ({x}, {y}) out of bounds for grid "
                    f"{width}x{height}"
                )
                raise IndexError(msg)
        content = self._content
        colors = self._colors
        dirty_flags = self._dirty_flags
        min_x = max_x = min_y = max_y = 0
        added = False
        for x, y, char, color in cells:
            content[y][x] = char
            colors[y][x] = color
            self._dirty_color_rows.add(y)
            if not dirty_flags[y][x]:
                dirty_flags[y][x] = True
                self._dirty_count += 1
                self._dirty_cells_list.append((x, y))
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
        if not (0 <= x < self.width):
            msg = (
                f"coordinates ({x}, {y}) out of bounds for grid "
                f"{self.width}x{self.height}"
            )
            raise IndexError(msg)
        width = self.width
        text_len = len(text)
        if x + text_len <= 0:
            return
        x_start = max(0, x)
        x_end = min(width, x + text_len)
        sub = text[x_start - x : x_end - x]
        span = x_end - x_start
        self._content[y][x_start:x_end] = list(sub)
        self._colors[y][x_start:x_end] = [color] * span
        self._dirty_color_rows.add(y)
        dirty_flags = self._dirty_flags
        x_max = x_end - 1
        for col in range(x_start, x_end):
            if not dirty_flags[y][col]:
                dirty_flags[y][col] = True
                self._dirty_count += 1
                self._dirty_cells_list.append((col, y))
        if x_start <= x_max:
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
            row_chars = chars[row_idx][col_start:col_end]
            row_chars = (row_chars + [self.filler] * span)[:span]
            content[gy][x_start:x_end] = row_chars
            if colors is not None and row_idx < len(colors):
                row_colors = colors[row_idx][col_start:col_end]
                row_colors = (row_colors + [None] * span)[:span]
                grid_colors[gy][x_start:x_end] = row_colors
            self._dirty_color_rows.add(gy)

        dirty_flags = self._dirty_flags
        for gy in range(y_start, y_end):
            for gx in range(x_start, x_end):
                if not dirty_flags[gy][gx]:
                    dirty_flags[gy][gx] = True
                    self._dirty_count += 1
                    self._dirty_cells_list.append((gx, gy))
        self._expand_dirty(x_start, y_start, x_end - 1, y_end - 1)

    def get(self, x: int, y: int) -> tuple[str, Color | None]:
        self._check_bounds(x, y)
        return self._content[y][x], self._colors[y][x]

    def __getitem__(self, key: tuple[int, int]) -> tuple[str, Color | None]:
        return self.get(*key)

    def __setitem__(
        self,
        key: tuple[int, int],
        value: tuple[int, int, str, Color | None],
    ) -> None:
        x, y = key
        _x, _y, char, color = value
        self.set(_x, _y, char, color)

    def _is_uniform(self, char: str, color: Color | None) -> bool:
        content = self._content
        colors = self._colors
        for y in range(self.height):
            row = content[y]
            row_colors = colors[y]
            for x in range(self.width):
                if row[x] != char or row_colors[x] != color:
                    return False
        return True

    def fill(
        self, char: str = "", color: Color | None = None, force: bool = False
    ) -> None:
        if not force and self._is_uniform(char, color):
            return
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
        dirty_flags = self._dirty_flags
        for row in dirty_flags:
            for i in range(len(row)):
                row[i] = False
        self._dirty_cells_list.clear()
        self._dirty_color_rows.clear()
        self._dirty_count = 0
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
