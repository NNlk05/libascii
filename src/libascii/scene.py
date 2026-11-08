from __future__ import annotations

from abc import ABC, abstractmethod

from .grid import Grid


class Scene(ABC):
    @abstractmethod
    def enter(self) -> None:
        pass

    @abstractmethod
    def exit(self) -> None:
        pass

    @abstractmethod
    def update(self, dt: float) -> None:
        pass

    @abstractmethod
    def draw(self, grid: Grid) -> None:
        pass


class SceneManager:
    def __init__(self) -> None:
        self._stack: list[Scene] = []

    @property
    def current(self) -> Scene | None:
        if not self._stack:
            return None
        return self._stack[-1]

    def push(self, scene: Scene) -> None:
        if self._stack:
            self._stack[-1].exit()
        self._stack.append(scene)
        scene.enter()

    def pop(self) -> Scene:
        if not self._stack:
            msg = "scene stack is empty"
            raise IndexError(msg)
        scene = self._stack.pop()
        scene.exit()
        if self._stack:
            self._stack[-1].enter()
        return scene

    def replace(self, scene: Scene) -> None:
        if self._stack:
            self._stack[-1].exit()
            self._stack.pop()
        self._stack.append(scene)
        scene.enter()

    def update(self, dt: float) -> None:
        if self._stack:
            self._stack[-1].update(dt)

    def draw(self, grid: Grid) -> None:
        if self._stack:
            self._stack[-1].draw(grid)
