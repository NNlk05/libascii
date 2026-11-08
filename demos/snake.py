import random

from libascii import Color, Game, ParticleSystem, draw_text

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

OPPOSITE = {
    UP: DOWN,
    DOWN: UP,
    LEFT: RIGHT,
    RIGHT: LEFT,
}

SNAKE_CHAR = "#"
FOOD_CHAR = "*"
SNAKE_COLOR = Color("green")
FOOD_COLOR = Color("red")
SCORE_COLOR = Color("white")
GAME_OVER_COLOR = Color("white")


class SnakeGame:
    def __init__(
        self, width: int = 40, height: int = 20, fps: int = 10
    ) -> None:
        self.game = Game(
            width=width,
            height=height,
            title="Snake",
            fps=fps,
        )
        self.snake: list[tuple[int, int]] = [(5, 5), (4, 5), (3, 5)]
        self.direction = RIGHT
        self.food: tuple[int, int] | None = None
        self.score = 0
        self.game_over = False
        self.particles = ParticleSystem()
        self._bind_actions()
        self._spawn_food()
        self.game.on_frame(self._tick)

    def _bind_actions(self) -> None:
        self.game.bind_action("move_up", "Up")
        self.game.bind_action("move_down", "Down")
        self.game.bind_action("move_left", "Left")
        self.game.bind_action("move_right", "Right")

    def _spawn_food(self) -> None:
        while True:
            candidate = (
                random.randint(0, self.game.width - 1),
                random.randint(0, self.game.height - 1),
            )
            if candidate not in self.snake:
                self.food = candidate
                return

    def _explode(self, x: int, y: int, color: Color) -> None:
        for _ in range(6):
            self.particles.emit(
                x + 0.5,
                y + 0.5,
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                life=random.uniform(0.3, 0.7),
                char="*",
                color=color,
            )

    def _tick(self) -> None:
        if not self.game_over:
            if self.game.action_was_pressed("move_up"):
                if self.direction != DOWN:
                    self.direction = UP
            elif self.game.action_was_pressed("move_down"):
                if self.direction != UP:
                    self.direction = DOWN
            elif self.game.action_was_pressed("move_left"):
                if self.direction != RIGHT:
                    self.direction = LEFT
            elif self.game.action_was_pressed("move_right"):
                if self.direction != LEFT:
                    self.direction = RIGHT

            head_x, head_y = self.snake[0]
            dir_x, dir_y = self.direction
            new_head = (head_x + dir_x, head_y + dir_y)

            if (
                new_head[0] < 0
                or new_head[0] >= self.game.width
                or new_head[1] < 0
                or new_head[1] >= self.game.height
            ):
                self.game_over = True
                self._explode(head_x, head_y, GAME_OVER_COLOR)

            elif new_head in self.snake:
                self.game_over = True
                self._explode(head_x, head_y, GAME_OVER_COLOR)

            else:
                self.snake.insert(0, new_head)
                if self.food is not None and new_head == self.food:
                    self.score += 10
                    self._explode(new_head[0], new_head[1], FOOD_COLOR)
                    self._spawn_food()
                else:
                    self.snake.pop()

        self.particles.update(1.0 / self.game.fps)
        self._render()

    def _render(self) -> None:
        self.game.clear()
        if self.food is not None:
            self.game.set(self.food[0], self.food[1], FOOD_CHAR, FOOD_COLOR)
        for segment in self.snake:
            self.game.set(segment[0], segment[1], SNAKE_CHAR, SNAKE_COLOR)
        self.particles.draw(self.game.grid)
        draw_text(
            self.game.grid,
            0,
            0,
            [f"Score: {self.score}"],
            color=SCORE_COLOR,
            align_mode="left",
        )
        if self.game_over:
            draw_text(
                self.game.grid,
                10,
                9,
                ["GAME OVER"],
                color=GAME_OVER_COLOR,
                align_mode="left",
            )
        self.game.refresh()

    def run(self) -> None:
        self.game.start()


if __name__ == "__main__":
    SnakeGame().run()
