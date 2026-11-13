from __future__ import annotations

import importlib
import os
import sys
import threading
import time
import atexit
from typing import Any, TextIO, override
from ..camera import Camera
from ..color import Color
from ..grid import Grid
from . import Renderer

try:
    colorama = importlib.import_module("colorama")
except ImportError:
    colorama = None


_NAMED_COLORS: dict[str, tuple[int, int, int]] = {
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "yellow": (255, 255, 0),
    "blue": (0, 0, 255),
    "magenta": (255, 0, 255),
    "cyan": (0, 255, 255),
    "white": (255, 255, 255),
    "gray": (128, 128, 128),
    "grey": (128, 128, 128),
    "bright_black": (128, 128, 128),
    "bright_red": (255, 0, 0),
    "bright_green": (0, 255, 0),
    "bright_yellow": (255, 255, 0),
    "bright_blue": (0, 0, 255),
    "bright_magenta": (255, 0, 255),
    "bright_cyan": (0, 255, 255),
    "bright_white": (255, 255, 255),
}


def _color_to_rgb(value: str | None) -> tuple[int, int, int] | None:
    if value is None or value == "":
        return None
    if value in _COLOR_RGB_CACHE:
        return _COLOR_RGB_CACHE[value]
    if value.startswith("#"):
        hex_str = value[1:]
        if len(hex_str) == 6:
            try:
                result = (
                    int(hex_str[0:2], 16),
                    int(hex_str[2:4], 16),
                    int(hex_str[4:6], 16),
                )
            except ValueError:
                result = None
        else:
            result = None
    else:
        result = _NAMED_COLORS.get(value.lower())
    _COLOR_RGB_CACHE[value] = result
    return result


def _build_xterm256_palette() -> list[tuple[int, int, int]]:
    palette: list[tuple[int, int, int]] = [
        (0, 0, 0),
        (128, 0, 0),
        (0, 128, 0),
        (128, 128, 0),
        (0, 0, 128),
        (128, 0, 128),
        (0, 128, 128),
        (192, 192, 192),
        (128, 128, 128),
        (255, 0, 0),
        (0, 255, 0),
        (255, 255, 0),
        (0, 0, 255),
        (255, 0, 255),
        (0, 255, 255),
        (255, 255, 255),
    ]
    for r in range(6):
        for g in range(6):
            for b in range(6):
                palette.append(
                    (
                        0 if r == 0 else 95 + 40 * r,
                        0 if g == 0 else 95 + 40 * g,
                        0 if b == 0 else 95 + 40 * b,
                    )
                )
    for i in range(24):
        gray = 8 + 10 * i
        palette.append((gray, gray, gray))
    return palette


_XTERM256_PALETTE = _build_xterm256_palette()

_COLOR_RGB_CACHE: dict[str, tuple[int, int, int] | None] = {}
_XTERM256_CACHE: dict[tuple[int, int, int], int] = {}
_ESCAPE_CACHE: dict[tuple[Color | str, str], str] = {}


def _nearest_xterm256(r: int, g: int, b: int) -> int:
    key = (r, g, b)
    if key in _XTERM256_CACHE:
        return _XTERM256_CACHE[key]
    best_index = 0
    best_dist = 255 * 255 * 3 + 1
    for i, (pr, pg, pb) in enumerate(_XTERM256_PALETTE):
        dr = r - pr
        dg = g - pg
        db = b - pb
        dist = dr * dr + dg * dg + db * db
        if dist < best_dist:
            best_dist = dist
            best_index = i
    _XTERM256_CACHE[key] = best_index
    return best_index


def _supports_truecolor(stream: object) -> bool:
    isatty = getattr(stream, "isatty", None)
    if isatty is None or not isatty():
        return False
    return os.environ.get("COLORTERM") in ("truecolor", "24bit")


def _color_escape(
    color: Color | str | None,
    mode: str,
) -> str:
    if color is None:
        return ""
    cache_key = (color, mode)
    if cache_key in _ESCAPE_CACHE:
        return _ESCAPE_CACHE[cache_key]
    color_str = color.value if isinstance(color, Color) else color
    if color_str is None or color_str == "":
        _ESCAPE_CACHE[cache_key] = ""
        return ""
    rgb = _color_to_rgb(color_str)
    if rgb is None:
        result = ""
    else:
        r, g, b = rgb
        if mode == "truecolor":
            result = f"\x1b[38;2;{r};{g};{b}m"
        elif mode == "xterm256":
            result = f"\x1b[38;5;{_nearest_xterm256(r, g, b)}m"
        else:
            result = ""
    _ESCAPE_CACHE[cache_key] = result
    return result


_KEY_NAMES: dict[tuple[int, ...], str] = {
    (0x1B, 0x5B, 0x41): "Up",
    (0x1B, 0x5B, 0x42): "Down",
    (0x1B, 0x5B, 0x43): "Right",
    (0x1B, 0x5B, 0x44): "Left",
    (0x1B, 0x5B, 0x48): "Home",
    (0x1B, 0x5B, 0x46): "End",
    (0x1B, 0x5B, 0x35, 0x7E): "PageUp",
    (0x1B, 0x5B, 0x36, 0x7E): "PageDown",
    (0x1B, 0x5B, 0x33, 0x7E): "Delete",
    (0x1B, 0x5B, 0x5A): "Shift+Tab",
    (0x1B, 0x4F, 0x50): "F1",
    (0x1B, 0x4F, 0x51): "F2",
    (0x1B, 0x4F, 0x52): "F3",
    (0x1B, 0x4F, 0x53): "F4",
    (0x1B, 0x4F, 0x54): "F5",
    (0x1B, 0x4F, 0x55): "F6",
    (0x1B, 0x4F, 0x56): "F7",
    (0x1B, 0x4F, 0x57): "F8",
    (0x1B, 0x5B, 0x31, 0x35, 0x7E): "F6",
    (0x1B, 0x5B, 0x31, 0x37, 0x7E): "F7",
    (0x1B, 0x5B, 0x31, 0x38, 0x7E): "F8",
    (0x1B, 0x5B, 0x31, 0x39, 0x7E): "F9",
    (0x1B, 0x5B, 0x32, 0x30, 0x7E): "F10",
    (0x1B, 0x5B, 0x32, 0x31, 0x7E): "F11",
    (0x1B, 0x5B, 0x32, 0x33, 0x7E): "F12",
}


def _key_name_for_bytes(data: bytes) -> str | None:
    if not data:
        return None
    key = tuple(data)
    if key in _KEY_NAMES:
        return _KEY_NAMES[key]
    if len(data) == 1:
        b = data[0]
        if b == 0x1B:
            return "Escape"
        if b in (0x0D, 0x0A):
            return "Return"
        if b == 0x09:
            return "Tab"
        if b == 0x7F or b == 0x08:
            return "Backspace"
        if 0x20 <= b <= 0x7E:
            return chr(b)
        return None
    if data[0] == 0x1B and len(data) >= 3 and data[1] == 0x5B:
        final = data[-1]
        if 0x40 <= final <= 0x7E:
            if final == 0x41:
                return "Up"
            if final == 0x42:
                return "Down"
            if final == 0x43:
                return "Right"
            if final == 0x44:
                return "Left"
    return None


def _parse_mouse_x10(data: bytes) -> tuple[int, int, int] | None:
    if len(data) < 4 or data[0] != 0x1B or data[1] != 0x5B or data[2] != 0x4D:
        return None
    cb = data[3]
    cx = data[4] if len(data) > 4 else 0
    cy = data[5] if len(data) > 5 else 0
    button = cb & 0x03
    x = max(0, cx - 33)
    y = max(0, cy - 33)
    return (button, x, y)


def _parse_mouse_sgr(data: bytes) -> tuple[int, int, int, bool] | None:
    if len(data) < 6 or data[0] != 0x1B or data[1] != 0x5B or data[2] != 0x3C:
        return None
    try:
        text = data.decode("ascii", errors="replace")
        if not text.startswith("\x1b[<"):
            return None
        rest = text[3:]
        if rest.endswith("m"):
            rest = rest[:-1]
            pressed = True
        elif rest.endswith("M"):
            rest = rest[:-1]
            pressed = False
        else:
            return None
        parts = rest.split(";")
        if len(parts) != 3:
            return None
        button = int(parts[0])
        x = int(parts[1]) - 1
        y = int(parts[2]) - 1
        return (button, max(0, x), max(0, y), pressed)
    except (ValueError, IndexError):
        return None


class _InputDriver:
    def __init__(self, renderer: TerminalRenderer) -> None:
        self._renderer = renderer
        self._thread: threading.Thread | None = None
        self._stop_event = threading.Event()
        self._old_settings: list[int] | None = None
        self._mouse_enabled = False

    def start(self) -> None:
        if self._thread is not None:
            return
        self._setup_terminal()
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
        self._restore_terminal()

    def _setup_terminal(self) -> None:
        if os.name == "nt":
            self._setup_windows()
        else:
            self._setup_unix()

    def _setup_unix(self) -> None:
        import termios
        import tty

        if not sys.stdin.isatty():
            return
        fd = sys.stdin.fileno()
        try:
            self._old_settings = list(termios.tcgetattr(fd))
        except Exception:
            self._old_settings = None
            return
        try:
            tty.setraw(fd)
        except Exception:
            self._old_settings = None
            return
        self._enable_mouse_reporting()

    def _setup_windows(self) -> None:
        try:
            ctypes_mod = importlib.import_module("ctypes")
            windll = getattr(ctypes_mod, "windll", None)
            if windll is None:
                return
            kernel32 = getattr(windll, "kernel32", None)
            if kernel32 is None:
                return
            handle = kernel32.GetStdHandle(-10)
            mode = ctypes_mod.c_uint32()
            if kernel32.GetConsoleMode(handle, ctypes_mod.byref(mode)):
                mode.value |= 0x0001
                kernel32.SetConsoleMode(handle, mode)
        except Exception:
            pass

    def _restore_terminal(self) -> None:
        if os.name == "nt":
            self._restore_windows()
        else:
            self._restore_unix()

    def _restore_unix(self) -> None:
        import termios

        self._disable_mouse_reporting()
        if self._old_settings is not None:
            fd = sys.stdin.fileno()
            try:
                settings: Any = self._old_settings
                termios.tcsetattr(fd, termios.TCSADRAIN, settings)
            except Exception:
                pass
            self._old_settings = None

    def _restore_windows(self) -> None:
        pass

    def _enable_mouse_reporting(self) -> None:
        if self._mouse_enabled:
            return
        self._mouse_enabled = True
        try:
            sys.stdout.write("\x1b[?1000h")
            sys.stdout.flush()
        except Exception:
            pass

    def _disable_mouse_reporting(self) -> None:
        if not self._mouse_enabled:
            return
        self._mouse_enabled = False
        try:
            sys.stdout.write("\x1b[?1000l")
            sys.stdout.flush()
        except Exception:
            pass

    def _run(self) -> None:
        frame_interval = 1.0 / self._renderer._fps
        last_frame = time.monotonic()
        while not self._stop_event.is_set():
            now = time.monotonic()
            if now - last_frame >= frame_interval:
                for callback in list(self._renderer._frame_bindings):
                    try:
                        callback()
                    except Exception:
                        pass
                last_frame = now
            data = self._read_bytes()
            if data is None or len(data) == 0:
                continue
            mouse = _parse_mouse_sgr(data)
            if mouse is not None:
                button, x, y, pressed = mouse
                self._dispatch_mouse(button, x, y, pressed)
                continue
            mouse = _parse_mouse_x10(data)
            if mouse is not None:
                button, x, y = mouse
                self._dispatch_mouse(button, x, y, True)
                continue
            key_name = _key_name_for_bytes(data)
            if key_name is not None:
                self._dispatch_key(key_name)

    def _read_bytes(self) -> bytes | None:
        if os.name == "nt":
            return self._read_windows()
        return self._read_unix()

    def _read_unix(self) -> bytes | None:
        import select

        if not sys.stdin.isatty():
            return None
        fd = sys.stdin.fileno()
        try:
            ready, _, _ = select.select([fd], [], [], 0.1)
        except (OSError, ValueError):
            return None
        if not ready:
            return None
        try:
            first = os.read(fd, 1)
        except OSError:
            return None
        if not first:
            return None
        data = first
        while len(data) < 17:
            try:
                ready, _, _ = select.select([fd], [], [], 0.01)
            except (OSError, ValueError):
                break
            if not ready:
                break
            try:
                more = os.read(fd, 17 - len(data))
            except OSError:
                break
            if not more:
                break
            data += more
        return data

    def _read_windows(self) -> bytes | None:
        msvcrt_mod = importlib.import_module("msvcrt")
        kbhit = getattr(msvcrt_mod, "kbhit", None)
        if kbhit is None or not kbhit():
            return None
        getch = getattr(msvcrt_mod, "getch", None)
        if getch is None:
            return None
        try:
            ch = getch()
        except OSError:
            return None
        data = bytes(ch)
        if ch in (b"\x00", b"\xe0"):
            try:
                ch2 = getch()
                data = data + bytes(ch2)
            except OSError:
                pass
        return data

    def _dispatch_key(self, key_name: str) -> None:
        bindings = list(self._renderer._key_down_bindings)
        for binding, callback in bindings:
            if binding == key_name:
                try:
                    callback(key_name)
                except Exception:
                    pass

    def _dispatch_mouse(
        self, button: int, x: int, y: int, pressed: bool
    ) -> None:
        bindings = (
            list(self._renderer._mouse_down_bindings)
            if pressed
            else list(self._renderer._mouse_up_bindings)
        )
        for callback in bindings:
            try:
                callback((x, y))
            except Exception:
                pass


class TerminalRenderer(Renderer):
    def __init__(
        self,
        width: int,
        height: int,
        title: str,
        default_bg: Color,
        default_fg: Color,
        fps: int,
        use_color: bool = True,
        stream: TextIO | None = None,
    ) -> None:
        super().__init__()
        self.width = width
        self.height = height
        self.title = title
        self.default_bg = default_bg
        self.default_fg = default_fg
        self._fps = fps
        self.use_color = use_color
        self.stream = stream if stream is not None else sys.stdout
        self._running = False
        self._colorama_initialized = False
        self._color_mode: str | None = None
        self._screen_cleared = False
        self._cursor_hidden = False
        self._input_driver: _InputDriver | None = None

    def _init_colorama(self) -> None:
        if self._colorama_initialized:
            return
        self._colorama_initialized = True
        if colorama is not None and os.name == "nt":
            colorama.init()

    def _detect_mode(self) -> str:
        if self._color_mode is not None:
            return self._color_mode
        if not self.use_color:
            self._color_mode = "plain"
            return self._color_mode
        if _supports_truecolor(self.stream):
            self._color_mode = "truecolor"
        else:
            self._color_mode = "xterm256"
        return self._color_mode

    @override
    def start(self) -> None:
        self._init_colorama()
        self._running = True
        self._input_driver = _InputDriver(self)
        self._input_driver.start()
        empty_grid = Grid(self.width, self.height)
        self.render(empty_grid)
        self._hide_cursor()
        if sys.stdin.isatty():
            thread = self._input_driver._thread
            if thread is not None:
                try:
                    thread.join()
                finally:
                    self.stop()

    @override
    def stop(self) -> None:
        self._running = False
        self._show_cursor()
        if self._input_driver is not None:
            self._input_driver.stop()
            self._input_driver = None

    @override
    def render(
        self,
        grid: Grid,
        camera: Camera | None = None,
        region: tuple[int, int, int, int] | None = None,
    ) -> None:
        mode = self._detect_mode()
        if region is None:
            self._render_full(grid, mode)
        else:
            self._render_region(grid, region, mode)

    def _render_full(self, grid: Grid, mode: str) -> None:
        content = grid.content
        colors = grid.colors
        width = grid.width
        lines: list[str] = [
            self._row_runs(content[y], colors[y], 0, width, mode)
            for y in range(grid.height)
        ]
        result = "\r\n".join(lines) + "\r\n"
        if mode != "plain":
            if not self._screen_cleared:
                result = "\x1b[2J\x1b[H" + result
                self._screen_cleared = True
            else:
                result = "\x1b[H" + result
            result += "\x1b[0m"
        self.stream.write(result)
        self._flush()

    def _render_region(
        self, grid: Grid, region: tuple[int, int, int, int], mode: str
    ) -> None:
        rx, ry, rw, rh = region
        bottom = min(ry + rh, grid.height)
        right = min(rx + rw, grid.width)
        if bottom <= ry or right <= rx:
            return
        parts: list[str] = []
        content = grid.content
        colors = grid.colors
        for y in range(ry, bottom):
            parts.append(f"\x1b[{y + 1};{rx + 1}H")
            parts.append(
                self._row_runs(content[y], colors[y], rx, right, mode)
            )
        result = "".join(parts)
        if mode != "plain":
            result += "\x1b[0m"
        self.stream.write(result)
        self._flush()

    def _row_runs(
        self,
        row_chars: list[str],
        row_colors: list[Color | None],
        x_start: int,
        x_end: int,
        mode: str,
    ) -> str:
        if mode == "plain":
            return "".join(row_chars[x_start:x_end])
        parts: list[str] = []
        x = x_start
        color = row_colors[x]
        escape = _color_escape(color, mode)
        while x < x_end:
            end = x + 1
            next_escape = escape
            while end < x_end:
                next_color = row_colors[end]
                if next_color is color:
                    end += 1
                    continue
                next_escape = _color_escape(next_color, mode)
                if next_escape != escape:
                    break
                color = next_color
                end += 1
            run_chars = (
                row_chars[x] if end == x + 1 else "".join(row_chars[x:end])
            )
            if escape:
                parts.append(escape)
            parts.append(run_chars)
            if escape:
                parts.append("\x1b[0m")
            x = end
            if x < x_end:
                color = row_colors[x]
                escape = next_escape
        return "".join(parts)

    def _flush(self) -> None:
        flush = getattr(self.stream, "flush", None)
        if flush is not None:
            flush()

    def _hide_cursor(self) -> None:
        if self._cursor_hidden:
            return
        self._cursor_hidden = True
        try:
            self.stream.write("\x1b[?25l")
            self.stream.flush()
        except Exception:
            pass

    def _show_cursor(self) -> None:
        if not self._cursor_hidden:
            return
        self._cursor_hidden = False
        try:
            self.stream.write("\x1b[?25h")
            self.stream.flush()
        except Exception:
            pass

    @override
    def set_title(self, title: str) -> None:
        self.title = title

    @override
    def set_size(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

    @override
    def set_fps(self, fps: int) -> None:
        if fps <= 0:
            msg = "fps must be positive"
            raise ValueError(msg)
        self._fps = fps
