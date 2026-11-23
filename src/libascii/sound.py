from __future__ import annotations

import threading

from pathlib import Path
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from typing import Protocol

    class _PlayObject(Protocol):
        def stop(self) -> None: ...

        def is_alive(self) -> bool: ...

        def wait(self) -> None: ...

    PlayObject = _PlayObject
else:
    PlayObject = object


ps: object | None = None


def _import_playsound3() -> object:
    global ps
    if ps is not None:
        return ps
    try:
        import playsound3 as _ps_module
    except ImportError as exc:
        msg = (
            "playsound3 is required for Sound. Install it with "
            "`uv add --group audio playsound3` or `pip install playsound3`."
        )
        raise ImportError(msg) from exc
    ps = _ps_module
    return _ps_module


class Sound:
    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        self._active: list[PlayObject] = []
        self._lock = threading.Lock()

    def _prune(self) -> None:
        self._active = [obj for obj in self._active if obj.is_alive()]

    def play(self) -> PlayObject:
        ps_module = _import_playsound3()
        play_object = cast(
            PlayObject, getattr(ps_module, "playsound")(self.path, block=False)
        )
        with self._lock:
            self._prune()
            self._active.append(play_object)
        return play_object

    def stop_all(self) -> None:
        with self._lock:
            for play_object in self._active:
                try:
                    play_object.stop()
                except (OSError, ProcessLookupError):
                    pass
            self._active.clear()

    def stop_active(self) -> None:
        self.stop_all()

    def stop(self, play_object: PlayObject) -> None:
        if play_object is None:
            msg = "play_object must not be None"
            raise ValueError(msg)
        play_object.stop()

    def is_playing(self, play_object: PlayObject) -> bool:
        if play_object is None:
            msg = "play_object must not be None"
            raise ValueError(msg)
        return play_object.is_alive()

    def wait_done(self, play_object: PlayObject) -> None:
        if play_object is None:
            msg = "play_object must not be None"
            raise ValueError(msg)
        play_object.wait()
