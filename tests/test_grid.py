from libascii import Color, Grid


def test_init_defaults() -> None:
    grid = Grid(5, 3)
    assert grid.width == 5
    assert grid.height == 3
    assert grid.filler == " "
    assert grid.content == [[" "] * 5 for _ in range(3)]
    assert grid.colors == [[None] * 5 for _ in range(3)]


def test_init_custom_filler() -> None:
    grid = Grid(2, 2, filler=".")
    assert grid.filler == "."
    assert grid.content == [[".", "."], [".", "."]]


def test_set_and_get() -> None:
    grid = Grid(3, 3)
    grid.set(1, 1, "X", Color("red"))
    char, color = grid.get(1, 1)
    assert char == "X"
    assert color == Color("red")


def test_set_out_of_bounds_raises() -> None:
    grid = Grid(3, 3)
    for x, y in [(-1, 0), (0, -1), (3, 0), (0, 3)]:
        try:
            grid.set(x, y, "X")
        except IndexError:
            pass
        else:
            raise AssertionError(f"expected IndexError for ({x}, {y})")


def test_get_out_of_bounds_raises() -> None:
    grid = Grid(3, 3)
    for x, y in [(-1, 0), (0, -1), (3, 0), (0, 3)]:
        try:
            grid.get(x, y)
        except IndexError:
            pass
        else:
            raise AssertionError(f"expected IndexError for ({x}, {y})")


def test_set_many() -> None:
    grid = Grid(3, 3)
    grid.set_many([(0, 0, "a", None), (2, 2, "z", Color("blue"))])
    assert grid.get(0, 0) == ("a", None)
    assert grid.get(2, 2) == ("z", Color("blue"))


def test_set_many_ignores_out_of_bounds() -> None:
    grid = Grid(3, 3)
    grid.set_many([(5, 5, "x", None)])
    assert grid.in_bounds(5, 5) is False
    assert grid.get(0, 0) == (" ", None)


def test_fill() -> None:
    grid = Grid(3, 2)
    grid.fill("#", Color("red"))
    assert all(cell == "#" for row in grid.content for cell in row)
    assert all(cell == Color("red") for row in grid.colors for cell in row)


def test_clear() -> None:
    grid = Grid(3, 2, filler=".")
    grid.fill("#")
    grid.clear()
    assert all(cell == "." for row in grid.content for cell in row)
    assert all(cell is None for row in grid.colors for cell in row)


def test_getitem_setitem() -> None:
    grid = Grid(3, 3)
    grid[1, 1] = ("X", Color("green"))
    assert grid[1, 1] == ("X", Color("green"))


def test_repr() -> None:
    grid = Grid(4, 2, filler=".")
    assert repr(grid) == "Grid(width=4, height=2, filler='.')"


def test_negative_width_rejected() -> None:
    try:
        Grid(-1, 3)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for negative width")


def test_negative_height_rejected() -> None:
    try:
        Grid(3, -1)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for negative height")


def test_zero_width_rejected() -> None:
    try:
        Grid(0, 3)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for zero width")


def test_zero_height_rejected() -> None:
    try:
        Grid(3, 0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for zero height")


def test_in_bounds() -> None:
    grid = Grid(3, 2)
    assert grid.in_bounds(0, 0) is True
    assert grid.in_bounds(2, 1) is True
    assert grid.in_bounds(3, 0) is False
    assert grid.in_bounds(0, 2) is False
    assert grid.in_bounds(-1, 0) is False
    assert grid.in_bounds(0, -1) is False
