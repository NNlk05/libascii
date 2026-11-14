from __future__ import annotations

from .color import Color
from .grid import Grid


class Tilemap:
    def __init__(
        self,
        tile_grid: list[list[int]],
        tileset: dict[int, tuple[str, Color | None]],
    ) -> None:
        self._tile_grid = tile_grid
        self._tileset = tileset

    @property
    def tile_grid(self) -> list[list[int]]:
        return self._tile_grid

    @property
    def tileset(self) -> dict[int, tuple[str, Color | None]]:
        return self._tileset

    def draw(self, grid: Grid, ox: int, oy: int) -> None:
        cells: list[tuple[int, int, str, Color | None]] = []
        for ty, row in enumerate(self._tile_grid):
            grid_y = oy + ty
            if not 0 <= grid_y < grid.height:
                continue
            for tx, tile_id in enumerate(row):
                grid_x = ox + tx
                if not 0 <= grid_x < grid.width:
                    continue
                entry = self.tileset.get(tile_id)
                if entry is None:
                    char = ""
                    color = None
                else:
                    char, color = entry
                cells.append((grid_x, grid_y, char, color))
        grid.set_many_unchecked(cells)
