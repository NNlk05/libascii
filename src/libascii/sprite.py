from __future__ import annotations

from .color import Color
from .grid import Grid


def _mirror(
    chars: list[list[str]],
    flip_h: bool,
    flip_v: bool,
) -> list[list[str]]:
    if not flip_h and not flip_v:
        return chars
    result = chars
    if flip_v:
        result = result[::-1]
    if flip_h:
        result = [row[::-1] for row in result]
    return result


class Sprite:
    __slots__ = (
        "frames",
        "_colors",
        "fps",
        "loop",
        "flip_h",
        "flip_v",
        "_frame_duration",
        "_frame_index",
        "_elapsed",
        "_playing",
        "_finished",
        "_cached_chars",
        "_cached_flip_h",
        "_cached_flip_v",
        "_cached_frame_index",
    )

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
        self._cached_chars = None
        self._cached_flip_h = self.flip_h
        self._cached_flip_v = self.flip_v
        self._cached_frame_index = self._frame_index

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
        if (
            self._cached_chars is not None
            and self.flip_h == self._cached_flip_h
            and self.flip_v == self._cached_flip_v
            and self._frame_index == self._cached_frame_index
        ):
            return self._cached_chars
        self._cached_chars = _mirror(
            self.frames[self._frame_index], self.flip_h, self.flip_v
        )
        self._cached_flip_h = self.flip_h
        self._cached_flip_v = self.flip_v
        self._cached_frame_index = self._frame_index
        return self._cached_chars

    def _current_colors(self) -> list[list[Color | None]] | None:
        if self._colors is None:
            return None
        return self._colors[self._frame_index]

    def draw(self, grid: Grid, x: int, y: int) -> None:
        chars = self._current_chars()
        colors = self._current_colors()
        grid.blit_rows(x, y, chars, colors)

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
        if index >= len(lines):
            msg = "xpm header is missing"
            raise ValueError(msg)
        header = lines[index].split()
        index += 1
        if len(header) not in (4, 5):
            msg = f"xpm header must have 4 or 5 fields, got {len(header)}"
            raise ValueError(msg)
        try:
            width = int(header[0])
            height = int(header[1])
            num_colors = int(header[2])
            num_frames = int(header[3])
            cpp = int(header[4]) if len(header) > 4 else 1
        except ValueError:
            msg = "xpm header fields must be integers"
            raise ValueError(msg) from None
        if cpp <= 0:
            msg = "xpm chars-per-pixel must be positive"
            raise ValueError(msg)

        skip_blank()

        color_map: dict[str, Color | None] = {}
        for _ in range(num_colors):
            if index >= len(lines):
                msg = "xpm color section is truncated"
                raise ValueError(msg)
            parts = lines[index].split(maxsplit=1)
            index += 1
            if not parts:
                msg = "xpm color line is empty"
                raise ValueError(msg)
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
                if index >= len(lines):
                    msg = "xpm frame rows are truncated"
                    raise ValueError(msg)
                line = lines[index]
                index += 1
                if len(line) < width * cpp:
                    msg = (
                        f"xpm row is too short: expected {width * cpp} "
                        f"chars, got {len(line)}"
                    )
                    raise ValueError(msg)
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
