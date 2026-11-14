from libascii._utils.keymapping import expand_keybinding, keybinding_to_events


def test_expand_keybinding_single_key() -> None:
    result = expand_keybinding("space")
    assert result == [(frozenset(), "space")]


def test_expand_keybinding_single_modifier() -> None:
    result = expand_keybinding("ctrl+space")
    assert result == [(frozenset({"ctrl"}), "space")]


def test_expand_keybinding_multiple_modifiers() -> None:
    result = expand_keybinding("ctrl+shift+space")
    assert result == [(frozenset({"ctrl", "shift"}), "space")]


def test_expand_keybinding_modifier_order_independent() -> None:
    result_a = expand_keybinding("ctrl+shift+space")
    result_b = expand_keybinding("shift+ctrl+space")
    assert result_a == result_b


def test_expand_keybinding_alternatives() -> None:
    result = expand_keybinding("space or return")
    assert (frozenset(), "space") in result
    assert (frozenset(), "return") in result
    assert len(result) == 2


def test_expand_keybinding_alternatives_with_modifiers() -> None:
    result = expand_keybinding("ctrl+space or shift+return")
    assert (frozenset({"ctrl"}), "space") in result
    assert (frozenset({"shift"}), "return") in result


def test_expand_keybinding_choice_group() -> None:
    result = expand_keybinding("{a,b,c}")
    assert result == [
        (frozenset(), "a"),
        (frozenset(), "b"),
        (frozenset(), "c"),
    ]


def test_expand_keybinding_modifier_and_choice() -> None:
    result = expand_keybinding("ctrl+{x,y,z}")
    assert result == [
        (frozenset({"ctrl"}), "x"),
        (frozenset({"ctrl"}), "y"),
        (frozenset({"ctrl"}), "z"),
    ]


def test_expand_keybinding_empty_key() -> None:
    result = expand_keybinding("{a,b}")
    assert result == [(frozenset(), "a"), (frozenset(), "b")]


def test_expand_keybinding_unknown_modifier() -> None:
    try:
        expand_keybinding("[foo]+space")
    except ValueError:
        return
    raise AssertionError("expected ValueError for unknown modifier")


def test_keybinding_to_events_simple() -> None:
    events = keybinding_to_events("space", "KeyPress")
    assert "<KeyPress-space>" in events


def test_keybinding_to_events_with_modifiers() -> None:
    events = keybinding_to_events("ctrl+shift+space", "KeyPress")
    assert "<Control-Shift-KeyPress-space>" in events


def test_keybinding_to_events_key_release() -> None:
    events = keybinding_to_events("space", "KeyRelease")
    assert "<KeyRelease-space>" in events


def test_keybinding_to_events_multiple_alternatives() -> None:
    events = keybinding_to_events("space or return", "KeyPress")
    assert "<KeyPress-space>" in events
    assert "<KeyPress-return>" in events
    assert len(events) == 2
