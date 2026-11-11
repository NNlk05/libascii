from __future__ import annotations

import tkinter as tk
from collections.abc import Callable
from typing import override

from ..camera import Camera
from ..color import Color
from ..grid import Grid
from .._utils.keymapping import keybinding_to_events
from . import BindingMixin, Renderer


class TkRenderer(Renderer, BindingMixin):
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
        BindingMixin.__init__(self)
        self.width = width
        self.height = height
        self.title = title
        self.default_bg = default_bg
        self.default_fg = default_fg
        self._fps = fps
        self.font_size = font_size

        self.root: tk.Tk | None = None
        self.area: tk.Text | None = None

        self._running = False

        self._tag_configured: set[str] = set()

    @override
    def start(self) -> None:
        root = tk.Tk()
        root.title(self.title)
        root.protocol("WM_DELETE_WINDOW", self.stop)
        self.root = root

        self.area = tk.Text(
            self.root,
            width=self.width,
            height=self.height,
            font=("Courier", self.font_size),
            bg=str(self.default_bg),
            fg=str(self.default_fg),
            padx=0,
            pady=0,
            borderwidth=0,
            highlightthickness=0,
        )
        self.area.pack()
        self._tag_configured = set()

        self.area.bind("<Button-1>", self._prevent_selection)
        self.area.bind("<B1-Motion>", self._prevent_selection)

        for keybinding, callback in self._key_down_bindings:
            for event in keybinding_to_events(keybinding, "KeyPress"):
                self.area.bind(event, self._make_key_handler(callback))

        for keybinding, callback in self._key_up_bindings:
            for event in keybinding_to_events(keybinding, "KeyRelease"):
                self.area.bind(event, self._make_key_handler(callback))

        self.area.bind(
            "<Button-1>", self._make_mouse_handler(self._mouse_down_bindings)
        )
        self.area.bind(
            "<ButtonRelease-1>",
            self._make_mouse_handler(self._mouse_up_bindings),
        )

        self.area.bind("<Key>", lambda event: "break")

        self._running = True
        self.render(self._empty_grid())

        def _tick() -> None:
            if not self._running:
                return
            for callback in self._frame_bindings:
                callback()
            assert self.root is not None
            self.root.after(round(1000 / self._fps), _tick)

        assert self.root is not None
        self.root.after(round(1000 / self._fps), _tick)
        self.root.mainloop()

    @override
    def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        if self.root is not None:
            self.root.quit()

    @override
    def render(
        self,
        grid: Grid,
        camera: Camera | None = None,
        region: tuple[int, int, int, int] | None = None,
    ) -> None:
        if self.area is None:
            return

        if region is None:
            if camera is None:
                content = grid.content
                colors = grid.colors
            else:
                ox, oy = camera.offset
                vw = camera.viewport_width
                vh = camera.viewport_height
                content = [
                    row[ox : ox + vw] for row in grid.content[oy : oy + vh]
                ]
                colors = [
                    row[ox : ox + vw] for row in grid.colors[oy : oy + vh]
                ]

            self.area.delete("1.0", tk.END)

            rows = ["".join(row) for row in content]
            self.area.insert("1.0", "\n".join(rows) + "\n")

            self._apply_colors(colors)
        else:
            self._render_region(grid, region)

    def _apply_colors(
        self,
        colors: list[list[Color | None]],
        start_row: int = 0,
        end_row: int | None = None,
    ) -> None:
        if self.area is None:
            return
        tag_ranges: dict[str, list[tuple[str, str]]] = {}
        if end_row is None:
            end_row = len(colors)
        for y in range(start_row, end_row):
            if y >= len(colors):
                break
            row = colors[y]
            line_prefix = f"{y + 1}."
            x = 0
            row_len = len(row)
            while x < row_len:
                color = row[x]
                if color is None:
                    x += 1
                    continue
                color_str = str(color)
                if not color_str:
                    x += 1
                    continue
                start = x
                x += 1
                while (
                    x < row_len
                    and row[x] is not None
                    and str(row[x]) == color_str
                ):
                    x += 1
                end = x
                tag_ranges.setdefault(color_str, []).append(
                    (f"{line_prefix}{start}", f"{line_prefix}{end}")
                )

        for color_str, ranges in tag_ranges.items():
            if color_str not in self._tag_configured:
                self.area.tag_config(color_str, foreground=color_str)
                self._tag_configured.add(color_str)
            for start_idx, end_idx in ranges:
                self.area.tag_add(color_str, start_idx, end_idx)

    def _render_region(
        self,
        grid: Grid,
        region: tuple[int, int, int, int],
    ) -> None:
        if self.area is None:
            return
        rx, ry, rw, rh = region
        bottom = min(ry + rh, grid.height)
        right = min(rx + rw, grid.width)

        for y in range(ry, bottom):
            line = f"{y + 1}."
            row_slice = grid.content[y][rx:right]
            self.area.delete(f"{line}{rx}", f"{line}{right}")
            self.area.insert(f"{line}{rx}", "".join(row_slice))

        for tag in self.area.tag_names():
            self.area.tag_remove(tag, f"{ry + 1}.0", f"{bottom}.end")

        colors = grid.colors
        self._apply_colors(colors, start_row=ry, end_row=bottom)

    @override
    def set_title(self, title: str) -> None:
        self.title = title
        if self.root is not None:
            self.root.title(title)

    @override
    def set_size(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        if self.area is not None:
            self.area.config(width=width, height=height)

    @override
    def set_fps(self, fps: int) -> None:
        if fps <= 0:
            msg = "fps must be positive"
            raise ValueError(msg)
        self._fps = fps

    @staticmethod
    def _prevent_selection(event: tk.Event[tk.Misc]) -> str:
        return "break"

    def _make_key_handler(
        self, callback: Callable[[str], None]
    ) -> Callable[[tk.Event[tk.Misc]], str]:
        def handler(event: tk.Event[tk.Misc]) -> str:
            callback(event.keysym)
            return "break"

        return handler

    def _make_mouse_handler(
        self, bindings: list[Callable[[tuple[int, int]], None]]
    ) -> Callable[[tk.Event[tk.Misc]], None]:
        def handler(event: tk.Event[tk.Misc]) -> None:
            if self.area is None:
                return
            line, col = self.area.index(f"@{event.x},{event.y}").split(".")
            coord = (int(col), int(line) - 1)
            for binding in bindings:
                binding(coord)

        return handler

    def _empty_grid(self) -> Grid:
        from ..grid import Grid

        return Grid(self.width, self.height)
