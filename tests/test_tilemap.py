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


def test_tilemap_missing_tile_id_passthrough() -> None:
    tile_grid = [[9]]
    tileset = {0: (" ", None)}
    tm = Tilemap(tile_grid, tileset)
    grid = Grid(1, 1)
    grid.set(0, 0, "#", Color("red"))
    grid.mark_clean()
    tm.draw(grid, 0, 0)
    assert grid.get(0, 0) == ("#", Color("red"))
    assert not grid.dirty


def test_tilemap_tile_grid_and_tileset_copied() -> None:
    tile_grid = [[1, 2], [3, 4]]
    tileset = {1: ("#", None), 2: (" ", None)}
    tm = Tilemap(tile_grid, tileset)

    tile_grid[0][0] = 9
    tileset[1] = ("@", None)

    assert tm.tile_grid == [[1, 2], [3, 4]]
    assert tm.tileset[1] == ("#", None)
    assert tm.tileset[2] == (" ", None)

    returned_grid = tm.tile_grid
    returned_tileset = tm.tileset
    returned_grid[0][0] = 5
    returned_tileset[3] = ("$", None)

    assert tm.tile_grid[0][0] == 1
    assert 3 not in tm.tileset


def test_tilemap_unhashable_tile_id_skipped() -> None:
    tile_grid: list[list[int]] = [[1]]
    tm = Tilemap(tile_grid, {})
    tm._tile_grid[0][0] = []  # type: ignore
    grid = Grid(1, 1)
    grid.set(0, 0, "#", Color("red"))
    grid.mark_clean()
    tm.draw(grid, 0, 0)
    assert grid.get(0, 0) == ("#", Color("red"))
    assert not grid.dirty


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
