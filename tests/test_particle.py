from libascii import Color, Particle, ParticleSystem
from libascii.grid import Grid


def test_particle_ages_and_dies() -> None:
    p = Particle(0, 0, 0, 0, 1.0, "*", Color("white"))
    assert p.dead is False
    p.update(0.5)
    assert p.dead is False
    assert p.life == 0.5
    p.update(0.5)
    assert p.dead is True
    assert p.life == 0.0


def test_particle_moves_with_velocity() -> None:
    p = Particle(0, 0, 2, 3, 10, "*", Color("white"))
    p.update(1.0)
    assert p.x == 2.0
    assert p.y == 3.0


def test_particle_fade_chars_change_over_life() -> None:
    fade = ["@", "#", "+", "-", "."]
    p = Particle(0, 0, 0, 0, 1.0, "*", Color("white"), fade_chars=fade)
    assert p.char == "*"
    p.update(0.5)
    assert p.char == "+"
    p.update(0.5)
    assert p.dead is True


def test_particle_no_fade_chars_keeps_char() -> None:
    p = Particle(0, 0, 0, 0, 1.0, "*", Color("white"))
    p.update(0.5)
    assert p.char == "*"


def test_particle_position_rounds() -> None:
    p = Particle(0.4, 0.6, 0, 0, 10, "*", Color("white"))
    assert p.position == (0, 1)


def test_particle_system_emit_and_update() -> None:
    ps = ParticleSystem()
    ps.emit(0, 0, life=1.0)
    assert len(ps.particles) == 1
    ps.update(0.5)
    assert len(ps.particles) == 1
    ps.update(0.6)
    assert len(ps.particles) == 0


def test_particle_system_multiple_particles() -> None:
    ps = ParticleSystem()
    ps.emit(0, 0, life=1.0, char="A")
    ps.emit(5, 5, life=2.0, char="B")
    assert len(ps.particles) == 2
    ps.update(1.5)
    assert len(ps.particles) == 1
    assert ps.particles[0].char == "B"


def test_particle_system_draw_clips_to_bounds() -> None:
    grid = Grid(3, 3)
    ps = ParticleSystem()
    ps.emit(-1, -1, life=10, char="X")
    ps.emit(0, 0, life=10, char="A")
    ps.emit(2, 2, life=10, char="B")
    ps.emit(5, 5, life=10, char="Y")
    ps.draw(grid)
    assert grid.get(0, 0)[0] == "A"
    assert grid.get(2, 2)[0] == "B"
    assert grid.get(1, 1)[0] == " "


def test_particle_system_system_empty_after_all_die() -> None:
    ps = ParticleSystem()
    ps.emit(0, 0, life=0.1)
    ps.emit(1, 1, life=0.2)
    ps.update(0.3)
    assert len(ps.particles) == 0


def test_from_libascii_import() -> None:
    from libascii import Particle, ParticleSystem

    assert Particle is not None
    assert ParticleSystem is not None


def test_particle_system_draw_sets_dirty() -> None:
    grid = Grid(3, 3)
    assert grid.dirty is False
    ps = ParticleSystem()
    ps.emit(0, 0, life=10, char="*")
    ps.draw(grid)
    assert grid.dirty is True
