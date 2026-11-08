from __future__ import annotations

from typing import cast

from .renderers import BindingMixin, Renderer


class ActionMap:
    def __init__(self, renderer: Renderer) -> None:
        self._renderer = renderer
        self._bindings: dict[str, str] = {}
        self._pressed: dict[str, bool] = {}
        self._frame = 0
        self._pressed_frame: dict[str, int] = {}

        cast(BindingMixin, renderer).on_frame(self._on_frame)

    def bind_action(self, name: str, keybinding: str) -> None:
        self._bindings[name] = keybinding
        self._pressed[name] = False
        cast(BindingMixin, self._renderer).on_key_down(
            keybinding, lambda _: self._key_down(name)
        )
        cast(BindingMixin, self._renderer).on_key_up(
            keybinding, lambda _: self._key_up(name)
        )

    def _key_down(self, name: str) -> None:
        self._pressed[name] = True
        self._pressed_frame[name] = self._frame

    def _key_up(self, name: str) -> None:
        self._pressed[name] = False

    def _on_frame(self) -> None:
        self._frame += 1

    def is_pressed(self, name: str) -> bool:
        return self._pressed.get(name, False)

    def was_pressed(self, name: str) -> bool:
        return (
            self._pressed.get(name, False)
            and self._pressed_frame.get(name, -1) == self._frame - 1
        )

    def is_held(self, name: str) -> bool:
        return (
            self._pressed.get(name, False)
            and self._pressed_frame.get(name, -1) < self._frame - 1
        )
