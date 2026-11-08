from libascii import Color, Grid, Tilemap


def _make_tilemap() -> Tilemap:
    tile_grid = [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 2, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]
    tileset = {
        0: (" ", None),
        1: ("#", Color("gray")),
        2: ("@", Color("red")),
    }
    return Tilemap(tile_grid, tileset)


def test_tilemap_draw_full() -> None:
    grid = Grid(5, 5)
    tm = _make_tilemap()
    tm.draw(grid, 0, 0)

    assert grid.get(0, 0) == ("#", Color("gray"))
    assert grid.get(1, 1) == (" ", None)
    assert grid.get(2, 2) == ("@", Color("red"))
    assert grid.get(4, 4) == ("#", Color("gray"))


def test_tilemap_missing_tile_id_blank() -> None:
    tile_grid = [[9]]
    tileset = {0: (" ", None)}
    tm = Tilemap(tile_grid, tileset)
    grid = Grid(1, 1)
    tm.draw(grid, 0, 0)
    assert grid.get(0, 0) == ("", None)


def test_tilemap_draw_with_offset() -> None:
    grid = Grid(7, 7)
    tm = _make_tilemap()
    tm.draw(grid, 2, 1)

    assert grid.get(2, 1) == ("#", Color("gray"))
    assert grid.get(6, 5) == ("#", Color("gray"))
    assert grid.get(4, 3) == ("@", Color("red"))


def test_tilemap_draw_clips_to_grid_bounds() -> None:
    grid = Grid(3, 3)
    tm = _make_tilemap()
    tm.draw(grid, 3, 3)

    assert grid.get(0, 0) == (" ", None)


def test_tilemap_draw_negative_offset_clips() -> None:
    grid = Grid(3, 3)
    tm = _make_tilemap()
    tm.draw(grid, -2, -2)

    assert grid.get(0, 0) == ("@", Color("red"))


def test_tilemap_draw_fully_out_of_bounds() -> None:
    grid = Grid(3, 3)
    tm = _make_tilemap()
    tm.draw(grid, -10, -10)
    assert grid.get(0, 0) == (" ", None)


def test_tilemap_empty_tile_grid() -> None:
    tm = Tilemap([], {})
    grid = Grid(3, 3)
    tm.draw(grid, 0, 0)
    assert grid.get(0, 0) == (" ", None)
