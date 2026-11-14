from typing import Any, cast

from unittest.mock import MagicMock

from libascii import Sound


def test_sound_play_calls_playsound() -> None:
    mock_play_object = MagicMock()
    mock_ps = MagicMock()
    mock_ps.playsound.return_value = mock_play_object

    import libascii.sound as sound_module

    original_ps = sound_module.ps
    sound_module.ps = mock_ps
    try:
        s = Sound("test.wav")
        result = s.play()
        mock_ps.playsound.assert_called_once_with("test.wav", block=False)
        assert result is mock_play_object
    finally:
        sound_module.ps = original_ps


def test_sound_stop_with_none_raises() -> None:
    import libascii.sound as sound_module

    original_ps = sound_module.ps
    sound_module.ps = MagicMock()
    try:
        s = Sound("test.wav")
        try:
            s.stop(cast(Any, None))
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for None play_object")
    finally:
        sound_module.ps = original_ps


def test_sound_is_playing_with_none_raises() -> None:
    import libascii.sound as sound_module

    original_ps = sound_module.ps
    sound_module.ps = MagicMock()
    try:
        s = Sound("test.wav")
        try:
            s.is_playing(cast(Any, None))
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for None play_object")
    finally:
        sound_module.ps = original_ps


def test_sound_wait_done_with_none_raises() -> None:
    import libascii.sound as sound_module

    original_ps = sound_module.ps
    sound_module.ps = MagicMock()
    try:
        s = Sound("test.wav")
        try:
            s.wait_done(cast(Any, None))
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError for None play_object")
    finally:
        sound_module.ps = original_ps


def test_sound_init_stores_path() -> None:
    import libascii.sound as sound_module

    original_ps = sound_module.ps
    sound_module.ps = None
    try:
        s = Sound("test.wav")
        assert s.path == "test.wav"
    finally:
        sound_module.ps = original_ps
