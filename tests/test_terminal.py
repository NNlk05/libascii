import os
from io import StringIO
from typing import TextIO, cast
from unittest.mock import patch

from libascii import Color, Grid
from libascii.renderers import TerminalRenderer


class FakeStream:
    def __init__(self) -> None:
        self._buffer = StringIO()
        self._isatty = False

    def write(self, text: str) -> int:
        return self._buffer.write(text)

    def isatty(self) -> bool:
        return self._isatty

    def getvalue(self) -> str:
        return self._buffer.getvalue()


def test_terminal_render_plain_text_no_ansi() -> None:
    stream = FakeStream()
    renderer = TerminalRenderer(
        3,
        2,
        "test",
        Color("black"),
        Color("white"),
        60,
        use_color=False,
        stream=cast(TextIO, stream),
    )
    grid = Grid(3, 2)
    grid.set(0, 0, "A", Color("red"))
    grid.set(1, 0, "B", Color("green"))
    grid.set(2, 0, "C", None)
    renderer.render(grid)
    output = stream.getvalue()
    assert "\x1b" not in output
    assert "ABC" in output


def test_terminal_render_truecolor() -> None:
    stream = FakeStream()
    stream._isatty = True
    renderer = TerminalRenderer(
        3,
        1,
        "test",
        Color("black"),
        Color("white"),
        60,
        use_color=True,
        stream=cast(TextIO, stream),
    )
    grid = Grid(3, 1)
    grid.set(0, 0, "A", Color("#FF0000"))
    with patch.dict(os.environ, {"COLORTERM": "truecolor"}):
        renderer.render(grid)
    output = stream.getvalue()
    assert "\x1b[38;2;255;0;0m" in output


def test_terminal_render_xterm256_downsample() -> None:
    stream = FakeStream()
    stream._isatty = False
    renderer = TerminalRenderer(
        3,
        1,
        "test",
        Color("black"),
        Color("white"),
        60,
        use_color=True,
        stream=cast(TextIO, stream),
    )
    grid = Grid(3, 1)
    grid.set(0, 0, "A", Color("#FF0000"))
    renderer.render(grid)
    output = stream.getvalue()
    assert "\x1b[38;5;" in output
    assert "\x1b[38;2;" not in output


def test_terminal_cell_run_grouping() -> None:
    stream = FakeStream()
    renderer = TerminalRenderer(
        5,
        1,
        "test",
        Color("black"),
        Color("white"),
        60,
        use_color=True,
        stream=cast(TextIO, stream),
    )
    grid = Grid(5, 1)
    grid.set(0, 0, "A", Color("red"))
    grid.set(1, 0, "B", Color("red"))
    grid.set(2, 0, "C", Color("blue"))
    grid.set(3, 0, "D", Color("red"))
    grid.set(4, 0, "E", Color("red"))
    renderer.render(grid)
    output = stream.getvalue()
    red_count = output.count("\x1b[38;5;9m")
    assert red_count == 2


def test_terminal_none_color_no_escape() -> None:
    stream = FakeStream()
    renderer = TerminalRenderer(
        3,
        1,
        "test",
        Color("black"),
        Color("white"),
        60,
        use_color=True,
        stream=cast(TextIO, stream),
    )
    grid = Grid(3, 1)
    grid.set(0, 0, "A", Color("red"))
    grid.set(1, 0, "B", None)
    grid.set(2, 0, "C", Color("red"))
    renderer.render(grid)
    output = stream.getvalue()
    assert output.count("\x1b[38;5;9m") == 2


def test_terminal_start_renders_empty_grid() -> None:
    stream = FakeStream()
    renderer = TerminalRenderer(
        3,
        2,
        "test",
        Color("black"),
        Color("white"),
        60,
        use_color=False,
        stream=cast(TextIO, stream),
    )
    renderer.start()
    output = stream.getvalue()
    assert "   \r\n   \r\n" in output


def test_terminal_set_title() -> None:
    renderer = TerminalRenderer(
        3, 2, "old", Color("black"), Color("white"), 60, stream=StringIO()
    )
    renderer.set_title("new")
    assert renderer.title == "new"


def test_terminal_set_size() -> None:
    renderer = TerminalRenderer(
        3, 2, "test", Color("black"), Color("white"), 60, stream=StringIO()
    )
    renderer.set_size(10, 5)
    assert renderer.width == 10
    assert renderer.height == 5


def test_terminal_set_fps_validates_positive() -> None:
    renderer = TerminalRenderer(
        3, 2, "test", Color("black"), Color("white"), 60, stream=StringIO()
    )
    try:
        renderer.set_fps(0)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for fps=0")


def test_terminal_no_tkinter_import() -> None:
    import pathlib

    terminal_path = (
        pathlib.Path(__file__).resolve().parent.parent
        / "src"
        / "libascii"
        / "renderers"
        / "terminal.py"
    )
    source = terminal_path.read_text()
    assert "tkinter" not in source


def test_terminal_binding_mixin_methods() -> None:
    renderer = TerminalRenderer(
        3, 2, "test", Color("black"), Color("white"), 60, stream=StringIO()
    )
    assert hasattr(renderer, "on_key_down")
    assert hasattr(renderer, "on_key_up")
    assert hasattr(renderer, "on_frame")
    assert hasattr(renderer, "on_mouse_down")
    assert hasattr(renderer, "on_mouse_up")


def test_terminal_named_color() -> None:
    stream = FakeStream()
    renderer = TerminalRenderer(
        3,
        1,
        "test",
        Color("black"),
        Color("white"),
        60,
        use_color=True,
        stream=cast(TextIO, stream),
    )
    grid = Grid(3, 1)
    grid.set(0, 0, "A", Color("red"))
    renderer.render(grid)
    output = stream.getvalue()
    assert "\x1b[38;5;9m" in output


def test_terminal_hex_color_truecolor() -> None:
    stream = FakeStream()
    stream._isatty = True
    renderer = TerminalRenderer(
        3,
        1,
        "test",
        Color("black"),
        Color("white"),
        60,
        use_color=True,
        stream=cast(TextIO, stream),
    )
    grid = Grid(3, 1)
    grid.set(0, 0, "A", Color("#123456"))
    with patch.dict(os.environ, {"COLORTERM": "truecolor"}):
        renderer.render(grid)
    output = stream.getvalue()
    assert "\x1b[38;2;18;52;86m" in output


def test_terminal_not_exposed_at_top_level() -> None:
    import libascii

    assert not hasattr(libascii, "TerminalRenderer")
