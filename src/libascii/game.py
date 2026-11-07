from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from .color import Color
from .grid import Grid
from .shapes.shape import Shape
from ._utils.keymapping import keybinding_to_events


class Game:
    @staticmethod
    def _prevent_selection(event: tk.Event[tk.Misc]) -> str:
        return "break"

    def __init__(
        self,
        width: int = 80,
        height: int = 24,
        title: str = "asciilib game",
        fg: Color | None = None,
        bg: Color | None = None,
        filler: str = " ",
        fps: int = 60,
    ) -> None:
        self.width = width
        self.height = height

        self.default_bg = bg if bg is not None else Color("black")
        self.default_fg = fg if fg is not None else Color("white")

        self.filler = filler
        self.title = title

        self.grid = Grid(width, height, filler)

        self._key_down_bindings: list[tuple[str, Callable]] = []
        self._key_up_bindings: list[tuple[str, Callable]] = []

        self._mouse_down_bindings: list[Callable[[tuple[int, int]], None]] = []
        self._mouse_up_bindings: list[Callable[[tuple[int, int]], None]] = []

        self._frame_bindings: list[Callable[[], None]] = []
        self._fps = fps

        self._running = False
        self.root: tk.Tk | None = None
        self.area: tk.Text | None = None

    def on_key_down(
        self,
        keybinding: str,
        callback: Callable[[tk.Event[tk.Misc]], None],
    ) -> None:
        self._key_down_bindings.append((keybinding, callback))

    def on_key_up(
        self,
        keybinding: str,
        callback: Callable[[tk.Event[tk.Misc]], None],
    ) -> None:
        self._key_up_bindings.append((keybinding, callback))

    def on_mouse_down(
        self,
        callback: Callable[[tuple[int, int]], None],
    ) -> None:
        self._mouse_down_bindings.append(callback)

    def on_mouse_up(
        self,
        callback: Callable[[tuple[int, int]], None],
    ) -> None:
        self._mouse_up_bindings.append(callback)

    def on_frame(self, callback: Callable[[], None]) -> None:
        self._frame_bindings.append(callback)

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
        self._render()

    @property
    def fps(self) -> int:
        return self._fps

    @fps.setter
    def fps(self, value: int) -> None:
        self._fps = value

    def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        if self.root is not None:
            self.root.quit()

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
                self.area.bind(event, callback)

        for keybinding, callback in self._key_up_bindings:
            for event in keybinding_to_events(keybinding, "KeyRelease"):
                self.area.bind(event, callback)

        def _make_mouse_handler(
            bindings: list[Callable[[tuple[int, int]], None]],
        ) -> Callable[[tk.Event[tk.Misc]], None]:
            def handler(event: tk.Event[tk.Misc]) -> None:
                line, col = self.area.index(f"@{event.x},{event.y}").split(".")
                coord = (int(col), int(line) - 1)
                for binding in bindings:
                    binding(coord)

            return handler

        down_handler = _make_mouse_handler(self._mouse_down_bindings)
        up_handler = _make_mouse_handler(self._mouse_up_bindings)
        self.area.bind("<Button-1>", down_handler)
        self.area.bind("<ButtonRelease-1>", up_handler)

        self._running = True
        self._render()

        def _tick() -> None:
            if not self._running:
                return
            for callback in self._frame_bindings:
                callback()
            self.root.after(round(1000 / self._fps), _tick)

        self.root.after(round(1000 / self._fps), _tick)
        self.root.mainloop()

    def _render(self) -> None:
        self.area.delete("1.0", tk.END)

        for y, row in enumerate(self.grid.content):
            self.area.insert(f"{y + 1}.0", "".join(row) + "\n")
        for y, row in enumerate(self.grid.colors):
            for x, color in enumerate(row):
                if color is not None:
                    color_str = str(color)

                    if color_str:
                        self.area.tag_add(
                            color_str, f"{y + 1}.{x}", f"{y + 1}.{x + 1}"
                        )
                        self.area.tag_config(color_str, foreground=color_str)


if __name__ == "__main__":
    Game().start()
