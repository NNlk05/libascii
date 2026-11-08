from pathlib import Path

from typing import Any, cast

from libascii import Color, Sprite


def test_sprite_flip_h_draw() -> None:
    from libascii import Grid

    grid = Grid(4, 2)
    frames = [[["a", "b"], ["c", "d"]]]
    sprite = Sprite(frames, fps=10)
    sprite.flip_h = True
    sprite.draw(grid, 0, 0)
    assert grid.get(0, 0) == ("b", None)
    assert grid.get(1, 0) == ("a", None)
    assert grid.get(0, 1) == ("d", None)
    assert grid.get(1, 1) == ("c", None)


def test_sprite_flip_v_draw() -> None:
    from libascii import Grid

    grid = Grid(2, 4)
    frames = [[["a", "b"], ["c", "d"]]]
    sprite = Sprite(frames, fps=10)
    sprite.flip_v = True
    sprite.draw(grid, 0, 0)
    assert grid.get(0, 0) == ("c", None)
    assert grid.get(1, 0) == ("d", None)
    assert grid.get(0, 1) == ("a", None)
    assert grid.get(1, 1) == ("b", None)


def test_sprite_flip_h_and_v_draw() -> None:
    from libascii import Grid

    grid = Grid(4, 2)
    frames = [[["a", "b"], ["c", "d"]]]
    sprite = Sprite(frames, fps=10)
    sprite.flip_h = True
    sprite.flip_v = True
    sprite.draw(grid, 0, 0)
    assert grid.get(0, 0) == ("d", None)
    assert grid.get(1, 0) == ("c", None)
    assert grid.get(0, 1) == ("b", None)
    assert grid.get(1, 1) == ("a", None)


def test_sprite_update_large_dt_advances_multiple() -> None:
    sprite = Sprite([[["a"]], [["b"]], [["c"]]], fps=2)
    sprite.play()
    sprite.update(1.1)
    assert sprite.current_frame == 2


def test_sprite_update_non_loop_stops_at_last() -> None:
    sprite = Sprite([[["a"]], [["b"]]], fps=2, loop=False)
    sprite.play()
    sprite.update(10.0)
    assert sprite.current_frame == 1
    assert sprite.is_playing is False
    assert sprite.finished is True


def test_sprite_construction_mismatched_frame_heights() -> None:
    try:
        Sprite([[["a"], ["b"]], [["c"]]], fps=10)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for mismatched frames")


def test_sprite_construction_mismatched_frame_widths() -> None:
    try:
        Sprite([[["a", "b"]], [["c"]]], fps=10)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for mismatched frame widths")


def test_sprite_construction_colors_wrong_frame_count() -> None:
    try:
        Sprite(
            [[["a"]], [["b"]]],
            fps=10,
            colors=cast(Any, [[["red"]]]),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for wrong colors count")


def test_sprite_construction_colors_wrong_row_count() -> None:
    try:
        Sprite(
            [[["a", "b"]]],
            fps=10,
            colors=cast(Any, [[["red"], ["blue"]]]),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for wrong colors row count")


def test_sprite_construction_colors_wrong_col_count() -> None:
    try:
        Sprite(
            [[["a", "b"]]],
            fps=10,
            colors=cast(Any, [[["red"]]]),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for wrong colors col count")


def test_sprite_from_xpm_string_basic() -> None:
    data = """2 2 1 1

. white

..
..
"""
    sprite = Sprite.from_xpm_string(data, fps=10)
    assert sprite.current_frame == 0
    assert sprite.frames[0][0][0] == "."
    assert sprite.frames[0][0][1] == "."
    colors = cast(list[list[list[Color | None]]], sprite._colors)
    assert colors[0][0][0] == Color("white")


def test_sprite_from_xpm_string_multiple_frames() -> None:
    data = """2 1 2 2

. white
# black

..
##
"""
    sprite = Sprite.from_xpm_string(data, fps=10, loop=False)
    assert len(sprite.frames) == 2
    assert sprite.frames[0] == [[".", "."]]
    assert sprite.frames[1] == [["#", "#"]]
    colors = cast(list[list[list[Color | None]]], sprite._colors)
    assert colors[0][0][0] == Color("white")
    assert colors[1][0][0] == Color("black")


def test_sprite_from_xpm_string_cpp_2() -> None:
    data = """1 1 1 1 2

XX white

XXXX
"""
    sprite = Sprite.from_xpm_string(data, fps=10)
    assert sprite.frames[0][0][0] == "XX"


def test_sprite_to_xpm_string_basic() -> None:
    frames = [[["a", "b"], ["c", "d"]]]
    sprite = Sprite(frames, fps=10, loop=True)
    output = sprite.to_xpm_string()
    assert "2 2 4 1 1" in output
    assert "a None" in output
    assert "ab" in output
    assert "cd" in output


def test_sprite_to_xpm_string_with_colors() -> None:
    frames = [[["a", "b"], ["c", "d"]]]
    colors = [[[Color("red"), None], [None, Color("blue")]]]
    sprite = Sprite(frames, fps=10, colors=colors)
    output = sprite.to_xpm_string()
    assert "a red" in output
    assert "b None" in output
    assert "c None" in output
    assert "d blue" in output


def test_sprite_to_xpm_string_multiple_frames() -> None:
    frames = [[["a"]], [["b"]]]
    sprite = Sprite(frames, fps=10, loop=False)
    output = sprite.to_xpm_string()
    assert "1 1 2 2 1" in output
    assert output.count("\n\n") >= 1


def test_sprite_from_xpm_string_none_color() -> None:
    data = """1 1 1 1

. None

.
"""
    sprite = Sprite.from_xpm_string(data, fps=10)
    colors = cast(list[list[list[Color | None]]], sprite._colors)
    assert colors[0][0][0] is None


def test_sprite_from_xpm_file(tmp_path: Path) -> None:
    xpm_content = """2 2 1 1

. white

..
..
"""
    xpm_file = tmp_path / "test.xpm"
    xpm_file.write_text(xpm_content)
    sprite = Sprite.from_xpm_file(str(xpm_file), fps=10)
    assert sprite.frames[0][0][0] == "."
    colors = cast(list[list[list[Color | None]]], sprite._colors)
    assert colors[0][0][0] == Color("white")


def test_sprite_play_after_finish_restarts() -> None:
    sprite = Sprite([[["a"]], [["b"]]], fps=2, loop=False)
    sprite.play()
    sprite.update(10.0)
    assert sprite.finished is True
    sprite.play()
    assert sprite.finished is False
    assert sprite.current_frame == 0
    assert sprite.is_playing is True


def test_sprite_draw_with_colors() -> None:
    from libascii import Grid

    grid = Grid(2, 2)
    red = Color("red")
    blue = Color("blue")
    sprite = Sprite(
        [[["a", "b"], ["c", "d"]]],
        fps=10,
        colors=[[[red, blue], [None, red]]],
    )
    sprite.draw(grid, 0, 0)
    assert grid.get(0, 0) == ("a", red)
    assert grid.get(1, 0) == ("b", blue)
    assert grid.get(0, 1) == ("c", None)
    assert grid.get(1, 1) == ("d", red)


def test_sprite_update_negative_dt_clamped() -> None:
    sprite = Sprite([[["a"]], [["b"]]], fps=2)
    sprite.play()
    sprite.update(-5.0)
    assert sprite.current_frame == 0


def test_sprite_update_zero_dt_noop() -> None:
    sprite = Sprite([[["a"]], [["b"]]], fps=2)
    sprite.play()
    sprite.update(0.0)
    assert sprite.current_frame == 0
