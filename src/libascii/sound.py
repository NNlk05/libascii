from pathlib import Path

import simpleaudio as sa


class Sound:
    def __init__(self, path: str | Path) -> None:
        try:
            self.wave_object = sa.WaveObject.from_wave_file(str(path))
        except (FileNotFoundError, OSError, ValueError) as exc:
            msg = f"could not load sound from {path!r}: {exc}"
            raise ValueError(msg) from exc

    def play(self) -> sa.PlayObject:
        return self.wave_object.play()

    def stop(self, play_object: sa.PlayObject) -> None:
        if play_object is None:
            msg = "play_object must not be None"
            raise ValueError(msg)
        play_object.stop()

    def is_playing(self, play_object: sa.PlayObject) -> bool:
        if play_object is None:
            msg = "play_object must not be None"
            raise ValueError(msg)
        return play_object.is_playing()

    def wait_done(self, play_object: sa.PlayObject) -> None:
        if play_object is None:
            msg = "play_object must not be None"
            raise ValueError(msg)
        play_object.wait_done()
