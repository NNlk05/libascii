from __future__ import annotations

from .color import Color
from .grid import Grid


class Tilemap:
    def __init__(
        self,
        tile_grid: list[list[int]],
        tileset: dict[int, tuple[str, Color | None]],
    ) -> None:
        self._tile_grid = [list(row) for row in tile_grid]
        self._tileset = dict(tileset)

    @property
    def tile_grid(self) -> list[list[int]]:
        return [list(row) for row in self._tile_grid]

    @property
    def tileset(self) -> dict[int, tuple[str, Color | None]]:
        return dict(self._tileset)

    def draw(self, grid: Grid, ox: int, oy: int) -> None:
        in_bounds_cells: list[tuple[int, int, str, Color | None]] = []
        tileset = self._tileset
        for ty, row in enumerate(self._tile_grid):
            grid_y = oy + ty
            if not 0 <= grid_y < grid.height:
                continue
            for tx, tile_id in enumerate(row):
                grid_x = ox + tx
                if not 0 <= grid_x < grid.width:
                    continue
                try:
                    entry = tileset.get(tile_id)
                except TypeError:
                    entry = None
                if entry is None:
                    continue
                char, color = entry
                in_bounds_cells.append((grid_x, grid_y, char, color))
        grid.set_many_unchecked(in_bounds_cells)
