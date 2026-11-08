from libascii import Camera, Color, Game, Grid, ParticleSystem, draw_text
from libascii.chars import get_char

ALIVE = get_char("MAIN", "BLOCK")
DEAD = " "
CURSOR_OUTLINE = get_char("MAIN", "CIRCLE_OUTLINE")
CURSOR_FILLED = get_char("MAIN", "CIRCLE_FILLED")

ALIVE_COLOR = Color("white")
DEAD_COLOR = Color("black")
CURSOR_COLOR = Color("white")
BIRTH_COLOR = Color("green")
DEATH_COLOR = Color("red")

LOGICAL_WIDTH = 40
LOGICAL_HEIGHT = 30
DISPLAY_WIDTH = 32
DISPLAY_HEIGHT = 16


def main() -> None:
    cx = LOGICAL_WIDTH // 2
    cy = LOGICAL_HEIGHT // 2
    paused = False
    generation = 0

    game = Game(
        DISPLAY_WIDTH,
        DISPLAY_HEIGHT,
        "Conway's Game of Life",
        fps=4,
    )
    grid = Grid(LOGICAL_WIDTH, LOGICAL_HEIGHT, DEAD)
    camera = Camera(
        DISPLAY_WIDTH, DISPLAY_HEIGHT, LOGICAL_WIDTH, LOGICAL_HEIGHT
    )
    particles = ParticleSystem()

    def get_cell(x: int, y: int) -> str:
        state, _ = grid.get(x, y)
        return state

    def set_cell(x: int, y: int, state: str) -> None:
        grid.set(x, y, state)

    def move_cursor(dx: int, dy: int) -> None:
        nonlocal cx, cy
        cx = max(0, min(LOGICAL_WIDTH - 1, cx + dx))
        cy = max(0, min(LOGICAL_HEIGHT - 1, cy + dy))
        camera.follow(cx, cy)

    def toggle_cell() -> None:
        state = get_cell(cx, cy)
        set_cell(cx, cy, DEAD if state == ALIVE else ALIVE)

    def toggle_pause() -> None:
        nonlocal paused
        paused = not paused

    def tick() -> None:
        nonlocal generation
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
                    if neighbors_count not in (2, 3):
                        next_states[(cell_x, cell_y)] = DEAD
                elif neighbors_count == 3:
                    next_states[(cell_x, cell_y)] = ALIVE
        for (x, y), state in next_states.items():
            if state != get_cell(x, y):
                set_cell(x, y, state)
                if state == ALIVE:
                    particles.emit(
                        x + 0.5,
                        y + 0.5,
                        life=0.5,
                        char="*",
                        color=BIRTH_COLOR,
                    )
                else:
                    particles.emit(
                        x + 0.5,
                        y + 0.5,
                        life=0.5,
                        char="x",
                        color=DEATH_COLOR,
                    )
        generation += 1

    def render() -> None:
        game.clear()
        ox, oy = camera.offset
        for y in range(LOGICAL_HEIGHT):
            if not oy <= y < oy + DISPLAY_HEIGHT:
                continue
            for x in range(LOGICAL_WIDTH):
                if not ox <= x < ox + DISPLAY_WIDTH:
                    continue
                state = get_cell(x, y)
                if state == DEAD:
                    continue
                display_x = 2 * (x - ox)
                display_y = y - oy
                game.set(display_x, display_y, state, ALIVE_COLOR)
                game.set(display_x + 1, display_y, state, ALIVE_COLOR)
        cursor_display_x = 2 * (cx - ox)
        cursor_display_y = cy - oy
        if (
            0 <= cursor_display_x < DISPLAY_WIDTH
            and 0 <= cursor_display_y < DISPLAY_HEIGHT
        ):
            on_cell = get_cell(cx, cy) == ALIVE
            cursor_char = CURSOR_FILLED if on_cell else CURSOR_OUTLINE
            game.set(
                cursor_display_x, cursor_display_y, cursor_char, CURSOR_COLOR
            )
        particles.update(1.0 / game.fps)
        particles.draw(game.grid)
        draw_text(
            game.grid,
            0,
            0,
            [f"Gen: {generation}"],
            color=Color("white"),
            align_mode="left",
        )
        if paused:
            draw_text(
                game.grid,
                0,
                DISPLAY_HEIGHT - 1,
                ["PAUSED"],
                color=Color("white"),
                align_mode="center",
            )
        game.refresh()

    game.on_key_down("Up", lambda _: move_cursor(0, -1))
    game.on_key_down("Down", lambda _: move_cursor(0, 1))
    game.on_key_down("Left", lambda _: move_cursor(-1, 0))
    game.on_key_down("Right", lambda _: move_cursor(1, 0))
    game.on_key_down("w", lambda _: move_cursor(0, -1))
    game.on_key_down("s", lambda _: move_cursor(0, 1))
    game.on_key_down("a", lambda _: move_cursor(-1, 0))
    game.on_key_down("d", lambda _: move_cursor(1, 0))
    game.bind_action("toggle_cell", "space")
    game.bind_action("toggle_pause", "Return")

    def on_frame_callback() -> None:
        tick()
        if game.action_was_pressed("toggle_cell"):
            toggle_cell()
        if game.action_was_pressed("toggle_pause"):
            toggle_pause()
        render()

    game.on_frame(on_frame_callback)

    with game:
        pass


if __name__ == "__main__":
    main()
