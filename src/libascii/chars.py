from types import MappingProxyType
from typing import Never, override


class _ReadOnlyDict(dict[str, MappingProxyType[str | int, str]]):
    @override
    def __setitem__(self, key: object, value: object) -> Never:
        raise TypeError("CharLib is read-only")

    @override
    def __delitem__(self, key: object) -> Never:
        raise TypeError("CharLib is read-only")

    @override
    def clear(self) -> Never:
        raise TypeError("CharLib is read-only")

    @override
    def pop(self, key: object, default: object = None, /) -> Never:
        raise TypeError("CharLib is read-only")

    @override
    def popitem(self) -> Never:
        raise TypeError("CharLib is read-only")

    @override
    def setdefault(self, key: object, default: object = None, /) -> Never:
        raise TypeError("CharLib is read-only")

    @override
    def update(self, __other: object = None, /, **kwargs: object) -> Never:
        raise TypeError("CharLib is read-only")


_CHARLIB: dict[str, dict[str | int, str]] = {
    "MAIN": {
        "BLANK": " ",
        "LIGHT_SHADE": "░",
        "MEDIUM_SHADE": "▒",
        "DARK_SHADE": "▓",
        "BLOCK": "█",
        "SQUARE_FILLED": "■",
        "SQUARE_OUTLINE": "□",
        "CIRCLE_FILLED": "●",
        "CIRCLE_OUTLINE": "○",
        "DIAMOND_FILLED": "◆",
        "DIAMOND_OUTLINE": "◇",
        "TRIANGLE_UP_FILLED": "▲",
        "TRIANGLE_UP_OUTLINE": "△",
        "TRIANGLE_DOWN_FILLED": "▼",
        "TRIANGLE_DOWN_OUTLINE": "▽",
        "TRIANGLE_LEFT_FILLED": "◀",
        "TRIANGLE_LEFT_OUTLINE": "◁",
        "TRIANGLE_RIGHT_FILLED": "▶",
        "TRIANGLE_RIGHT_OUTLINE": "▷",
    },
    "PIPE_ASCII": {
        "HORIZONTAL": "-",
        "VERTICAL": "|",
        "TOP_LEFT": "/",
        "TOP_RIGHT": "\\",
        "CROSS": "+",
    },
    "PIPE_EXTENDED": {
        "HORIZONTAL": "─",
        "VERTICAL": "│",
        "BOTTOM_LEFT_TURN": "┌",
        "BOTTOM_RIGHT_TURN": "┐",
        "TOP_LEFT_TURN": "└",
        "TOP_RIGHT_TURN": "┘",
        "T_UP": "┴",
        "T_DOWN": "┬",
        "T_LEFT": "┤",
        "T_RIGHT": "├",
        "CROSS": "┼",
        "HEAVY_HORIZONTAL": "━",
        "HEAVY_VERTICAL": "┃",
        "HEAVY_BOTTOM_LEFT_TURN": "┏",
        "HEAVY_BOTTOM_RIGHT_TURN": "┓",
        "HEAVY_TOP_LEFT_TURN": "┗",
        "HEAVY_TOP_RIGHT_TURN": "┛",
        "HEAVY_T_UP": "┻",
        "HEAVY_T_DOWN": "┳",
        "HEAVY_T_LEFT": "┫",
        "HEAVY_T_RIGHT": "┣",
        "HEAVY_CROSS": "╋",
        "DOUBLE_HORIZONTAL": "═",
        "DOUBLE_VERTICAL": "║",
        "DOUBLE_BOTTOM_LEFT_TURN": "╔",
        "DOUBLE_BOTTOM_RIGHT_TURN": "╗",
        "DOUBLE_TOP_LEFT_TURN": "╚",
        "DOUBLE_TOP_RIGHT_TURN": "╝",
        "DOUBLE_T_UP": "╩",
        "DOUBLE_T_DOWN": "╦",
        "DOUBLE_T_LEFT": "╣",
        "DOUBLE_T_RIGHT": "╠",
        "DOUBLE_CROSS": "╬",
        "ROUNDED_BOTTOM_LEFT_TURN": "╭",
        "ROUNDED_BOTTOM_RIGHT_TURN": "╮",
        "ROUNDED_TOP_LEFT_TURN": "╰",
        "ROUNDED_TOP_RIGHT_TURN": "╯",
    },
    "PIPE_BLOCKS": {
        "FULL_BLOCK": "█",
        "LOWER_HALF_BLOCK": "▄",
        "UPPER_HALF_BLOCK": "▀",
        "LEFT_HALF_BLOCK": "▌",
        "RIGHT_HALF_BLOCK": "▐",
        "LOWER_LEFT_QUARTER_BLOCK": "▖",
        "LOWER_RIGHT_QUARTER_BLOCK": "▗",
        "UPPER_LEFT_QUARTER_BLOCK": "▘",
        "UPPER_RIGHT_QUARTER_BLOCK": "▝",
        "LEFT_THREE_QUARTER_BLOCK": "▙",
        "RIGHT_THREE_QUARTER_BLOCK": "▛",
        "LOWER_THREE_QUARTER_BLOCK": "▟",
        "UPPER_THREE_QUARTER_BLOCK": "▜",
    },
    "PIPE_EXTRAS": {
        "X": "╳",
        "HALF_LEFT_HORIZONTAL": "╴",
        "HALF_TOP_VERTICAL": "╵",
        "HALF_RIGHT_HORIZONTAL": "╶",
        "HALF_BOTTOM_VERTICAL": "╷",
        "END_LEFT": "╼",
        "END_TOP": "╽",
        "END_RIGHT": "╾",
        "END_BOTTOM": "╿",
    },
    "DOTS": {
        "ELLIPSE_MIDDLE": "⋯",
        "ELLIPSE_VERTICAL": "⋮",
        "ELLIPSE_DIAGONAL_RIGHT_TO_LEFT": "⋰",
        "ELLIPSE_DIAGONAL_LEFT_TO_RIGHT": "⋱",
        "MIDDOT": "·",
        "BULLET": "•",
    },
    "ARROWS": {
        "UP_ARROW": "↑",
        "DOWN_ARROW": "↓",
        "LEFT_ARROW": "←",
        "RIGHT_ARROW": "→",
        "UP_DOWN_ARROW": "↕",
        "LEFT_RIGHT_ARROW": "↔",
        "NORTH_WEST_ARROW": "↖",
        "NORTH_EAST_ARROW": "↗",
        "SOUTH_EAST_ARROW": "↘",
        "SOUTH_WEST_ARROW": "↙",
        "DOUBLE_UP_ARROW": "⇑",
        "DOUBLE_DOWN_ARROW": "⇓",
        "DOUBLE_LEFT_ARROW": "⇐",
        "DOUBLE_RIGHT_ARROW": "⇒",
        "DOUBLE_LEFT_RIGHT_ARROW": "⇔",
        "DOUBLE_UP_DOWN_ARROW": "⇕",
    },
    "BRAILLE": {i: chr(0x2800 + i) for i in range(1, 256)},
}

CharLib: dict[str, MappingProxyType[str | int, str]] = _ReadOnlyDict(
    {key: MappingProxyType(value) for key, value in _CHARLIB.items()}
)


def get_char(category: str, name: str | int) -> str:
    try:
        category_chars = CharLib[category]
    except KeyError:
        msg = f"category {category!r} not found"
        raise ValueError(msg) from None
    try:
        return category_chars[name]
    except KeyError:
        msg = f"character {name!r} not found in category {category!r}"
        raise ValueError(msg) from None


if __name__ == "__main__":
    for category, chars in CharLib.items():
        print(f"Category: {category}")
        for name, char in chars.items():
            print(f"  {name}: {char}")
        print()
