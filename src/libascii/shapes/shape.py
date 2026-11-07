from abc import ABC, abstractmethod
from libascii.grid import Grid


class Shape(ABC):
    @abstractmethod
    def draw(self, grid: Grid) -> None:
        pass
