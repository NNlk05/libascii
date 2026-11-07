from __future__ import annotations

from collections.abc import Callable
from types import TracebackType

from .color import Color
from .grid import Grid
from .renderers import Renderer, TkRenderer
from .shapes.shape import Shape


class Game:
    def __init__(
        self,
        width: int = 80,
        height: int = 24,
        title: str = "libascii game",
        fg: Color | None = None,
        bg: Color | None = None,
        filler: str = " ",
        fps: int = 60,
        renderer: Renderer | None = None,
    ) -> None:
        if fps <= 0:
            msg = "fps must be positive"
            raise ValueError(msg)

        self.width = width
        self.height = height
        self.title = title

        self.default_bg = bg if bg is not None else Color("black")
        self.default_fg = fg if fg is not None else Color("white")

        self.filler = filler
        self._fps = fps

        self.grid = Grid(width, height, filler)

        self._running = False
        self.started = False

        if renderer is not None:
            self.renderer = renderer
        else:
            self.renderer = TkRenderer(
                width,
                height,
                title,
                self.default_bg,
                self.default_fg,
                fps,
            )

    @property
    def fps(self) -> int:
        return self._fps

    @fps.setter
    def fps(self, value: int) -> None:
        if value <= 0:
            msg = "fps must be positive"
            raise ValueError(msg)
        self._fps = value
        self.renderer.set_fps(value)

    def on_key_down(
        self,
        keybinding: str,
        callback: Callable[[str], None],
    ) -> None:
        self.renderer.on_key_down(keybinding, callback)

    def on_key_up(
        self,
        keybinding: str,
        callback: Callable[[str], None],
    ) -> None:
        self.renderer.on_key_up(keybinding, callback)

    def on_mouse_down(
        self,
        callback: Callable[[tuple[int, int]], None],
    ) -> None:
        self.renderer.on_mouse_down(callback)

    def on_mouse_up(
        self,
        callback: Callable[[tuple[int, int]], None],
    ) -> None:
        self.renderer.on_mouse_up(callback)

    def on_frame(self, callback: Callable[[], None]) -> None:
        self.renderer.on_frame(callback)

    def draw(self, shape: Shape) -> None:
        shape.draw(self.grid)

    def set(
        self,
        x: int,
        y: int,
        char: str = "",
        color: Color | None = None,
    ) -> None:
        self.grid.set(x, y, char, color)

    def get(self, x: int, y: int) -> tuple[str, Color | None]:
        return self.grid.get(x, y)

    def clear(self) -> None:
        self.grid.clear()

    def text(
        self,
        x: int,
        y: int,
        string: str,
        color: Color | None = None,
    ) -> None:
        for offset, char in enumerate(string):
            self.grid.set(x + offset, y, char, color)

    def refresh(self) -> None:
        self.renderer.render(self.grid)

    def start(self) -> None:
        if self.started:
            return
        self.started = True
        self._running = True
        self.renderer.start()

    def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        self.renderer.stop()

    def __enter__(self) -> Game:
        self.start()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self.stop()
