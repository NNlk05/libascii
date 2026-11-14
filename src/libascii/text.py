from __future__ import annotations

from .color import Color
from .grid import Grid


def wrap(text: str, width: int) -> list[str]:
    if width <= 0:
        msg = f"width must be positive, got {width!r}"
        raise ValueError(msg)
    if not text:
        return []
    lines: list[str] = []
    current: list[str] = []
    current_len = 0
    for word in text.split():
        if not current:
            current = [word]
            current_len = len(word)
        elif current_len + 1 + len(word) <= width:
            current.append(word)
            current_len += 1 + len(word)
        else:
            lines.append(" ".join(current))
            current = [word]
            current_len = len(word)
    if current:
        lines.append(" ".join(current))
    return lines


def align(line: str, width: int, mode: str = "left") -> str:
    if len(line) >= width:
        return line[:width]
    padding = width - len(line)
    if mode == "left":
        return line + " " * padding
    if mode == "right":
        return " " * padding + line
    if mode == "center":
        left = padding // 2
        right = padding - left
        return " " * left + line + " " * right
    msg = f"unknown align mode: {mode!r}"
    raise ValueError(msg)


def draw_text(
    grid: Grid,
    x: int,
    y: int,
    lines: str | list[str],
    color: Color | None = None,
    align_mode: str = "left",
) -> None:
    if isinstance(lines, str):
        lines = lines.split("\n")
    available_width = max(0, grid.width - x)
    cells: list[tuple[int, int, str, Color | None]] = []
    for row, line in enumerate(lines):
        aligned = align(line, available_width, align_mode)
        gy = y + row
        if not 0 <= gy < grid.height:
            continue
        for col, ch in enumerate(aligned):
            gx = x + col
            if 0 <= gx < grid.width:
                cells.append((gx, gy, ch, color))
    grid.set_many_unchecked(cells)
