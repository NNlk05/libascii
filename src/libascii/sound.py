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


__all__ = ["Sound"]

_ps: object | None = None


def _import_playsound3() -> object:
    global _ps
    if _ps is not None:
        return _ps
    try:
        import playsound3 as _ps_module
    except ImportError as exc:
        msg = (
            "playsound3 is required for Sound. Install it with "
            "`uv add --group audio playsound3` or `pip install playsound3`."
        )
        raise ImportError(msg) from exc
    _ps = _ps_module
    return _ps_module


class Sound:
    def __init__(self, path: str | Path) -> None:
        if not isinstance(path, (str, Path)):
            msg = f"path must be str or Path, got {type(path).__name__}"
            raise TypeError(msg)
        path_str = str(path)
        if not path_str:
            msg = "path must not be empty"
            raise ValueError(msg)
        self.path = path_str
        self._active: list[PlayObject] = []
        self._lock = threading.Lock()

    def _prune(self) -> None:
        self._active = [obj for obj in self._active if obj.is_alive()]

    def play(self, block: bool = False) -> PlayObject:
        ps_module = _import_playsound3()
        try:
            play_object = cast(
                PlayObject,
                getattr(ps_module, "playsound")(self.path, block=block),
            )
        except Exception as exc:
            msg = f"failed to play {self.path}: {exc}"
            raise RuntimeError(msg) from exc
        if play_object is None:
            msg = f"failed to play {self.path}: playsound3 returned None"
            raise RuntimeError(msg)
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
        try:
            play_object.stop()
        except (OSError, ProcessLookupError):
            pass

    def is_playing(self, play_object: PlayObject) -> bool:
        if play_object is None:
            msg = "play_object must not be None"
            raise ValueError(msg)
        return play_object.is_alive()

    def wait_done(
        self, play_object: PlayObject, timeout: float | None = None
    ) -> None:
        if play_object is None:
            msg = "play_object must not be None"
            raise ValueError(msg)
        if timeout is None:
            play_object.wait()
            return
        done = threading.Event()

        def _wait() -> None:
            try:
                play_object.wait()
            except Exception:
                pass
            finally:
                done.set()

        waiter = threading.Thread(target=_wait, daemon=True)
        waiter.start()
        if not done.wait(timeout):
            msg = f"playback of {self.path} did not complete within {timeout}s"
            raise TimeoutError(msg)

    def close(self) -> None:
        self.stop_all()

    def __enter__(self) -> Sound:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
