from libascii.input import ActionMap


def test_initial_state() -> None:
    am = ActionMap()
    am.bind_action("jump", "space")
    assert am.is_pressed("jump") is False
    assert am.was_pressed("jump") is False
    assert am.is_held("jump") is False


def test_key_down_sets_pressed() -> None:
    am = ActionMap()
    am.bind_action("jump", "space")
    am.key_down("jump")
    assert am.is_pressed("jump") is True


def test_key_up_clears_pressed() -> None:
    am = ActionMap()
    am.bind_action("jump", "space")
    am.key_down("jump")
    am.key_up("jump")
    assert am.is_pressed("jump") is False


def test_was_pressed_one_frame() -> None:
    am = ActionMap()
    am.bind_action("jump", "space")
    am.key_down("jump")
    am.tick()
    assert am.was_pressed("jump") is True
    am.tick()
    assert am.was_pressed("jump") is False


def test_is_held_persists() -> None:
    am = ActionMap()
    am.bind_action("jump", "space")
    am.key_down("jump")
    am.tick()
    assert am.is_held("jump") is False
    am.tick()
    assert am.is_held("jump") is True


def test_unknown_action() -> None:
    am = ActionMap()
    assert am.is_pressed("nonexistent") is False
    assert am.was_pressed("nonexistent") is False
    assert am.is_held("nonexistent") is False


def test_multiple_actions_independent() -> None:
    am = ActionMap()
    am.bind_action("jump", "space")
    am.bind_action("shoot", "ctrl")
    am.key_down("jump")
    assert am.is_pressed("jump") is True
    assert am.is_pressed("shoot") is False
    am.key_down("shoot")
    assert am.is_pressed("jump") is True
    assert am.is_pressed("shoot") is True
    am.key_up("jump")
    assert am.is_pressed("jump") is False
    assert am.is_pressed("shoot") is True


def test_release_clears_was_pressed() -> None:
    am = ActionMap()
    am.bind_action("jump", "space")
    am.key_down("jump")
    am.tick()
    assert am.was_pressed("jump") is True
    am.key_up("jump")
    am.tick()
    assert am.was_pressed("jump") is False
    assert am.is_pressed("jump") is False
