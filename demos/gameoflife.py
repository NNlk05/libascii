from libascii import Game, Color, Grid
from libascii.chars import get_char

ALIVE = get_char("MAIN", "BLOCK")
DEAD = " "
CURSOR_OUTLINE = get_char("MAIN", "CIRCLE_OUTLINE")
CURSOR_FILLED = get_char("MAIN", "CIRCLE_FILLED")

ALIVE_COLOR = Color("white")
DEAD_COLOR = Color("black")
CURSOR_COLOR = Color("white")

LOGICAL_WIDTH = 16
LOGICAL_HEIGHT = 16
DISPLAY_WIDTH = 32
DISPLAY_HEIGHT = 16


def main() -> None:
    cx = 0
    cy = 0
    paused = False

    game = Game(
        DISPLAY_WIDTH,
        DISPLAY_HEIGHT,
        "Conway's Game of Life",
        fps=4,
    )
    grid = Grid(LOGICAL_WIDTH, LOGICAL_HEIGHT, DEAD)

    def get_cell(x: int, y: int) -> str:
        state, _ = grid.get(x, y)
        return state

    def set_cell(x: int, y: int, state: str) -> None:
        grid.set(x, y, state)

    def move_cursor(dx: int, dy: int) -> None:
        nonlocal cx, cy
        cx = max(0, min(LOGICAL_WIDTH - 1, cx + dx))
        cy = max(0, min(LOGICAL_HEIGHT - 1, cy + dy))

    def toggle_cell() -> None:
        state = get_cell(cx, cy)
        set_cell(cx, cy, DEAD if state == ALIVE else ALIVE)

    def toggle_pause() -> None:
        nonlocal paused
        paused = not paused

    def tick() -> None:
        if paused:
            return
        next_states: dict[tuple[int, int], str] = {}
        for cell_x in range(LOGICAL_WIDTH):
            for cell_y in range(LOGICAL_HEIGHT):
                cell_state = get_cell(cell_x, cell_y)
                neighbors_count = 0
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = cell_x + dx, cell_y + dy
                        if not grid.in_bounds(nx, ny):
                            continue
                        if get_cell(nx, ny) == ALIVE:
                            neighbors_count += 1
                if cell_state == ALIVE:
                    next_states[(cell_x, cell_y)] = (
                        ALIVE if neighbors_count in (2, 3) else DEAD
                    )
                elif neighbors_count == 3:
                    next_states[(cell_x, cell_y)] = ALIVE
        for (x, y), state in next_states.items():
            if state != get_cell(x, y):
                set_cell(x, y, state)

    def render() -> None:
        game.clear()
        for y in range(LOGICAL_HEIGHT):
            for x in range(LOGICAL_WIDTH):
                state = get_cell(x, y)
                color = ALIVE_COLOR if state == ALIVE else DEAD_COLOR
                display_x = 2 * x
                game.set(display_x, y, state, color)
                game.set(display_x + 1, y, state, color)
        cursor_x = 2 * cx
        on_cell = get_cell(cx, cy) == ALIVE
        cursor_char = CURSOR_FILLED if on_cell else CURSOR_OUTLINE
        game.set(cursor_x, cy, cursor_char, CURSOR_COLOR)
        game.refresh()

    game.on_key_down("Up", lambda _: move_cursor(0, -1))
    game.on_key_down("Down", lambda _: move_cursor(0, 1))
    game.on_key_down("Left", lambda _: move_cursor(-1, 0))
    game.on_key_down("Right", lambda _: move_cursor(1, 0))
    game.on_key_down("space", lambda _: toggle_cell())
    game.on_key_down("Return", lambda _: toggle_pause())
    game.on_frame(lambda: (tick(), render()))

    with game:
        pass


if __name__ == "__main__":
    main()
