from __future__ import annotations

from libascii.color import Color
from libascii.grid import Grid


def wrap(text: str, width: int) -> list[str]:
    if width <= 0:
        return []
    if not text:
        return []
    lines: list[str] = []
    for word in text.split(" "):
        if not word:
            continue
        if not lines:
            lines.append(word)
        elif len(lines[-1]) + 1 + len(word) <= width:
            lines[-1] = lines[-1] + " " + word
        else:
            lines.append(word)
    return lines


def align(line: str, width: int, mode: str = "left") -> str:
    if len(line) >= width:
        return line
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
    lines: list[str],
    color: Color | None = None,
    align_mode: str = "left",
) -> None:
    available_width = max(0, grid.width - x)
    for row, line in enumerate(lines):
        aligned = align(line, available_width, align_mode)
        gy = y + row
        if not 0 <= gy < grid.height:
            continue
        for col, ch in enumerate(aligned):
            gx = x + col
            if 0 <= gx < grid.width:
                grid.set(gx, gy, ch, color)
