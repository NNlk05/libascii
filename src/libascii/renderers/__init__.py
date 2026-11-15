from __future__ import annotations

from typing import TYPE_CHECKING

from .._renderers.base import BindingMixin, Renderer

__all__ = ["BindingMixin", "Renderer"]

if TYPE_CHECKING:
    from .headless import HeadlessRenderer  # noqa: F401
    from .terminal import TerminalRenderer  # noqa: F401
    from .tk import TkRenderer  # noqa: F401


def __getattr__(name: str) -> object:
    if name == "HeadlessRenderer":
        from .headless import HeadlessRenderer

        return HeadlessRenderer
    if name == "TerminalRenderer":
        from .terminal import TerminalRenderer

        return TerminalRenderer
    if name == "TkRenderer":
        from .tk import TkRenderer

        return TkRenderer
    msg = f"module {__name__!r} has no attribute {name!r}"
    raise AttributeError(msg)
