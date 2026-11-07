from pathlib import Path

import simpleaudio as sa


class Sound:
    def __init__(self, path: str | Path) -> None:
        self.wave_object = sa.WaveObject.from_wave_file(str(path))

    @classmethod
    def from_wav(cls, path: str | Path) -> "Sound":
        return cls(path)

    def play(self) -> sa.PlayObject:
        return self.wave_object.play()

    def stop(self, play_object: sa.PlayObject) -> None:
        play_object.stop()

    def is_playing(self, play_object: sa.PlayObject) -> bool:
        return play_object.is_playing()

    def wait_done(self, play_object: sa.PlayObject) -> None:
        play_object.wait_done()
