from __future__ import annotations

from collections.abc import Callable
from typing import override

from ..camera import Camera
from ..color import Color
from ..grid import Grid
from . import Renderer


class HeadlessRenderer(Renderer):
    def __init__(
        self,
        width: int,
        height: int,
        title: str,
        default_bg: Color,
        default_fg: Color,
        fps: int,
        font_size: int = 10,
    ) -> None:
        super().__init__()
        self.width = width
        self.height = height
        self.title = title
        self.default_bg = default_bg
        self.default_fg = default_fg
        self._fps = fps

        self.last_grid: Grid | None = None
        self.last_region: tuple[int, int, int, int] | None = None
        self._running = False

    @override
    def start(self) -> None:
        self._running = True

    @override
    def stop(self) -> None:
        self._running = False

    @override
    def render(
        self,
        grid: Grid,
        camera: Camera | None = None,
        region: tuple[int, int, int, int] | None = None,
    ) -> None:
        self.last_grid = grid
        self.last_region = region

    @override
    def set_title(self, title: str) -> None:
        self.title = title

    @override
    def set_size(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    @override
    def set_fps(self, fps: int) -> None:
        if fps <= 0:
            msg = "fps must be positive"
            raise ValueError(msg)
        self._fps = fps

    def tick(self) -> None:
        if not self._running:
            return
        for callback in self._frame_bindings:
            callback()
