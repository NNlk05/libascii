from __future__ import annotations

from .grid import Grid


def rect_overlap(
    r1: tuple[int, int, int, int],
    r2: tuple[int, int, int, int],
) -> bool:
    if len(r1) != 4 or len(r2) != 4:
        msg = "rect must be a 4-tuple of (x, y, width, height)"
        raise ValueError(msg)
    x1, y1, w1, h1 = r1
    x2, y2, w2, h2 = r2
    if w1 < 0 or h1 < 0 or w2 < 0 or h2 < 0:
        msg = "width and height must be non-negative"
        raise ValueError(msg)
    return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)


def point_in_rect(
    px: int,
    py: int,
    rect: tuple[int, int, int, int],
) -> bool:
    if len(rect) != 4:
        msg = "rect must be a 4-tuple of (x, y, width, height)"
        raise ValueError(msg)
    x, y, w, h = rect
    if w < 0 or h < 0:
        msg = "width and height must be non-negative"
        raise ValueError(msg)
    return x <= px < x + w and y <= py < y + h


def grid_cell_overlap(
    shape_or_rect: tuple[int, int, int, int] | object,
    grid_region_rect: tuple[int, int, int, int],
) -> bool:
    if isinstance(shape_or_rect, (tuple, list)):
        if len(shape_or_rect) != 4:
            msg = "rect must be a 4-tuple of (x, y, width, height)"
            raise ValueError(msg)
        shape_rect = (
            int(shape_or_rect[0]),
            int(shape_or_rect[1]),
            int(shape_or_rect[2]),
            int(shape_or_rect[3]),
        )
    else:
        shape_rect = (
            int(getattr(shape_or_rect, "x")),
            int(getattr(shape_or_rect, "y")),
            int(getattr(shape_or_rect, "width")),
            int(getattr(shape_or_rect, "height")),
        )
    return rect_overlap(shape_rect, grid_region_rect)
