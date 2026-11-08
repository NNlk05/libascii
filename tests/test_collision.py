from libascii import (
    grid_cell_overlap,
    point_in_rect,
    rect_overlap,
)
from libascii.shapes import Rectangle


def test_rect_overlap_disjoint() -> None:
    assert rect_overlap((0, 0, 2, 2), (5, 5, 2, 2)) is False
    assert rect_overlap((5, 5, 2, 2), (0, 0, 2, 2)) is False


def test_rect_overlap_touching_counts_as_overlap() -> None:
    assert rect_overlap((0, 0, 2, 2), (2, 0, 2, 2)) is True
    assert rect_overlap((0, 0, 2, 2), (0, 2, 2, 2)) is True
    assert rect_overlap((2, 0, 2, 2), (0, 0, 2, 2)) is True
    assert rect_overlap((0, 2, 2, 2), (0, 0, 2, 2)) is True


def test_rect_overlap_nested() -> None:
    assert rect_overlap((0, 0, 5, 5), (1, 1, 2, 2)) is True
    assert rect_overlap((1, 1, 2, 2), (0, 0, 5, 5)) is True


def test_rect_overlap_identical() -> None:
    assert rect_overlap((3, 3, 4, 4), (3, 3, 4, 4)) is True


def test_rect_overlap_partial() -> None:
    assert rect_overlap((0, 0, 3, 3), (2, 2, 3, 3)) is True
    assert rect_overlap((2, 2, 3, 3), (0, 0, 3, 3)) is True


def test_rect_overlap_zero_width_or_height() -> None:
    assert rect_overlap((0, 0, 0, 5), (0, 0, 2, 2)) is True
    assert rect_overlap((0, 0, 5, 0), (0, 0, 2, 2)) is True


def test_point_in_rect_inside() -> None:
    assert point_in_rect(1, 1, (0, 0, 5, 5)) is True
    assert point_in_rect(0, 0, (0, 0, 5, 5)) is True
    assert point_in_rect(4, 4, (0, 0, 5, 5)) is True


def test_point_in_rect_outside() -> None:
    assert point_in_rect(5, 5, (0, 0, 5, 5)) is False
    assert point_in_rect(-1, 0, (0, 0, 5, 5)) is False
    assert point_in_rect(0, 5, (0, 0, 5, 5)) is False


def test_grid_cell_overlap_rect() -> None:
    assert grid_cell_overlap((0, 0, 3, 3), (2, 2, 2, 2)) is True
    assert grid_cell_overlap((5, 5, 2, 2), (0, 0, 3, 3)) is False
    assert grid_cell_overlap((2, 2, 2, 2), (0, 0, 3, 3)) is True


def test_grid_cell_overlap_shape() -> None:
    rect = Rectangle(4, 4)
    assert grid_cell_overlap(rect, (0, 0, 3, 3)) is True
    assert grid_cell_overlap(rect, (5, 5, 2, 2)) is False
