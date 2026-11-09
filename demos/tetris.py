import random

from libascii import Color, Game, draw_text
from libascii.renderers import TerminalRenderer

BOARD_W = 11
BOARD_H = 20
PANEL_W = 19
DISP_W = BOARD_W + PANEL_W + 4
DISP_H = BOARD_H + 2

PIECE_COLORS = {
    "I": Color("cyan"),
    "O": Color("yellow"),
    "T": Color("magenta"),
    "S": Color("green"),
    "Z": Color("red"),
    "J": Color("blue"),
    "L": Color("white"),
}

PIECES = {
    "I": [
        [(0, 0), (1, 0), (2, 0), (3, 0)],
        [(1, -1), (1, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, -1), (2, 0), (2, 1), (2, 2)],
    ],
    "O": [
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
        [(0, 0), (1, 0), (0, 1), (1, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}
PIECE_NAMES = ["I", "O", "T", "S", "Z", "J", "L"]


class Tetris:
    def __init__(self) -> None:
        self.renderer = TerminalRenderer(
            DISP_W,
            DISP_H,
            "Tetris",
            Color("black"),
            Color("white"),
            10,
        )
        self.game = Game(
            DISP_W,
            DISP_H,
            "Tetris",
            fps=10,
            renderer=self.renderer,
        )
        self.board: list[list[Color | None]] = [
            [None for _ in range(BOARD_W)] for _ in range(BOARD_H)
        ]
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False
        self.piece_cells: list[tuple[int, int]] = []
        self.piece_x = 0
        self.piece_y = 0
        self.piece_color: Color | None = None
        self.drop_timer = 0.0
        self._bind_keys()
        self._spawn_piece()
        self.game.on_frame(self._tick)

    def _bind_keys(self) -> None:
        self.game.bind_action("move_left", "Left")
        self.game.bind_action("move_right", "Right")
        self.game.bind_action("move_down", "Down")
        self.game.bind_action("rotate", "Up")
        self.game.bind_action("hard_drop", " ")
        self.game.bind_action("quit", "q")

    def _spawn_piece(self) -> None:
        piece_type = random.choice(PIECE_NAMES)
        self.piece_color = PIECE_COLORS[piece_type]
        self.piece_cells = list(PIECES[piece_type][0])
        self.piece_x = BOARD_W // 2 - 2
        self.piece_y = 0
        if not self._valid(self.piece_cells, self.piece_x, self.piece_y):
            self.game_over = True

    def _valid(self, cells: list[tuple[int, int]], ox: int, oy: int) -> bool:
        for cx, cy in cells:
            nx, ny = ox + cx, oy + cy
            if nx < 0 or nx >= BOARD_W or ny >= BOARD_H:
                return False
            if ny >= 0 and self.board[ny][nx] is not None:
                return False
        return True

    def _rotate(self) -> None:
        piece_type = None
        for name, color in PIECE_COLORS.items():
            if color == self.piece_color:
                piece_type = name
                break
        if piece_type is None:
            return
        rotations = PIECES[piece_type]
        current_idx = rotations.index(self.piece_cells)
        new_cells = list(rotations[(current_idx + 1) % len(rotations)])
        if self._valid(new_cells, self.piece_x, self.piece_y):
            self.piece_cells = new_cells

    def _move(self, dx: int, dy: int) -> bool:
        if self._valid(self.piece_cells, self.piece_x + dx, self.piece_y + dy):
            self.piece_x += dx
            self.piece_y += dy
            return True
        return False

    def _lock(self) -> None:
        for cx, cy in self.piece_cells:
            nx, ny = self.piece_x + cx, self.piece_y + cy
            if 0 <= nx < BOARD_W and 0 <= ny < BOARD_H:
                self.board[ny][nx] = self.piece_color
        self._clear_lines()
        self._spawn_piece()

    def _clear_lines(self) -> None:
        new_board = [row for row in self.board if any(c is None for c in row)]
        cleared = BOARD_H - len(new_board)
        if cleared > 0:
            self.lines += cleared
            self.score += cleared * cleared * 100 * self.level
            self.level = self.lines // 10 + 1
            for _ in range(cleared):
                new_board.insert(0, [None for _ in range(BOARD_W)])
        self.board = new_board

    def _hard_drop(self) -> None:
        while self._move(0, 1):
            pass
        self._lock()

    def _tick(self) -> None:
        if self.game_over:
            return

        if self.game.action_was_pressed("move_left"):
            self._move(-1, 0)
        elif self.game.action_was_pressed("move_right"):
            self._move(1, 0)
        elif self.game.action_was_pressed("move_down"):
            if not self._move(0, 1):
                self._lock()
        elif self.game.action_was_pressed("rotate"):
            self._rotate()
        elif self.game.action_was_pressed("hard_drop"):
            self._hard_drop()
        elif self.game.action_was_pressed("quit"):
            self.game_over = True
            self.game.stop()

        self.drop_timer += 1.0 / self.game.fps
        drop_interval = max(0.1, 1.0 - (self.level - 1) * 0.1)
        if self.drop_timer >= drop_interval:
            self.drop_timer = 0.0
            if not self._move(0, 1):
                self._lock()

        self._render()

    def _render(self) -> None:
        self.game.clear()

        for y in range(BOARD_H + 2):
            self.game.set(0, y, "#", Color("gray"))
            self.game.set(BOARD_W + 1, y, "#", Color("gray"))
        for x in range(BOARD_W + 2):
            self.game.set(x, 0, "#", Color("gray"))
            self.game.set(x, BOARD_H + 1, "#", Color("gray"))

        for y in range(BOARD_H):
            for x in range(BOARD_W):
                color = self.board[y][x]
                if color is not None:
                    self.game.set(x + 1, y + 1, "#", color)

        if not self.game_over:
            for cx, cy in self.piece_cells:
                nx = self.piece_x + cx + 1
                ny = self.piece_y + cy + 1
                if 0 <= nx < BOARD_W + 2 and 0 <= ny < BOARD_H + 2:
                    self.game.set(nx, ny, "#", self.piece_color)

        panel_x = BOARD_W + 4
        draw_text(
            self.game.grid,
            panel_x,
            1,
            ["TETRIS"],
            color=Color("white"),
            align_mode="left",
        )
        draw_text(
            self.game.grid,
            panel_x,
            3,
            [f"Score: {self.score}"],
            color=Color("white"),
        )
        draw_text(
            self.game.grid,
            panel_x,
            4,
            [f"Level: {self.level}"],
            color=Color("white"),
        )
        draw_text(
            self.game.grid,
            panel_x,
            5,
            [f"Lines: {self.lines}"],
            color=Color("white"),
        )
        draw_text(
            self.game.grid,
            panel_x,
            7,
            ["Controls:"],
            color=Color("white"),
        )
        draw_text(
            self.game.grid,
            panel_x,
            8,
            ["Arrows: move/rotate"],
            color=Color("white"),
        )
        draw_text(
            self.game.grid,
            panel_x,
            9,
            ["Down: soft drop"],
            color=Color("white"),
        )
        draw_text(
            self.game.grid,
            panel_x,
            10,
            ["Space: hard drop"],
            color=Color("white"),
        )
        draw_text(
            self.game.grid,
            panel_x,
            11,
            ["Q: quit"],
            color=Color("white"),
        )

        if self.game_over:
            draw_text(
                self.game.grid,
                1,
                BOARD_H // 2,
                ["GAME OVER"],
                color=Color("white"),
            )
        self.game.refresh()

    def run(self) -> None:
        self.game.start()


if __name__ == "__main__":
    Tetris().run()
