from __future__ import annotations


class Camera:
    def __init__(
        self,
        viewport_width: int,
        viewport_height: int,
        world_width: int,
        world_height: int,
    ) -> None:
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.world_width = world_width
        self.world_height = world_height
        self._offset_x = 0
        self._offset_y = 0

    @property
    def offset(self) -> tuple[int, int]:
        return (self._offset_x, self._offset_y)

    @property
    def visible_rect(self) -> tuple[int, int, int, int]:
        return (
            self._offset_x,
            self._offset_y,
            self.viewport_width,
            self.viewport_height,
        )

    def set_offset(self, ox: int, oy: int) -> None:
        max_x = max(0, self.world_width - self.viewport_width)
        max_y = max(0, self.world_height - self.viewport_height)
        self._offset_x = min(max(0, ox), max_x)
        self._offset_y = min(max(0, oy), max_y)

    def follow(self, target_x: int, target_y: int) -> None:
        ox = target_x - (self.viewport_width - 1) // 2
        oy = target_y - (self.viewport_height - 1) // 2
        self.set_offset(ox, oy)
