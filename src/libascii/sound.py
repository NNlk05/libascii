from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    import simpleaudio as _sa_typing

    PlayObject = _sa_typing.PlayObject
    WaveObject = _sa_typing.WaveObject
else:
    PlayObject = object
    WaveObject = object


sa: object | None = None


def _import_simpleaudio() -> object:
    global sa
    if sa is not None:
        return sa
    try:
        import simpleaudio as _sa_module
    except ImportError as exc:
        msg = (
            "simpleaudio is required for Sound. Install it with "
            "`uv add --group audio simpleaudio` or `pip install simpleaudio`."
        )
        raise ImportError(msg) from exc
    sa = _sa_module
    return _sa_module


class Sound:
    def __init__(self, path: str | Path) -> None:
        sa_module = _import_simpleaudio()
        try:
            self.wave_object = cast(
                WaveObject,
                getattr(sa_module, "WaveObject").from_wave_file(str(path)),
            )
        except (FileNotFoundError, OSError, ValueError) as exc:
            msg = f"could not load sound from {path!r}: {exc}"
            raise ValueError(msg) from exc

    def play(self) -> PlayObject:
        sa_module = _import_simpleaudio()
        return cast(PlayObject, self.wave_object.play())

    def stop(self, play_object: PlayObject) -> None:
        if play_object is None:
            msg = "play_object must not be None"
            raise ValueError(msg)
        play_object.stop()

    def is_playing(self, play_object: PlayObject) -> bool:
        if play_object is None:
            msg = "play_object must not be None"
            raise ValueError(msg)
        return cast(bool, play_object.is_playing())

    def wait_done(self, play_object: PlayObject) -> None:
        if play_object is None:
            msg = "play_object must not be None"
            raise ValueError(msg)
        play_object.wait_done()
