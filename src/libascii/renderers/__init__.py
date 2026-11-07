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


class BindingMixin:
    """Shared binding-registration boilerplate for renderers."""

    def __init__(self) -> None:
        self._key_down_bindings: list[tuple[str, Callable[[str], None]]] = []
        self._key_up_bindings: list[tuple[str, Callable[[str], None]]] = []
        self._mouse_down_bindings: list[Callable[[tuple[int, int]], None]] = []
        self._mouse_up_bindings: list[Callable[[tuple[int, int]], None]] = []
        self._frame_bindings: list[Callable[[], None]] = []

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


from .headless import HeadlessRenderer  # noqa: E402
from .tk import TkRenderer  # noqa: E402
