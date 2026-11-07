from __future__ import annotations

from collections.abc import Callable

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
    ) -> None:
        self.width = width
        self.height = height
        self.title = title
        self.default_bg = default_bg
        self.default_fg = default_fg
        self._fps = fps

        self.last_grid: Grid | None = None
        self._running = False

        self._key_down_bindings: list[tuple[str, Callable[[str], None]]] = []
        self._key_up_bindings: list[tuple[str, Callable[[str], None]]] = []
        self._mouse_down_bindings: list[Callable[[tuple[int, int]], None]] = []
        self._mouse_up_bindings: list[Callable[[tuple[int, int]], None]] = []
        self._frame_bindings: list[Callable[[], None]] = []

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def render(self, grid: Grid) -> None:
        self.last_grid = grid

    def set_title(self, title: str) -> None:
        self.title = title

    def set_size(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    def set_fps(self, fps: int) -> None:
        if fps <= 0:
            msg = "fps must be positive"
            raise ValueError(msg)
        self._fps = fps

    def on_key_down(
        self, keybinding: str, callback: Callable[[str], None]
    ) -> None:
        self._key_down_bindings.append((keybinding, callback))

    def on_key_up(
        self, keybinding: str, callback: Callable[[str], None]
    ) -> None:
        self._key_up_bindings.append((keybinding, callback))

    def on_mouse_down(
        self, callback: Callable[[tuple[int, int]], None]
    ) -> None:
        self._mouse_down_bindings.append(callback)

    def on_mouse_up(self, callback: Callable[[tuple[int, int]], None]) -> None:
        self._mouse_up_bindings.append(callback)

    def on_frame(self, callback: Callable[[], None]) -> None:
        self._frame_bindings.append(callback)

    def tick(self) -> None:
        if not self._running:
            return
        for callback in self._frame_bindings:
            callback()
