from __future__ import annotations


class ActionMap:
    __slots__ = (
        "_bindings",
        "_pressed",
        "_frame",
        "_pressed_frame",
        "_closed",
    )

    def __init__(self) -> None:
        self._bindings: dict[str, str] = {}
        self._pressed: dict[str, bool] = {}
        self._frame = 0
        self._pressed_frame: dict[str, int] = {}
        self._closed = False

    def bind_action(self, name: str, keybinding: str) -> None:
        self._bindings[name] = keybinding
        self._pressed[name] = False

    def unbind_action(self, name: str) -> None:
        self._bindings.pop(name, None)
        self._pressed.pop(name, None)
        self._pressed_frame.pop(name, None)

    def get_keybinding(self, name: str) -> str | None:
        return self._bindings.get(name)

    def bound_actions(self) -> list[str]:
        return list(self._bindings)

    def key_down(self, name: str) -> None:
        if self._closed:
            return
        self._pressed[name] = True
        self._pressed_frame[name] = self._frame

    def key_up(self, name: str) -> None:
        if self._closed:
            return
        self._pressed[name] = False

    def tick(self) -> None:
        if self._closed:
            return
        self._frame += 1

    def close(self) -> None:
        self._closed = True
        self._bindings.clear()
        self._pressed.clear()
        self._pressed_frame.clear()

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
