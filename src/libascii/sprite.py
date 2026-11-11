from __future__ import annotations

from libascii.color import Color
from libascii.grid import Grid


def _mirror(
    chars: list[list[str]],
    flip_h: bool,
    flip_v: bool,
) -> list[list[str]]:
    result = [list(row) for row in chars]
    if flip_h:
        result = [list(reversed(row)) for row in result]
    if flip_v:
        result = list(reversed(result))
    return result


class Sprite:
    def __init__(
        self,
        frames: list[list[list[str]]],
        fps: int,
        loop: bool = True,
        colors: list[list[list[Color | None]]] | None = None,
    ) -> None:
        if not frames:
            msg = "frames must not be empty"
            raise ValueError(msg)
        height = len(frames[0])
        width = len(frames[0][0]) if height > 0 else 0
        if width <= 0 or height <= 0:
            msg = "frames must not be empty"
            raise ValueError(msg)
        for frame in frames:
            if len(frame) != height:
                msg = "all frames must have the same dimensions"
                raise ValueError(msg)
            for row in frame:
                if len(row) != width:
                    msg = "all frames must have the same dimensions"
                    raise ValueError(msg)
        if colors is not None:
            if len(colors) != len(frames):
                msg = "colors must match frames"
                raise ValueError(msg)
            for frame_colors, frame in zip(colors, frames):
                if len(frame_colors) != len(frame):
                    msg = "colors must match frames"
                    raise ValueError(msg)
                for color_row, char_row in zip(frame_colors, frame):
                    if len(color_row) != len(char_row):
                        msg = "colors must match frames"
                        raise ValueError(msg)
        if fps <= 0:
            msg = "fps must be positive"
            raise ValueError(msg)

        self.frames = frames
        self._colors = colors
        self.fps = fps
        self.loop = loop
        self.flip_h = False
        self.flip_v = False
        self._frame_duration = 1.0 / fps
        self._frame_index = 0
        self._elapsed = 0.0
        self._playing = False
        self._finished = False

    @property
    def current_frame(self) -> int:
        return self._frame_index

    @property
    def is_playing(self) -> bool:
        return self._playing

    @property
    def finished(self) -> bool:
        return self._finished

    def play(self) -> None:
        if self._finished:
            self._frame_index = 0
            self._elapsed = 0.0
            self._finished = False
        self._playing = True

    def pause(self) -> None:
        self._playing = False

    def stop(self) -> None:
        self._playing = False
        self._frame_index = 0
        self._elapsed = 0.0
        self._finished = False

    def update(self, dt: float) -> None:
        if not self._playing:
            return
        if dt < 0:
            dt = 0.0
        self._elapsed += dt
        while self._elapsed >= self._frame_duration:
            self._elapsed -= self._frame_duration
            self._frame_index += 1
            if self._frame_index >= len(self.frames):
                if self.loop:
                    self._frame_index = 0
                else:
                    self._frame_index = len(self.frames) - 1
                    self._playing = False
                    self._finished = True
                    break

    def _current_chars(self) -> list[list[str]]:
        return _mirror(
            self.frames[self._frame_index], self.flip_h, self.flip_v
        )

    def _current_colors(self) -> list[list[Color | None]] | None:
        if self._colors is None:
            return None
        return self._colors[self._frame_index]

    def draw(self, grid: Grid, x: int, y: int) -> None:
        chars = self._current_chars()
        colors = self._current_colors()
        height = len(chars)
        width = len(chars[0]) if height > 0 else 0
        cells: list[tuple[int, int, str, Color | None]] = []
        for row in range(height):
            grid_y = y + row
            if not 0 <= grid_y < grid.height:
                continue
            color_row = None if colors is None else colors[row]
            for col in range(width):
                grid_x = x + col
                if not 0 <= grid_x < grid.width:
                    continue
                color = None if color_row is None else color_row[col]
                cells.append((grid_x, grid_y, chars[row][col], color))
        grid.set_many_unchecked(cells)

    @staticmethod
    def from_xpm_string(
        data: str,
        fps: int = 10,
        loop: bool = True,
    ) -> Sprite:
        lines = [line.rstrip("\r") for line in data.split("\n")]
        index = 0

        def skip_blank() -> None:
            nonlocal index
            while index < len(lines) and lines[index].strip() == "":
                index += 1

        skip_blank()
        header = lines[index].split()
        index += 1
        width = int(header[0])
        height = int(header[1])
        num_colors = int(header[2])
        num_frames = int(header[3])
        cpp = int(header[4]) if len(header) > 4 else 1

        skip_blank()

        color_map: dict[str, Color | None] = {}
        for _ in range(num_colors):
            parts = lines[index].split(maxsplit=1)
            index += 1
            char_key = parts[0]
            color_val = parts[1].strip() if len(parts) > 1 else "None"
            color_map[char_key] = (
                None if color_val == "None" else Color(color_val)
            )

        skip_blank()

        frames: list[list[list[str]]] = []
        frame_colors: list[list[list[Color | None]]] = []
        for _ in range(num_frames):
            grid_chars: list[list[str]] = []
            grid_colors: list[list[Color | None]] = []
            for _ in range(height):
                line = lines[index]
                index += 1
                row_chars: list[str] = []
                row_colors: list[Color | None] = []
                for cell_x in range(width):
                    start = cell_x * cpp
                    cell_str = line[start : start + cpp]
                    row_chars.append(cell_str)
                    row_colors.append(color_map.get(cell_str, None))
                grid_chars.append(row_chars)
                grid_colors.append(row_colors)
            frames.append(grid_chars)
            frame_colors.append(grid_colors)
            skip_blank()

        return Sprite(frames, fps=fps, loop=loop, colors=frame_colors)

    @staticmethod
    def from_xpm_file(
        path: str,
        fps: int = 10,
        loop: bool = True,
    ) -> Sprite:
        with open(path) as handle:
            data = handle.read()
        return Sprite.from_xpm_string(data, fps=fps, loop=loop)

    def to_xpm_string(self) -> str:
        if not self.frames:
            msg = "sprite has no frames"
            raise ValueError(msg)
        height = len(self.frames[0])
        width = len(self.frames[0][0]) if height > 0 else 0
        num_frames = len(self.frames)
        cpp = 1

        color_map: dict[str, Color | None] = {}
        for frame_idx, frame in enumerate(self.frames):
            frame_colors = (
                self._colors[frame_idx] if self._colors is not None else None
            )
            for row_idx, row in enumerate(frame):
                for col_idx, char in enumerate(row):
                    color: Color | None = None
                    if frame_colors is not None:
                        color = frame_colors[row_idx][col_idx]
                    color_map[char] = color

        num_colors = len(color_map)

        lines: list[str] = []
        lines.append(f"{width} {height} {num_colors} {num_frames} {cpp}")
        lines.append("")

        for char, color in color_map.items():
            color_str = "None" if color is None else str(color)
            lines.append(f"{char} {color_str}")

        lines.append("")

        for frame_idx, frame in enumerate(self.frames):
            for row in frame:
                lines.append("".join(row))
            if frame_idx < num_frames - 1:
                lines.append("")

        return "\n".join(lines)
