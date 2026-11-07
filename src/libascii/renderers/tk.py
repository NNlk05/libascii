from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

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
    ) -> None:
        BindingMixin.__init__(self)
        self.width = width
        self.height = height
        self.title = title
        self.default_bg = default_bg
        self.default_fg = default_fg
        self._fps = fps

        self.root: tk.Tk | None = None
        self.area: tk.Text | None = None

        self._running = False

    def start(self) -> None:
        root = tk.Tk()
        root.title(self.title)
        root.protocol("WM_DELETE_WINDOW", self.stop)
        self.root = root

        self.area = tk.Text(
            self.root,
            width=self.width,
            height=self.height,
            font=("Courier", 10),
            bg=str(self.default_bg),
            fg=str(self.default_fg),
            padx=0,
            pady=0,
            borderwidth=0,
            highlightthickness=0,
        )
        self.area.pack()

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

        self._running = True
        self.render(self._empty_grid())

        def _tick() -> None:
            if not self._running:
                return
            for callback in self._frame_bindings:
                callback()
            self.root.after(round(1000 / self._fps), _tick)

        self.root.after(round(1000 / self._fps), _tick)
        self.root.mainloop()

    def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        if self.root is not None:
            self.root.quit()

    def render(self, grid: Grid) -> None:
        if self.area is None:
            return
        self.area.delete("1.0", tk.END)

        for y, row in enumerate(grid.content):
            self.area.insert(f"{y + 1}.0", "".join(row) + "\n")
        if grid.colors:
            unique_colors = {
                color
                for row in grid.colors
                for color in row
                if color is not None
            }
            for color in unique_colors:
                color_str = str(color)
                if color_str:
                    self.area.tag_config(color_str, foreground=color_str)
        for y, row in enumerate(grid.colors):
            for x, color in enumerate(row):
                if color is not None:
                    color_str = str(color)
                    if color_str:
                        self.area.tag_add(
                            color_str, f"{y + 1}.{x}", f"{y + 1}.{x + 1}"
                        )

    def set_title(self, title: str) -> None:
        self.title = title
        if self.root is not None:
            self.root.title(title)

    def set_size(self, width: int, height: int) -> None:
        self.width = width
        self.height = height
        if self.area is not None:
            self.area.config(width=width, height=height)

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
