from libascii import Camera


def test_camera_initial_state() -> None:
    cam = Camera(10, 8, 100, 60)
    assert cam.viewport_width == 10
    assert cam.viewport_height == 8
    assert cam.world_width == 100
    assert cam.world_height == 60
    assert cam.offset == (0, 0)
    assert cam.visible_rect == (0, 0, 10, 8)


def test_camera_set_offset_clamps_negative() -> None:
    cam = Camera(10, 8, 100, 60)
    cam.set_offset(-5, -5)
    assert cam.offset == (0, 0)


def test_camera_set_offset_clamps_max() -> None:
    cam = Camera(10, 8, 100, 60)
    cam.set_offset(200, 200)
    assert cam.offset == (90, 52)


def test_camera_set_offset_within_range() -> None:
    cam = Camera(10, 8, 100, 60)
    cam.set_offset(50, 30)
    assert cam.offset == (50, 30)


def test_camera_world_smaller_than_screen_stays_zero() -> None:
    cam = Camera(100, 50, 10, 10)
    cam.set_offset(5, 5)
    assert cam.offset == (0, 0)


def test_camera_viewport_equals_world_stays_zero() -> None:
    cam = Camera(100, 60, 100, 60)
    cam.set_offset(10, 10)
    assert cam.offset == (0, 0)


def test_camera_follow_centers_target() -> None:
    cam = Camera(10, 8, 100, 60)
    cam.follow(5, 4)
    assert cam.offset == (1, 1)


def test_camera_follow_target_at_world_edge_clamps() -> None:
    cam = Camera(10, 8, 100, 60)
    cam.follow(95, 55)
    assert cam.offset == (90, 52)


def test_camera_follow_negative_target_clamps() -> None:
    cam = Camera(10, 8, 100, 60)
    cam.follow(1, 1)
    assert cam.offset == (0, 0)


def test_camera_visible_rect_reflects_offset() -> None:
    cam = Camera(10, 8, 100, 60)
    cam.follow(95, 55)
    assert cam.visible_rect == (90, 52, 10, 8)


def test_camera_visible_rect_initial() -> None:
    cam = Camera(5, 5, 20, 20)
    assert cam.visible_rect == (0, 0, 5, 5)


def test_camera_set_offset_only_x() -> None:
    cam = Camera(10, 8, 100, 60)
    cam.set_offset(40, 0)
    assert cam.offset == (40, 0)


def test_camera_set_offset_only_y() -> None:
    cam = Camera(10, 8, 100, 60)
    cam.set_offset(0, 20)
    assert cam.offset == (0, 20)
