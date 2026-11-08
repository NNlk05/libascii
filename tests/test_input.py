from libascii import Color
from libascii.input import ActionMap
from libascii.renderers import HeadlessRenderer

_BG = Color("black")
_FG = Color("white")


def _make_renderer() -> HeadlessRenderer:
    renderer = HeadlessRenderer(10, 10, "t", _BG, _FG, 60)
    renderer.start()
    return renderer


def test_initial_state() -> None:
    renderer = _make_renderer()
    am = ActionMap(renderer)
    am.bind_action("jump", "space")
    assert am.is_pressed("jump") is False
    assert am.was_pressed("jump") is False
    assert am.is_held("jump") is False


def test_key_down_sets_pressed() -> None:
    renderer = _make_renderer()
    am = ActionMap(renderer)
    am.bind_action("jump", "space")
    am._key_down("jump")
    assert am.is_pressed("jump") is True


def test_key_up_clears_pressed() -> None:
    renderer = _make_renderer()
    am = ActionMap(renderer)
    am.bind_action("jump", "space")
    am._key_down("jump")
    am._key_up("jump")
    assert am.is_pressed("jump") is False


def test_was_pressed_one_frame() -> None:
    renderer = _make_renderer()
    am = ActionMap(renderer)
    am.bind_action("jump", "space")
    am._key_down("jump")
    renderer.tick()
    assert am.was_pressed("jump") is True
    renderer.tick()
    assert am.was_pressed("jump") is False


def test_is_held_persists() -> None:
    renderer = _make_renderer()
    am = ActionMap(renderer)
    am.bind_action("jump", "space")
    am._key_down("jump")
    renderer.tick()
    assert am.is_held("jump") is False
    renderer.tick()
    assert am.is_held("jump") is True


def test_unknown_action() -> None:
    renderer = _make_renderer()
    am = ActionMap(renderer)
    assert am.is_pressed("nonexistent") is False
    assert am.was_pressed("nonexistent") is False
    assert am.is_held("nonexistent") is False


def test_multiple_actions_independent() -> None:
    renderer = _make_renderer()
    am = ActionMap(renderer)
    am.bind_action("jump", "space")
    am.bind_action("shoot", "ctrl")
    am._key_down("jump")
    assert am.is_pressed("jump") is True
    assert am.is_pressed("shoot") is False
    am._key_down("shoot")
    assert am.is_pressed("jump") is True
    assert am.is_pressed("shoot") is True
    am._key_up("jump")
    assert am.is_pressed("jump") is False
    assert am.is_pressed("shoot") is True


def test_release_clears_was_pressed() -> None:
    renderer = _make_renderer()
    am = ActionMap(renderer)
    am.bind_action("jump", "space")
    am._key_down("jump")
    renderer.tick()
    assert am.was_pressed("jump") is True
    am._key_up("jump")
    renderer.tick()
    assert am.was_pressed("jump") is False
    assert am.is_pressed("jump") is False
