from __future__ import annotations

import threading


class ActionMap:
    __slots__ = (
        "_bindings",
        "_pressed",
        "_frame",
        "_pressed_frame",
        "_just_pressed",
        "_closed",
        "_lock",
    )

    def __init__(self) -> None:
        self._bindings: dict[str, str] = {}
        self._pressed: dict[str | tuple[str, str], bool] = {}
        self._frame = 0
        self._pressed_frame: dict[str | tuple[str, str], int] = {}
        self._just_pressed: set[str | tuple[str, str]] = set()
        self._closed = False
        self._lock = threading.Lock()

    def bind_action(self, name: str, keybinding: str) -> None:
        with self._lock:
            self._bindings[name] = keybinding
            self._pressed[name] = False

    def unbind_action(self, name: str) -> None:
        with self._lock:
            self._bindings.pop(name, None)
            self._pressed.pop(name, None)
            self._pressed_frame.pop(name, None)
            self._just_pressed.discard(name)

    def get_keybinding(self, name: str) -> str | None:
        with self._lock:
            return self._bindings.get(name)

    def bound_actions(self) -> list[str]:
        with self._lock:
            return list(self._bindings)

    def _state_key(self, name: str, key: str | None) -> str | tuple[str, str]:
        return (name, key) if key is not None else name

    def key_down(self, name: str, key: str | None = None) -> None:
        with self._lock:
            if self._closed:
                return
            if name not in self._bindings:
                return
            state_key = self._state_key(name, key)
            if not self._pressed.get(state_key, False):
                self._pressed[state_key] = True
                self._pressed_frame[state_key] = self._frame
                self._just_pressed.add(state_key)

    def key_up(self, name: str, key: str | None = None) -> None:
        with self._lock:
            if self._closed:
                return
            if name not in self._bindings:
                return
            self._pressed[self._state_key(name, key)] = False

    def tick(self) -> None:
        with self._lock:
            if self._closed:
                return
            self._frame += 1
            self._just_pressed.clear()

    def close(self) -> None:
        with self._lock:
            self._closed = True
            self._bindings.clear()
            self._pressed.clear()
            self._pressed_frame.clear()
            self._just_pressed.clear()

    def reopen(self) -> None:
        with self._lock:
            self._closed = False
            self._bindings.clear()
            self._pressed.clear()
            self._pressed_frame.clear()
            self._just_pressed.clear()
            self._frame = 0

    def is_pressed(self, name: str, key: str | None = None) -> bool:
        with self._lock:
            return self._pressed.get(self._state_key(name, key), False)

    def was_pressed(self, name: str, key: str | None = None) -> bool:
        with self._lock:
            state_key = self._state_key(name, key)
            if state_key in self._just_pressed:
                self._just_pressed.discard(state_key)
                return True
            return (
                self._pressed.get(state_key, False)
                and self._pressed_frame.get(state_key, -1) == self._frame - 1
            )

    def is_held(self, name: str, key: str | None = None) -> bool:
        with self._lock:
            state_key = self._state_key(name, key)
            return (
                self._pressed.get(state_key, False)
                and self._pressed_frame.get(state_key, -1) < self._frame - 1
            )
