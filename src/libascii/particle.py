from __future__ import annotations

from .color import Color
from .grid import Grid


class Particle:
    __slots__ = (
        "x",
        "y",
        "vx",
        "vy",
        "life",
        "max_life",
        "char",
        "color",
        "fade_chars",
        "dead",
    )

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        life: float,
        char: str,
        color: Color | None,
        fade_chars: list[str] | None = None,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.char = char
        self.color = color
        self.fade_chars = fade_chars or []
        self.dead = False

    def update(self, dt: float) -> None:
        if self.dead:
            return
        self.life -= dt
        self.x += self.vx * dt
        self.y += self.vy * dt
        if self.life <= 0:
            self.dead = True
            self.life = 0
        else:
            self._update_char()

    def _update_char(self) -> None:
        if not self.fade_chars:
            return
        fraction = 1.0 - self.life / self.max_life
        index = int(fraction * (len(self.fade_chars) - 1))
        if index < 0:
            index = 0
        elif index >= len(self.fade_chars):
            index = len(self.fade_chars) - 1
        self.char = self.fade_chars[index]

    @property
    def position(self) -> tuple[int, int]:
        return (round(self.x), round(self.y))


class ParticleSystem:
    __slots__ = ("particles",)

    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def emit(
        self,
        x: float,
        y: float,
        vx: float = 0.0,
        vy: float = 0.0,
        life: float = 1.0,
        char: str = "*",
        color: Color | None = None,
        fade_chars: list[str] | None = None,
    ) -> None:
        self.particles.append(
            Particle(x, y, vx, vy, life, char, color, fade_chars)
        )

    def update(self, dt: float) -> None:
        has_dead = False
        for particle in self.particles:
            particle.update(dt)
            if particle.dead:
                has_dead = True
        if has_dead:
            self.particles = [p for p in self.particles if not p.dead]

    def draw(self, grid: Grid) -> None:
        grid_w = grid.width
        grid_h = grid.height
        cells = []
        for particle in self.particles:
            px = round(particle.x)
            py = round(particle.y)
            if 0 <= px < grid_w and 0 <= py < grid_h:
                char, color = grid.get(px, py)
                if char == particle.char and color == particle.color:
                    continue
                cells.append((px, py, particle.char, particle.color))
        if cells:
            grid.set_many_unchecked(cells)
