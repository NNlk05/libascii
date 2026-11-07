MODIFIER_MAP = {
    "ctrl": "Control",
    "shift": "Shift",
    "alt": "Alt",
    "meta": "Meta",
}

MODIFIER_ORDER = ("ctrl", "shift", "alt", "meta")


def expand_keybinding(keybinding: str) -> list[tuple[frozenset[str], str]]:
    combinations: list[tuple[frozenset[str], str]] = []
    for pattern in keybinding.split(" or "):
        pattern_combos: list[tuple[frozenset[str], str | None]] = [
            (frozenset(), None)
        ]

        for token in [token.strip() for token in pattern.split("+")]:
            if token.startswith("[") and token.endswith("]"):
                modifier = token[1:-1]
                expanded: list[tuple[frozenset[str], str | None]] = []

                for modifiers, key in pattern_combos:
                    expanded.append((modifiers, key))
                    expanded.append((modifiers | {modifier}, key))
                pattern_combos = expanded
            elif token.startswith("{") and token.endswith("}"):
                choices = [choice.strip() for choice in token[1:-1].split(",")]
                expanded = []
                for modifiers, key in pattern_combos:
                    for choice in choices:
                        expanded.append((modifiers | {choice}, key))
                pattern_combos = expanded
            elif token in MODIFIER_MAP:
                pattern_combos = [
                    (modifiers | {token}, key)
                    for modifiers, key in pattern_combos
                ]
            else:
                pattern_combos = [
                    (modifiers, token) for modifiers, _ in pattern_combos
                ]

        for modifiers, key in pattern_combos:
            if key is not None:
                combinations.append((modifiers, key))
    return combinations


def keybinding_to_events(keybinding: str, event_type: str) -> list[str]:
    events: list[str] = []
    for modifiers, key in expand_keybinding(keybinding):
        ordered = [
            MODIFIER_MAP[modifier]
            for modifier in MODIFIER_ORDER
            if modifier in modifiers
        ]
        parts = [*ordered, event_type, key]
        events.append(f"<{'-'.join(parts)}>")
    return events
