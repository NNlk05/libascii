from __future__ import annotations

from libascii.color import Color
from libascii.grid import Grid


class Particle:
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
        for particle in self.particles:
            particle.update(dt)
        self.particles = [p for p in self.particles if not p.dead]

    def draw(self, grid: Grid) -> None:
        cells: list[tuple[int, int, str, Color | None]] = []
        for particle in self.particles:
            px, py = particle.position
            if 0 <= px < grid.width and 0 <= py < grid.height:
                cells.append((px, py, particle.char, particle.color))
        grid.set_many_unchecked(cells)
