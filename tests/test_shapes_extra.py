from libascii import Color, Grid
from libascii.shapes import Ellipse, Line, Rectangle, Triangle


def test_shape_is_abstract() -> None:
    from libascii.shapes.shape import Shape

    import abc

    assert hasattr(Shape.draw, "__isabstractmethod__")
    assert Shape.draw.__isabstractmethod__ is True


def test_rectangle_zero_height() -> None:
    try:
        Rectangle(5, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for zero height")


def test_rectangle_zero_width() -> None:
    try:
        Rectangle(0, 5)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for zero width")


def test_ellipse_zero_height() -> None:
    try:
        Ellipse(5, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for zero height")


def test_ellipse_zero_width() -> None:
    try:
        Ellipse(0, 5)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for zero width")


def test_triangle_zero_height() -> None:
    try:
        Triangle(5, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for zero height")


def test_triangle_zero_width() -> None:
    try:
        Triangle(0, 5)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for zero width")


def test_line_draw_vertical() -> None:
    grid = Grid(5, 5)
    line = Line(2, 0, 2, 4, char="|")
    line.draw(grid)
    for y in range(5):
        assert grid.get(2, y)[0] == "|"


def test_line_draw_horizontal() -> None:
    grid = Grid(5, 5)
    line = Line(0, 2, 4, 2, char="-")
    line.draw(grid)
    for x in range(5):
        assert grid.get(x, 2)[0] == "-"


def test_line_draw_single_point() -> None:
    grid = Grid(5, 5)
    line = Line(2, 2, 2, 2, char="*")
    line.draw(grid)
    assert grid.get(2, 2)[0] == "*"


def test_rectangle_border_only_no_fill() -> None:
    grid = Grid(5, 5)
    rect = Rectangle(3, 3, fill="", border="#", border_color=Color("blue"))
    rect.draw(grid)
    assert grid.get(1, 1)[0] == " "
    assert grid.get(0, 0)[0] == "#"
    assert grid.get(0, 0)[1] == Color("blue")


def test_rectangle_individual_borders() -> None:
    grid = Grid(3, 3)
    rect = Rectangle(
        3,
        3,
        fill=".",
        border="+",
        border_top="T",
        border_bottom="B",
        border_left="L",
        border_right="R",
    )
    rect.draw(grid)
    assert grid.get(0, 0)[0] == "T"
    assert grid.get(1, 0)[0] == "T"
    assert grid.get(2, 0)[0] == "T"
    assert grid.get(0, 2)[0] == "B"
    assert grid.get(1, 2)[0] == "B"
    assert grid.get(2, 2)[0] == "B"
    assert grid.get(0, 1)[0] == "L"
    assert grid.get(2, 1)[0] == "R"
    assert grid.get(1, 1)[0] == "."


def test_triangle_border_bottom() -> None:
    grid = Grid(5, 3)
    tri = Triangle(
        5,
        3,
        fill=".",
        border="#",
        border_bottom="B",
    )
    tri.draw(grid)
    for x in range(5):
        char, _ = grid.get(x, 2)
        assert char == "B"


def test_triangle_border_left_right() -> None:
    grid = Grid(5, 3)
    tri = Triangle(
        5,
        3,
        fill=".",
        border="#",
        border_left="L",
        border_right="R",
    )
    tri.draw(grid)
    char_top, _ = grid.get(2, 0)
    assert char_top in ("L", "R", "#")


def test_rectangle_fill_color_none() -> None:
    grid = Grid(3, 3)
    rect = Rectangle(3, 3, fill=".", fill_color=None)
    rect.draw(grid)
    assert grid.get(1, 1)[1] is None


def test_line_color_none() -> None:
    grid = Grid(5, 5)
    line = Line(0, 0, 4, 4, char="*", color=None)
    line.draw(grid)
    assert str(grid.get(0, 0)[1]) == ""
