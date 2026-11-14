from typing import override

from libascii import Color, Game, Grid
from libascii.camera import Camera
from libascii.renderers import HeadlessRenderer


def _make_renderer() -> HeadlessRenderer:
    return HeadlessRenderer(10, 8, "test", Color("black"), Color("white"), 60)


class CountingRenderer(HeadlessRenderer):
    def __init__(self) -> None:
        super().__init__(10, 8, "test", Color("black"), Color("white"), 60)
        self.render_calls = 0
        self.regions: list[tuple[int, int, int, int] | None] = []

    @override
    def render(
        self,
        grid: Grid,
        camera: Camera | None = None,
        region: tuple[int, int, int, int] | None = None,
    ) -> None:
        self.render_calls += 1
        self.regions.append(region)
        super().render(grid, camera=camera, region=region)


def test_game_initial_state() -> None:
    renderer = _make_renderer()
    game = Game(width=10, height=8, renderer=renderer)
    assert game.width == 10
    assert game.height == 8
    assert game.title == "libascii game"
    assert game.fps == 60
    assert game.show_debug is False
    assert game.started is False


def test_game_show_debug_default_false() -> None:
    renderer = _make_renderer()
    game = Game(width=10, height=8, renderer=renderer)
    assert game.show_debug is False


def test_game_show_debug_toggle() -> None:
    renderer = _make_renderer()
    game = Game(width=10, height=8, renderer=renderer)
    game.show_debug = True
    assert game.show_debug is True
    game.show_debug = False
    assert game.show_debug is False


def test_game_refresh_skips_when_clean() -> None:
    renderer = CountingRenderer()
    game = Game(width=10, height=8, renderer=renderer)
    game.refresh()
    assert renderer.render_calls == 0


def test_game_refresh_renders_when_dirty() -> None:
    renderer = CountingRenderer()
    game = Game(width=10, height=8, renderer=renderer)
    game.set(0, 0, "X")
    game.refresh()
    assert renderer.render_calls == 1


def test_game_refresh_skips_second_call_without_mutation() -> None:
    renderer = CountingRenderer()
    game = Game(width=10, height=8, renderer=renderer)
    game.set(0, 0, "X")
    game.refresh()
    game.refresh()
    assert renderer.render_calls == 1


def test_game_refresh_passes_dirty_region() -> None:
    renderer = CountingRenderer()
    game = Game(width=10, height=8, renderer=renderer)
    game.set(3, 2, "X")
    game.refresh()
    assert renderer.render_calls == 1
    assert renderer.regions[-1] == (3, 2, 1, 1)


def test_game_refresh_includes_debug_line_in_region() -> None:
    renderer = CountingRenderer()
    game = Game(width=10, height=8, renderer=renderer)
    game.show_debug = True
    game.set(0, 0, "X")
    game.refresh()
    assert renderer.render_calls == 1
    region = renderer.regions[-1]
    assert region is not None
    assert region[1] <= 7


def test_game_fps_setter_invalid_raises() -> None:
    renderer = _make_renderer()
    game = Game(width=10, height=8, renderer=renderer)
    try:
        game.fps = 0
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for fps <= 0")


def test_game_fps_setter_valid() -> None:
    renderer = _make_renderer()
    game = Game(width=10, height=8, renderer=renderer)
    game.fps = 30
    assert game.fps == 30


def test_game_bind_action_and_pressed() -> None:
    renderer = _make_renderer()
    game = Game(width=10, height=8, renderer=renderer)
    game.bind_action("jump", "space")
    assert game.action_is_pressed("jump") is False


def test_game_draw_shape() -> None:
    from libascii.shapes import Rectangle

    renderer = _make_renderer()
    game = Game(width=5, height=5, renderer=renderer)
    rect = Rectangle(3, 3, fill="#", border="+")
    game.draw(rect)
    assert game.get(0, 0) == ("+", Color(""))
    assert game.get(1, 1) == ("#", Color(""))


def test_game_set_and_get() -> None:
    renderer = _make_renderer()
    game = Game(width=5, height=5, renderer=renderer)
    game.set(2, 2, "X", Color("red"))
    char, color = game.get(2, 2)
    assert char == "X"
    assert color == Color("red")


def test_game_clear_sets_dirty() -> None:
    renderer = _make_renderer()
    game = Game(width=5, height=5, renderer=renderer)
    game.set(0, 0, "X")
    game.refresh()
    assert game.grid.dirty is False
    game.set(1, 1, "Y")
    game.clear()
    assert game.grid.dirty is True


def test_game_text() -> None:
    renderer = _make_renderer()
    game = Game(width=10, height=5, renderer=renderer)
    game.text(2, 2, "hello", Color("blue"))
    for i, ch in enumerate("hello"):
        char, color = game.get(2 + i, 2)
        assert char == ch
        assert color == Color("blue")


def test_game_context_manager() -> None:
    renderer = _make_renderer()
    with Game(width=5, height=5, renderer=renderer) as game:
        assert game.started is True
        game.set(0, 0, "X")
        game.refresh()
    assert game.started is True
    assert game._running is False


def test_game_grid_dirty_after_set() -> None:
    renderer = _make_renderer()
    game = Game(width=5, height=5, renderer=renderer)
    assert game.grid.dirty is False
    game.set(0, 0, "X")
    assert game.grid.dirty is True
