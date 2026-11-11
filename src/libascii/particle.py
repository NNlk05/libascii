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
        content = grid._content
        colors = grid._colors
        dirty = grid._dirty
        min_x = grid._dirty_min_x
        max_x = grid._dirty_max_x
        min_y = grid._dirty_min_y
        max_y = grid._dirty_max_y

        for particle in self.particles:
            px = round(particle.x)
            py = round(particle.y)
            if 0 <= px < grid_w and 0 <= py < grid_h:
                content[py][px] = particle.char
                colors[py][px] = particle.color
                if not dirty:
                    dirty = True
                    min_x = max_x = px
                    min_y = max_y = py
                else:
                    if px < min_x:
                        min_x = px
                    elif px > max_x:
                        max_x = px
                    if py < min_y:
                        min_y = py
                    elif py > max_y:
                        max_y = py
        grid._dirty = dirty
        grid._dirty_min_x = min_x
        grid._dirty_max_x = max_x
        grid._dirty_min_y = min_y
        grid._dirty_max_y = max_y
