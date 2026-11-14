from __future__ import annotations

import tkinter as tk
from collections.abc import Callable, Sequence
from typing import override

from ..camera import Camera
from ..color import Color
from ..grid import Grid
from .._utils.keymapping import keybinding_to_events
from . import Renderer


class TkRenderer(Renderer):
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
        self.font_size = font_size

        self.root: tk.Tk | None = None
        self.area: tk.Text | None = None

        self._running = False

        self._tag_configured: set[str] = set()

        self._row_cache: list[str] = []
        self._color_cache: list[list[Color | None]] = []
        self._str_cache: dict[str | None, str] = {}

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
        self._row_cache = []
        self._color_cache = []
        self._str_cache = {}

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
                rows = ["".join(row) for row in content]
                wiped_rows: set[int] = set()
                if len(self._row_cache) != len(rows):
                    self.area.delete("1.0", tk.END)
                    self.area.insert("1.0", "\n".join(rows) + "\n")
                    self._row_cache = list(rows)
                    wiped_rows = set(range(len(rows)))
                else:
                    for y, row in enumerate(rows):
                        if self._row_cache[y] != row:
                            line = f"{y + 1}."
                            self.area.delete(f"{line}0", f"{line}end")
                            self.area.insert(f"{line}0", row)
                            self._row_cache[y] = row
                            wiped_rows.add(y)
                self._apply_colors(colors, wiped_rows=wiped_rows)
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
                self._apply_colors(colors, wiped_rows=set(range(len(colors))))
        else:
            self._render_region(grid, region)

    def _color_str(self, color: Color | None) -> str:
        if color is None:
            return ""
        key = color.value
        if key not in self._str_cache:
            self._str_cache[key] = str(color)
        return self._str_cache[key]

    def _apply_colors(
        self,
        colors: Sequence[Sequence[Color | None]],
        start_row: int = 0,
        end_row: int | None = None,
        wiped_rows: set[int] | None = None,
    ) -> None:
        if self.area is None:
            return
        if end_row is None:
            end_row = len(colors)
        shadow = self._color_cache
        use_shadow = (
            len(colors) == self.height
            and bool(colors)
            and len(colors[0]) == self.width
        )
        if use_shadow and (
            len(shadow) != self.height
            or any(len(row) != self.width for row in shadow)
        ):
            shadow = [[None] * self.width for _ in range(self.height)]
            self._color_cache = shadow
        tag_ranges: dict[str, list[tuple[str, str]]] = {}
        for y in range(start_row, end_row):
            if y >= len(colors):
                break
            row = colors[y]
            line_prefix = f"{y + 1}."
            shadow_row = shadow[y] if use_shadow else None
            row_wiped = wiped_rows is not None and y in wiped_rows
            x = 0
            row_len = len(row)
            while x < row_len:
                color = row[x]
                color_str = self._color_str(color)
                if not color_str:
                    if shadow_row is not None:
                        old = shadow_row[x]
                        if old is not None:
                            old_str = self._color_str(old)
                            if old_str:
                                self.area.tag_remove(
                                    old_str,
                                    f"{line_prefix}{x}",
                                    f"{line_prefix}{x + 1}",
                                )
                        shadow_row[x] = color
                    x += 1
                    continue
                changed = (
                    shadow_row is None or row_wiped or shadow_row[x] != color
                )
                start = x
                x += 1
                while x < row_len:
                    next_color = row[x]
                    next_str = self._color_str(next_color)
                    if next_str != color_str:
                        break
                    next_changed = (
                        shadow_row is None
                        or row_wiped
                        or shadow_row[x] != next_color
                    )
                    if next_changed != changed:
                        break
                    x += 1
                end = x
                if changed:
                    tag_ranges.setdefault(color_str, []).append(
                        (f"{line_prefix}{start}", f"{line_prefix}{end}")
                    )
                    if shadow_row is not None and not row_wiped:
                        for xx in range(start, end):
                            old = shadow_row[xx]
                            if old is not None and old != color:
                                old_str = self._color_str(old)
                                if old_str:
                                    self.area.tag_remove(
                                        old_str,
                                        f"{line_prefix}{xx}",
                                        f"{line_prefix}{xx + 1}",
                                    )
                if shadow_row is not None:
                    for xx in range(start, end):
                        shadow_row[xx] = row[xx]
                x = end
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
        content = grid.content
        colors = grid.colors

        wiped_rows: set[int] = set()
        for y in range(ry, bottom):
            line = f"{y + 1}."
            row_slice = content[y][rx:right]
            row_str = "".join(row_slice)
            full_row = "".join(content[y])
            if y < len(self._row_cache) and self._row_cache[y] == full_row:
                continue
            self.area.delete(f"{line}{rx}", f"{line}{right}")
            self.area.insert(f"{line}{rx}", row_str)
            while len(self._row_cache) <= y:
                self._row_cache.append("")
            self._row_cache[y] = full_row
            wiped_rows.add(y)

        self._apply_colors(
            colors, start_row=ry, end_row=bottom, wiped_rows=wiped_rows
        )

    @override
    def set_title(self, title: str) -> None:
        self.title = title
        if self.root is not None:
            self.root.title(title)

    @override
    def set_size(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        self._row_cache = []
        self._color_cache = []
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
