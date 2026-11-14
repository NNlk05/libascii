from __future__ import annotations

import time
from collections.abc import Callable
from types import TracebackType

from .camera import Camera
from .color import Color
from .grid import Grid
from .input import ActionMap
from .renderers import Renderer, TkRenderer
from .shapes.shape import Shape


class Game:
    __slots__ = (
        "width",
        "height",
        "title",
        "default_bg",
        "default_fg",
        "filler",
        "_fps",
        "font_size",
        "grid",
        "_show_debug",
        "_last_mouse_coords",
        "_running",
        "started",
        "renderer",
        "action_map",
        "camera",
    )

    def __init__(
        self,
        width: int = 80,
        height: int = 24,
        title: str = "libascii game",
        fg: Color | None = None,
        bg: Color | None = None,
        filler: str = " ",
        fps: int = 60,
        font_size: int = 10,
        renderer: Renderer | None = None,
        camera: Camera | None = None,
    ) -> None:
        if fps <= 0:
            msg = "fps must be positive"
            raise ValueError(msg)
        if font_size <= 0:
            msg = "font_size must be positive"
            raise ValueError(msg)

        self.width = width
        self.height = height
        self.title = title

        self.default_bg = bg if bg is not None else Color("black")
        self.default_fg = fg if fg is not None else Color("white")

        self.filler = filler
        self._fps = fps
        self.font_size = font_size

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
                font_size,
            )

        self.action_map = ActionMap()

        self.camera = camera

        self.renderer.on_mouse_down(self._capture_mouse_coords)
        self.renderer.on_mouse_up(self._capture_mouse_coords)
        self.renderer.on_frame(self.action_map.tick)

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
        message = (
            f"FPS={self._fps} Grid="
            f"{self.grid.width}x{self.grid.height} Mouse={mouse_str}"
        )
        self.grid.set_text(0, self.height - 1, message)

    def on_frame(self, callback: Callable[[], None]) -> None:
        self.renderer.on_frame(callback)

    def bind_action(self, name: str, keybinding: str) -> None:
        self.action_map.bind_action(name, keybinding)

        def down(_: str) -> None:
            self.action_map.key_down(name)

        def up(_: str) -> None:
            self.action_map.key_up(name)

        self.renderer.on_key_down(keybinding, down)
        self.renderer.on_key_up(keybinding, up)

    def action_is_pressed(self, name: str) -> bool:
        return self.action_map.is_pressed(name)

    def action_was_pressed(self, name: str) -> bool:
        return self.action_map.was_pressed(name)

    def action_is_held(self, name: str) -> bool:
        return self.action_map.is_held(name)

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
        self.grid.set_text(x, y, string, color)

    def refresh(self) -> None:
        grid = self.grid
        if not grid.dirty:
            return
        regions = grid.dirty_regions()
        if not regions:
            return
        for region in regions:
            self.renderer.render(grid, camera=self.camera, region=region)
        grid.mark_clean()
        if self._show_debug:
            self._write_debug_line()
            self.renderer.render(
                grid,
                camera=self.camera,
                region=(0, grid.height - 1, grid.width, 1),
            )
            grid.mark_clean()

    def set_camera(self, camera: Camera | None) -> None:
        self.camera = camera

    def run(self, callback: Callable[[], None]) -> None:
        self.start()
        while self._running:
            callback()
            self.refresh()
            time.sleep(1 / self._fps)
        self.stop()

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
