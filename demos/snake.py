import random

from libascii import Color, Game

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

KEY_MAP = {
    "Up": UP,
    "Down": DOWN,
    "Left": LEFT,
    "Right": RIGHT,
    "w": UP,
    "s": DOWN,
    "a": LEFT,
    "d": RIGHT,
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
        self.next_direction = RIGHT
        self.food: tuple[int, int] | None = None
        self.score = 0
        self.game_over = False
        self._bind_keys()
        self._spawn_food()
        self.game.on_frame(self._tick)

    def _bind_keys(self) -> None:
        for key, direction in KEY_MAP.items():
            self.game.on_key_down(
                key, lambda _, d=direction: self._set_direction(d)
            )

    def _set_direction(self, direction: tuple[int, int]) -> None:
        if not self.game_over and direction != OPPOSITE[self.direction]:
            self.next_direction = direction

    def _spawn_food(self) -> None:
        while True:
            candidate = (
                random.randint(0, self.game.width - 1),
                random.randint(0, self.game.height - 1),
            )
            if candidate not in self.snake:
                self.food = candidate
                return

    def _tick(self) -> None:
        if not self.game_over:
            self.direction = self.next_direction
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

            elif new_head in self.snake:
                self.game_over = True

            else:
                self.snake.insert(0, new_head)
                if self.food is not None and new_head == self.food:
                    self.score += 10
                    self._spawn_food()
                else:
                    self.snake.pop()

        self._render()

    def _render(self) -> None:
        self.game.clear()
        if self.food is not None:
            self.game.set(self.food[0], self.food[1], FOOD_CHAR, FOOD_COLOR)
        for segment in self.snake:
            self.game.set(segment[0], segment[1], SNAKE_CHAR, SNAKE_COLOR)
        self.game.text(0, 0, f"Score: {self.score}", SCORE_COLOR)
        if self.game_over:
            self.game.text(10, 9, "GAME OVER", GAME_OVER_COLOR)
        self.game.refresh()

    def run(self) -> None:
        self.game.start()


if __name__ == "__main__":
    SnakeGame().run()
