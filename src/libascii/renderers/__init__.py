from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable

from ..grid import Grid


class Renderer(ABC):
    @abstractmethod
    def start(self) -> None:
        pass

    @abstractmethod
    def stop(self) -> None:
        pass

    @abstractmethod
    def render(self, grid: Grid) -> None:
        pass

    @abstractmethod
    def set_title(self, title: str) -> None:
        pass

    @abstractmethod
    def set_size(self, width: int, height: int) -> None:
        pass

    @abstractmethod
    def set_fps(self, fps: int) -> None:
        pass

    @abstractmethod
    def on_key_down(
        self, keybinding: str, callback: Callable[[str], None]
    ) -> None:
        pass

    @abstractmethod
    def on_key_up(
        self, keybinding: str, callback: Callable[[str], None]
    ) -> None:
        pass

    @abstractmethod
    def on_mouse_down(
        self, callback: Callable[[tuple[int, int]], None]
    ) -> None:
        pass

    @abstractmethod
    def on_mouse_up(self, callback: Callable[[tuple[int, int]], None]) -> None:
        pass

    @abstractmethod
    def on_frame(self, callback: Callable[[], None]) -> None:
        pass
