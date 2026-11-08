from typing import Any, cast

from unittest.mock import MagicMock

from libascii import Sound


def test_sound_init_loads_wave_object() -> None:
    mock_wave_object = MagicMock()
    mock_sa = MagicMock()
    mock_sa.WaveObject.from_wave_file.return_value = mock_wave_object

    import libascii.sound as sound_module

    original_sa = sound_module.sa
    sound_module.sa = mock_sa
    try:
        s = Sound("test.wav")
        mock_sa.WaveObject.from_wave_file.assert_called_once_with("test.wav")
        assert s.wave_object is mock_wave_object
    finally:
        sound_module.sa = original_sa


def test_sound_play_calls_wave_object_play() -> None:
    mock_play_object = MagicMock()
    mock_wave_object = MagicMock()
    mock_wave_object.play.return_value = mock_play_object
    mock_sa = MagicMock()
    mock_sa.WaveObject.from_wave_file.return_value = mock_wave_object

    import libascii.sound as sound_module

    original_sa = sound_module.sa
    sound_module.sa = mock_sa
    try:
        s = Sound("test.wav")
        result = s.play()
        mock_wave_object.play.assert_called_once()
        assert result is mock_play_object
    finally:
        sound_module.sa = original_sa


def test_sound_stop_with_none_raises() -> None:
    mock_sa = MagicMock()
    mock_sa.PlayObject = MagicMock

    import libascii.sound as sound_module

    original_sa = sound_module.sa
    sound_module.sa = mock_sa
    try:
        s = Sound("test.wav")
        try:
            s.stop(cast(Any, None))
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for None play_object")
    finally:
        sound_module.sa = original_sa


def test_sound_is_playing_with_none_raises() -> None:
    mock_sa = MagicMock()
    mock_sa.PlayObject = MagicMock

    import libascii.sound as sound_module

    original_sa = sound_module.sa
    sound_module.sa = mock_sa
    try:
        s = Sound("test.wav")
        try:
            s.is_playing(cast(Any, None))
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for None play_object")
    finally:
        sound_module.sa = original_sa


def test_sound_wait_done_with_none_raises() -> None:
    mock_sa = MagicMock()
    mock_sa.PlayObject = MagicMock

    import libascii.sound as sound_module

    original_sa = sound_module.sa
    sound_module.sa = mock_sa
    try:
        s = Sound("test.wav")
        try:
            s.wait_done(cast(Any, None))
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for None play_object")
    finally:
        sound_module.sa = original_sa


def test_sound_init_file_not_found_raises() -> None:
    mock_sa = MagicMock()
    mock_sa.WaveObject.from_wave_file.side_effect = FileNotFoundError(
        "no file"
    )

    import libascii.sound as sound_module

    original_sa = sound_module.sa
    sound_module.sa = mock_sa
    try:
        try:
            Sound("missing.wav")
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for missing file")
    finally:
        sound_module.sa = original_sa
