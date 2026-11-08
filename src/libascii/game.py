from __future__ import annotations

from collections.abc import Callable
from types import TracebackType

from .color import Color
from .grid import Grid
from .input import ActionMap
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

        self._show_debug = False
        self._last_mouse_coords: tuple[int, int] | None = None

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

        self.renderer.on_mouse_down(self._capture_mouse_coords)
        self.renderer.on_mouse_up(self._capture_mouse_coords)

        self._action_map = ActionMap(self.renderer)

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

    @property
    def show_debug(self) -> bool:
        return self._show_debug

    @show_debug.setter
    def show_debug(self, value: bool) -> None:
        self._show_debug = bool(value)

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

    def _capture_mouse_coords(self, coord: tuple[int, int]) -> None:
        self._last_mouse_coords = coord

    def _write_debug_line(self) -> None:
        mouse = self._last_mouse_coords
        if mouse is None:
            mouse_str = "None"
        else:
            mouse_str = f"({mouse[0]}, {mouse[1]})"
        self.text(
            0,
            self.height - 1,
            "FPS="
            + str(self._fps)
            + " Grid="
            + str(self.grid.width)
            + "x"
            + str(self.grid.height)
            + " Mouse="
            + mouse_str,
        )

    def on_frame(self, callback: Callable[[], None]) -> None:
        self.renderer.on_frame(callback)

    def bind_action(self, name: str, keybinding: str) -> None:
        self._action_map.bind_action(name, keybinding)

    def action_pressed(self, name: str) -> bool:
        return self._action_map.is_pressed(name)

    def action_was_pressed(self, name: str) -> bool:
        return self._action_map.was_pressed(name)

    def action_is_held(self, name: str) -> bool:
        return self._action_map.is_held(name)

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
        self.grid.set_many(
            [
                (x + offset, y, char, color)
                for offset, char in enumerate(string)
            ]
        )

    def refresh(self) -> None:
        if not self.grid.dirty:
            return
        if self._show_debug:
            self._write_debug_line()
        dirty_cells = self.grid.dirty_cells
        xs = [x for x, _ in dirty_cells]
        ys = [y for _, y in dirty_cells]
        rx = min(xs)
        ry = min(ys)
        rw = max(xs) - rx + 1
        rh = max(ys) - ry + 1
        region = (rx, ry, rw, rh)

        self.renderer.render(self.grid, region=region)
        self.grid.mark_clean()

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
