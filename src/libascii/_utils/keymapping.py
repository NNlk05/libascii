MODIFIER_MAP = {
    "ctrl": "Control",
    "shift": "Shift",
    "alt": "Alt",
    "meta": "Meta",
}

MODIFIER_ORDER = ("ctrl", "shift", "alt", "meta")

MAX_COMBINATIONS = 64


def _dedupe_combos(
    combos: list[tuple[frozenset[str], str | None]],
) -> list[tuple[frozenset[str], str | None]]:
    seen: set[tuple[frozenset[str], str | None]] = set()
    result: list[tuple[frozenset[str], str | None]] = []
    for combo in combos:
        if combo not in seen:
            seen.add(combo)
            result.append(combo)
    return result


def expand_keybinding(keybinding: str) -> list[tuple[frozenset[str], str]]:
    combinations: list[tuple[frozenset[str], str]] = []
    for pattern in keybinding.split(" or "):
        pattern_combos: list[tuple[frozenset[str], str | None]] = [
            (frozenset(), None)
        ]

        for token in [token.strip() for token in pattern.split("+")]:
            if token.startswith("[") and token.endswith("]"):
                modifier = token[1:-1]
                if modifier not in MODIFIER_MAP:
                    msg = f"Unknown modifier: [{modifier}]"
                    raise ValueError(msg)
                expanded: list[tuple[frozenset[str], str | None]] = []
                for modifiers, key in pattern_combos:
                    expanded.append((modifiers, key))
                    if modifier not in modifiers:
                        expanded.append((modifiers | {modifier}, key))
                pattern_combos = _dedupe_combos(expanded)
            elif token.startswith("{") and token.endswith("}"):
                choices = [choice.strip() for choice in token[1:-1].split(",")]
                expanded: list[tuple[frozenset[str], str | None]] = []
                for modifiers, key in pattern_combos:
                    for choice in choices:
                        expanded.append((modifiers, choice))
                pattern_combos = _dedupe_combos(expanded)
            elif token in MODIFIER_MAP:
                pattern_combos = _dedupe_combos(
                    [
                        (modifiers | {token}, key)
                        for modifiers, key in pattern_combos
                    ]
                )
            else:
                if any(key is not None for _, key in pattern_combos):
                    msg = f"Duplicate key in pattern: {token}"
                    raise ValueError(msg)
                pattern_combos = [
                    (modifiers, token) for modifiers, _ in pattern_combos
                ]
            if len(pattern_combos) > MAX_COMBINATIONS:
                count = len(pattern_combos)
                msg = (
                    f"Keybinding expands to {count} combinations; "
                    f"maximum is {MAX_COMBINATIONS}"
                )
                raise ValueError(msg)

        for modifiers, key in pattern_combos:
            if key is not None:
                combinations.append((modifiers, key))
        if len(combinations) > MAX_COMBINATIONS:
            count = len(combinations)
            msg = (
                f"Keybinding expands to {count} combinations; "
                f"maximum is {MAX_COMBINATIONS}"
            )
            raise ValueError(msg)
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
