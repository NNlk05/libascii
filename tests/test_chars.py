from typing import Any, cast

from libascii.chars import CharLib, get_char


def test_get_char_main_block() -> None:
    assert get_char("MAIN", "BLOCK") == "█"


def test_get_char_main_circle_filled() -> None:
    assert get_char("MAIN", "CIRCLE_FILLED") == "●"


def test_get_char_pipe_ascii_horizontal() -> None:
    assert get_char("PIPE_ASCII", "HORIZONTAL") == "-"


def test_get_char_pipe_extended_heavy_cross() -> None:
    assert get_char("PIPE_EXTENDED", "HEAVY_CROSS") == "╋"


def test_get_char_pipe_blocks_full_block() -> None:
    assert get_char("PIPE_BLOCKS", "FULL_BLOCK") == "█"


def test_get_char_pipe_extras_x() -> None:
    assert get_char("PIPE_EXTRAS", "X") == "╳"


def test_get_char_dots_middot() -> None:
    assert get_char("DOTS", "MIDDOT") == "·"


def test_get_char_arrows_double_left_right() -> None:
    assert get_char("ARROWS", "DOUBLE_LEFT_RIGHT_ARROW") == "⇔"


def test_get_char_braille_by_index() -> None:
    assert get_char("BRAILLE", cast(Any, 1)) == chr(0x2801)
    assert get_char("BRAILLE", cast(Any, 255)) == chr(0x2800 + 255)


def test_get_char_unknown_category_raises() -> None:
    try:
        get_char("UNKNOWN", "BLOCK")
    except KeyError:
        pass
    else:
        raise AssertionError("expected KeyError for unknown category")


def test_get_char_unknown_name_raises() -> None:
    try:
        get_char("MAIN", "DOES_NOT_EXIST")
    except KeyError:
        pass
    else:
        raise AssertionError("expected KeyError for unknown name")


def test_charlib_is_dict() -> None:
    assert isinstance(CharLib, dict)
    assert "MAIN" in CharLib
    assert "PIPE_ASCII" in CharLib
    assert "BRAILLE" in CharLib
