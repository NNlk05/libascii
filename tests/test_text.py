from libascii import Color, align, draw_text, wrap
from libascii.grid import Grid

import pytest


def test_wrap_simple() -> None:
    assert wrap("hello world", 11) == ["hello world"]


def test_wrap_breaks_at_spaces() -> None:
    assert wrap("the quick brown fox", 10) == ["the quick", "brown fox"]


def test_wrap_long_word_overflows() -> None:
    assert wrap("supercalifragilistic", 5) == ["supercalifragilistic"]


def test_wrap_multiple_lines() -> None:
    assert wrap("a b c d e f", 3) == ["a b", "c d", "e f"]


def test_wrap_empty_text() -> None:
    assert wrap("", 10) == []


def test_wrap_zero_width_raises() -> None:
    with pytest.raises(ValueError):
        wrap("hello", 0)


def test_wrap_negative_width_raises() -> None:
    with pytest.raises(ValueError):
        wrap("hello", -1)


def test_align_left() -> None:
    assert align("hi", 5) == "hi   "


def test_align_right() -> None:
    assert align("hi", 5, "right") == "   hi"


def test_align_center() -> None:
    assert align("hi", 5, "center") == " hi  "


def test_align_center_odd_padding() -> None:
    assert align("ab", 5, "center") == " ab  "


def test_align_line_wider_than_width_truncated() -> None:
    assert align("hello", 3) == "hel"


def test_align_invalid_mode_raises() -> None:
    try:
        align("hi", 5, "justify")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for invalid align mode")


def test_draw_text_single_line() -> None:
    grid = Grid(5, 5)
    draw_text(grid, 0, 0, ["hello"])
    assert grid.get(0, 0) == ("h", None)
    assert grid.get(4, 0) == ("o", None)


def test_draw_text_multi_line_stacks_vertically() -> None:
    grid = Grid(5, 3)
    draw_text(grid, 0, 0, ["ab", "cd", "ef"])
    assert grid.get(0, 0) == ("a", None)
    assert grid.get(1, 0) == ("b", None)
    assert grid.get(0, 1) == ("c", None)
    assert grid.get(1, 1) == ("d", None)
    assert grid.get(0, 2) == ("e", None)
    assert grid.get(1, 2) == ("f", None)


def test_draw_text_with_color() -> None:
    grid = Grid(3, 3)
    draw_text(grid, 0, 0, ["abc"], color=Color("red"))
    assert grid.get(0, 0) == ("a", Color("red"))
    assert grid.get(1, 0) == ("b", Color("red"))
    assert grid.get(2, 0) == ("c", Color("red"))


def test_draw_text_clips_to_grid_bounds() -> None:
    grid = Grid(3, 3)
    draw_text(grid, 1, 1, ["hello", "world"])
    assert grid.get(1, 1) == ("h", None)
    assert grid.get(2, 1) == ("e", None)
    assert grid.get(1, 2) == ("w", None)
    assert grid.get(2, 2) == ("o", None)


def test_draw_text_negative_x_clips() -> None:
    grid = Grid(3, 3)
    draw_text(grid, -1, 0, ["abc"])
    assert grid.get(0, 0) == ("b", None)
    assert grid.get(1, 0) == ("c", None)


def test_draw_text_out_of_bounds_y_noop() -> None:
    grid = Grid(3, 3)
    draw_text(grid, 0, 5, ["hello"])
    for y in range(3):
        for x in range(3):
            assert grid.get(x, y) == (" ", None)


def test_draw_text_empty_lines() -> None:
    grid = Grid(3, 3)
    draw_text(grid, 0, 0, [])
    for y in range(3):
        for x in range(3):
            assert grid.get(x, y) == (" ", None)


def test_draw_text_align_center() -> None:
    grid = Grid(7, 3)
    draw_text(grid, 0, 0, ["hi"], align_mode="center")
    assert grid.get(2, 0) == ("h", None)
    assert grid.get(3, 0) == ("i", None)


def test_draw_text_align_right() -> None:
    grid = Grid(7, 3)
    draw_text(grid, 0, 0, ["hi"], align_mode="right")
    assert grid.get(5, 0) == ("h", None)
    assert grid.get(6, 0) == ("i", None)


def test_from_libascii_import() -> None:
    from libascii import wrap, align, draw_text

    assert wrap is not None
    assert align is not None
    assert draw_text is not None
