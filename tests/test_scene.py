from libascii import Scene, SceneManager
from libascii.grid import Grid


class MockScene(Scene):
    def __init__(self, name: str) -> None:
        self.name = name
        self.entered = False
        self.exited = False
        self.updated_dt: float | None = None
        self.drew_grid = False

    def enter(self) -> None:
        self.entered = True

    def exit(self) -> None:
        self.exited = True

    def update(self, dt: float) -> None:
        self.updated_dt = dt

    def draw(self, grid: Grid) -> None:
        self.drew_grid = True


def test_current_none_on_empty() -> None:
    sm = SceneManager()
    assert sm.current is None


def test_push_enters_new_scene() -> None:
    sm = SceneManager()
    s1 = MockScene("s1")
    sm.push(s1)
    assert sm.current is s1
    assert s1.entered is True
    assert s1.exited is False


def test_push_pauses_previous_calls_exit() -> None:
    sm = SceneManager()
    s1 = MockScene("s1")
    s2 = MockScene("s2")
    sm.push(s1)
    sm.push(s2)
    assert sm.current is s2
    assert s1.exited is True
    assert s2.entered is True
    assert s2.exited is False


def test_pop_exits_top_and_enters_new_top() -> None:
    sm = SceneManager()
    s1 = MockScene("s1")
    s2 = MockScene("s2")
    sm.push(s1)
    sm.push(s2)
    popped = sm.pop()
    assert popped is s2
    assert s2.exited is True
    assert sm.current is s1
    assert s1.entered is True
    assert s1.exited is True


def test_pop_last_scene_clears_stack() -> None:
    sm = SceneManager()
    s1 = MockScene("s1")
    sm.push(s1)
    sm.pop()
    assert sm.current is None
    assert s1.exited is True


def test_pop_on_empty_raises_index_error() -> None:
    sm = SceneManager()
    try:
        sm.pop()
    except IndexError:
        pass
    else:
        raise AssertionError("expected IndexError on pop of empty stack")


def test_replace_exits_old_and_enters_new_once() -> None:
    sm = SceneManager()
    s1 = MockScene("s1")
    s2 = MockScene("s2")
    sm.push(s1)
    sm.replace(s2)
    assert sm.current is s2
    assert s1.exited is True
    assert s2.entered is True
    assert s2.exited is False


def test_replace_on_empty_just_enters() -> None:
    sm = SceneManager()
    s1 = MockScene("s1")
    sm.replace(s1)
    assert sm.current is s1
    assert s1.entered is True
    assert s1.exited is False


def test_update_only_top() -> None:
    sm = SceneManager()
    s1 = MockScene("s1")
    s2 = MockScene("s2")
    sm.push(s1)
    sm.push(s2)
    sm.update(0.5)
    assert s1.updated_dt is None
    assert s2.updated_dt == 0.5


def test_update_empty_stack_noop() -> None:
    sm = SceneManager()
    sm.update(0.5)


def test_draw_only_top() -> None:
    sm = SceneManager()
    s1 = MockScene("s1")
    s2 = MockScene("s2")
    sm.push(s1)
    sm.push(s2)
    grid = Grid(5, 5)
    sm.draw(grid)
    assert s1.drew_grid is False
    assert s2.drew_grid is True


def test_draw_empty_stack_noop() -> None:
    sm = SceneManager()
    grid = Grid(5, 5)
    sm.draw(grid)
