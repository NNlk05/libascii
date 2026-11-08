from libascii import Color, Sprite
from libascii.grid import Grid


def F(*rows: str) -> list[list[str]]:
    return [list(row) for row in rows]


def test_construction_rejects_empty_frames() -> None:
    import pytest

    with pytest.raises(ValueError):
        Sprite([], 10)


def test_construction_rejects_zero_dim_frame() -> None:
    import pytest

    with pytest.raises(ValueError):
        Sprite([[]], 10)


def test_construction_rejects_mismatched_dims() -> None:
    import pytest

    with pytest.raises(ValueError):
        Sprite([F("ab"), F("c")], 10)


def test_construction_rejects_bad_colors() -> None:
    import pytest

    with pytest.raises(ValueError):
        Sprite([F("ab")], 10, colors=[[[Color("red")]]])


def test_construction_rejects_nonpositive_fps() -> None:
    import pytest

    with pytest.raises(ValueError):
        Sprite([F("a")], 0)
    with pytest.raises(ValueError):
        Sprite([F("a")], -1)


def test_initial_state() -> None:
    sprite = Sprite([F("ab", "cd")], 10)
    assert sprite.current_frame == 0
    assert sprite.is_playing is False
    assert sprite.finished is False


def test_update_advances_frames() -> None:
    sprite = Sprite([F("a"), F("b"), F("c")], 2)
    sprite.play()
    sprite.update(0.5)
    assert sprite.current_frame == 1
    sprite.update(0.5)
    assert sprite.current_frame == 2


def test_update_advances_multiple_frames_large_dt() -> None:
    sprite = Sprite([F("a"), F("b"), F("c")], 2)
    sprite.play()
    sprite.update(1.1)
    assert sprite.current_frame == 2


def test_update_loops() -> None:
    sprite = Sprite([F("a"), F("b")], 2)
    sprite.play()
    sprite.update(1.0)
    assert sprite.current_frame == 0


def test_update_stops_on_last_frame_non_loop() -> None:
    sprite = Sprite([F("a"), F("b")], 2, loop=False)
    sprite.play()
    sprite.update(1.0)
    assert sprite.current_frame == 1
    assert sprite.is_playing is False
    assert sprite.finished is True


def test_negative_dt_clamped() -> None:
    sprite = Sprite([F("a"), F("b")], 2)
    sprite.play()
    sprite.update(-1.0)
    assert sprite.current_frame == 0


def test_zero_dt_noop() -> None:
    sprite = Sprite([F("a"), F("b")], 2)
    sprite.play()
    sprite.update(0.0)
    assert sprite.current_frame == 0


def test_play_restarts_when_finished() -> None:
    sprite = Sprite([F("a"), F("b")], 2, loop=False)
    sprite.play()
    sprite.update(1.0)
    assert sprite.finished is True
    sprite.play()
    assert sprite.current_frame == 0
    assert sprite.finished is False
    assert sprite.is_playing is True


def test_pause_then_play_resumes() -> None:
    sprite = Sprite([F("a"), F("b"), F("c")], 2)
    sprite.play()
    sprite.update(0.5)
    assert sprite.current_frame == 1
    sprite.pause()
    sprite.update(0.5)
    assert sprite.current_frame == 1
    sprite.play()
    sprite.update(0.5)
    assert sprite.current_frame == 2


def test_stop_resets() -> None:
    sprite = Sprite([F("a"), F("b")], 2)
    sprite.play()
    sprite.update(0.5)
    sprite.stop()
    assert sprite.current_frame == 0
    assert sprite.is_playing is False
    assert sprite.finished is False


def test_draw_clipped_to_bounds() -> None:
    grid = Grid(3, 3)
    sprite = Sprite([F("ab", "cd")], 10)
    sprite.draw(grid, 1, 1)
    assert grid.get(1, 1) == ("a", None)
    assert grid.get(2, 1) == ("b", None)
    assert grid.get(1, 2) == ("c", None)
    assert grid.get(2, 2) == ("d", None)
    assert grid.get(0, 0) == (" ", None)


def test_draw_negative_offset_clips() -> None:
    grid = Grid(3, 3)
    sprite = Sprite([F("ab", "cd")], 10)
    sprite.draw(grid, -1, -1)
    assert grid.get(0, 0) == ("d", None)
    assert grid.get(1, 0) == (" ", None)


def test_draw_grid_smaller_than_frame() -> None:
    grid = Grid(2, 2)
    sprite = Sprite([F("abcd", "efgh")], 10)
    sprite.draw(grid, 0, 0)
    assert grid.get(0, 0) == ("a", None)
    assert grid.get(1, 0) == ("b", None)
    assert grid.get(0, 1) == ("e", None)
    assert grid.get(1, 1) == ("f", None)


def test_draw_flip_h_mirrors_positions() -> None:
    grid = Grid(3, 3)
    sprite = Sprite([F("ab", "cd")], 10)
    sprite.flip_h = True
    sprite.draw(grid, 0, 0)
    assert grid.get(0, 0) == ("b", None)
    assert grid.get(1, 0) == ("a", None)
    assert grid.get(0, 1) == ("d", None)
    assert grid.get(1, 1) == ("c", None)


def test_draw_flip_v_mirrors_positions() -> None:
    grid = Grid(3, 3)
    sprite = Sprite([F("ab", "cd")], 10)
    sprite.flip_v = True
    sprite.draw(grid, 0, 0)
    assert grid.get(0, 0) == ("c", None)
    assert grid.get(1, 0) == ("d", None)
    assert grid.get(0, 1) == ("a", None)
    assert grid.get(1, 1) == ("b", None)


def test_draw_with_colors() -> None:
    grid = Grid(2, 2)
    red = Color("red")
    blue = Color("blue")
    sprite = Sprite(
        [F("ab", "cd")],
        10,
        colors=[[[red, blue], [None, red]]],
    )
    sprite.draw(grid, 0, 0)
    assert grid.get(0, 0) == ("a", red)
    assert grid.get(1, 0) == ("b", blue)
    assert grid.get(0, 1) == ("c", None)
    assert grid.get(1, 1) == ("d", red)


def test_draw_sets_dirty_flag() -> None:
    grid = Grid(3, 3)
    sprite = Sprite([F("ab", "cd")], 10)
    assert grid.dirty is False
    sprite.draw(grid, 0, 0)
    assert grid.dirty is True


def test_draw_current_frame_changes() -> None:
    grid = Grid(2, 2)
    sprite = Sprite([F("ab", "cd"), F("xy", "zw")], 10)
    sprite.play()
    sprite.update(0.5)
    sprite.draw(grid, 0, 0)
    assert grid.get(0, 0) == ("x", None)
    assert grid.get(1, 1) == ("w", None)
