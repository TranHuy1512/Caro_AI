import piece
import numpy as np
from board import BoardState
from ai import get_best_move


class GameRunner:
    def __init__(self, size=19, depth=2):
        self.size = size
        self.depth = depth
        self.finished = False
        self.restart()

    def restart(self, player_index=1):
        self.is_max_state = True if player_index == 1 else False
        self.state = BoardState(self.size, color=piece.BLACK)
        self.ai_color = piece.WHITE

    def play(self, i, j):
        position = (i, j)
        if self.state.color != piece.BLACK:
            return False
        if not self.state.is_valid_position(position):
            return False
        self.state = self.state.next(position)
        is_win, color, win_cells = self.state.check_five_in_a_row()
        self.finished = is_win or self.state.is_full()
        if is_win:
            self.state.win_cells = win_cells
        return True

    def aiplay(self):
        if self.state.color != piece.WHITE:
            return False, None
        move, value = get_best_move(self.state, self.depth, self.is_max_state)
        self.state = self.state.next(move)
        is_win, color, win_cells = self.state.check_five_in_a_row()
        self.finished = is_win or self.state.is_full()
        if is_win:
            self.state.win_cells = win_cells
        return True, move

    def get_status(self):
        board = self.state.values
        return {
            "board": board.tolist(),
            "next": -self.state.color,
            "finished": self.finished,
            "winner": self.state.winner,
            # 'debug_board': self.state.__str__()
        }
