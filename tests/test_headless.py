from typing import override

from libascii import Color, Game, Grid
from libascii.camera import Camera
from libascii.renderers import HeadlessRenderer


def _make_renderer() -> HeadlessRenderer:
    return HeadlessRenderer(5, 3, "test", Color("black"), Color("white"), 60)


def test_start_stop() -> None:
    renderer = _make_renderer()
    renderer.start()
    assert renderer._running is True
    renderer.stop()
    assert renderer._running is False


def test_render_stores_last_grid() -> None:
    renderer = _make_renderer()
    grid = Grid(5, 3)
    renderer.render(grid)
    assert renderer.last_grid is grid


def test_set_title() -> None:
    renderer = _make_renderer()
    renderer.set_title("new title")
    assert renderer.title == "new title"


def test_set_size() -> None:
    renderer = _make_renderer()
    renderer.set_size(10, 7)
    assert renderer.width == 10
    assert renderer.height == 7


def test_set_fps() -> None:
    renderer = _make_renderer()
    renderer.set_fps(30)
    assert renderer._fps == 30


def test_set_fps_invalid_raises() -> None:
    renderer = _make_renderer()
    try:
        renderer.set_fps(0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for fps <= 0")


def test_tick_invokes_frame_callbacks() -> None:
    renderer = _make_renderer()
    calls: list[int] = []
    renderer.on_frame(lambda: calls.append(1))
    renderer.start()
    renderer.tick()
    assert calls == [1]


def test_tick_when_not_running_does_not_invoke() -> None:
    renderer = _make_renderer()
    calls: list[int] = []
    renderer.on_frame(lambda: calls.append(1))
    renderer.tick()
    assert calls == []


def test_last_grid_after_game_refresh() -> None:
    renderer = _make_renderer()
    game = Game(width=5, height=3, renderer=renderer)
    game.set(0, 0, "X")
    game.refresh()
    assert renderer.last_grid is game.grid
    char, _ = renderer.last_grid.get(0, 0)
    assert char == "X"


def test_last_grid_after_direct_render() -> None:
    renderer = _make_renderer()
    grid = Grid(5, 3)
    grid.set(2, 1, "Z")
    renderer.render(grid)
    assert renderer.last_grid is grid
    char, _ = renderer.last_grid.get(2, 1)
    assert char == "Z"


def test_refresh_skips_render_when_clean() -> None:
    class CountingRenderer(HeadlessRenderer):
        def __init__(self) -> None:
            super().__init__(5, 3, "test", Color("black"), Color("white"), 60)
            self.render_calls = 0

        @override
        def render(
            self,
            grid: Grid,
            camera: Camera | None = None,
            region: tuple[int, int, int, int] | None = None,
        ) -> None:
            self.render_calls += 1
            super().render(grid, camera=camera, region=region)

    renderer = CountingRenderer()
    game = Game(width=5, height=3, renderer=renderer)
    game.set(0, 0, "X")
    game.refresh()
    assert renderer.render_calls == 1
    game.refresh()
    assert renderer.render_calls == 1

    game.set(1, 1, "Y")
    game.refresh()
    assert renderer.render_calls == 2
