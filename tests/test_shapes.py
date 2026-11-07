from libascii import Color, Grid
from libascii.shapes import Ellipse, Line, Rectangle, Triangle


def test_rectangle_draw() -> None:
    grid = Grid(5, 5)
    rect = Rectangle(
        3,
        3,
        fill="#",
        border="+",
        fill_color=Color("red"),
        border_color=Color("blue"),
    )
    rect.draw(grid)
    assert grid.content[1][1] == "#"
    assert grid.colors[1][1] == Color("red")
    assert grid.content[0][0] == "+"
    assert grid.content[0][2] == "+"
    assert grid.content[2][0] == "+"
    assert grid.content[2][2] == "+"
    assert grid.colors[0][0] == Color("blue")


def test_rectangle_zero_size_rejected() -> None:
    for width, height in [(0, 3), (3, 0)]:
        try:
            Rectangle(width, height)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {width}x{height}")


def test_ellipse_draw() -> None:
    grid = Grid(5, 5)
    ellipse = Ellipse(5, 5, fill="*", border="+")
    ellipse.draw(grid)
    assert grid.content[2][2] == "*"
    assert grid.content[0][2] == "+"
    assert grid.content[4][2] == "+"


def test_ellipse_zero_size_rejected() -> None:
    for width, height in [(0, 3), (3, 0)]:
        try:
            Ellipse(width, height)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {width}x{height}")


def test_triangle_draw() -> None:
    grid = Grid(5, 5)
    tri = Triangle(5, 3, fill="#", border="+")
    tri.draw(grid)
    assert grid.content[0][2] == "+"
    assert grid.content[1][1] == "+"
    assert grid.content[1][2] == "#"
    assert grid.content[1][3] == "+"
    assert grid.content[2][0] == "+"
    assert grid.content[2][4] == "+"


def test_triangle_zero_size_rejected() -> None:
    for width, height in [(0, 3), (3, 0)]:
        try:
            Triangle(width, height)
        except ValueError:
            pass
        else:
            raise AssertionError(f"expected ValueError for {width}x{height}")


def test_line_draw() -> None:
    grid = Grid(5, 5)
    line = Line(0, 0, 4, 4, char="*")
    line.draw(grid)
    assert grid.content[0][0] == "*"
    assert grid.content[2][2] == "*"
    assert grid.content[4][4] == "*"


def test_line_color() -> None:
    grid = Grid(5, 5)
    line = Line(0, 0, 0, 4, char="*", color=Color("red"))
    line.draw(grid)
    char, color = grid.get(0, 2)
    assert char == "*"
    assert color == Color("red")
