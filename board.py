import numpy as np
import piece


class BoardState:
    def __init__(self, size, values=None, evals=None, color=piece.WHITE):
        if np.all(values != None):
            self.values = np.copy(values)
        else:
            self.values = np.full((size, size), piece.EMPTY)

        self.size = size
        self.color = color
        self.last_move = None
        self.winner = 0

    def value(self, position):
        return self.values[position]

    def is_valid_position(self, position):
        i, j = position
        if not (0 <= i < self.size and 0 <= j < self.size):
            return False
        return self.values[position] == piece.EMPTY

    def legal_moves(self):
        prev_move_idxs = self.values != piece.EMPTY
        area_idxs = expand_area(self.size, prev_move_idxs)
        return np.column_stack(np.where(area_idxs == True))

    def next(self, position):
        next_state = BoardState(size=self.size, values=self.values, color=-self.color)
        next_state[position] = next_state.color
        next_state.last_move = tuple(position)
        return next_state

    def is_terminal(self):
        is_win, color, _ = self.check_five_in_a_row()
        is_full = self.is_full()
        if is_full:
            return True
        return is_win

    def check_five_in_a_row(self):
        """
        Kiểm tra 5 quân cờ liên tiếp trên bàn cờ 19x19
        Returns:
            tuple: (bool, int, list) - (Có thắng không, Người thắng (1: X, 2: O), Danh sách các ô thắng)
        """
        # Kiểm tra theo hàng ngang
        for row in range(19):
            for col in range(15):  # Chỉ cần kiểm tra đến cột 15 vì sau đó không đủ 5 ô
                cells = []
                current = self.values[row][col]
                if current == 0:  # Bỏ qua ô trống
                    continue

                is_five = True
                for i in range(5):
                    if self.values[row][col + i] != current:
                        is_five = False
                        break
                    cells.append(row * 19 + (col + i))  # Lưu vị trí ô

                if is_five:
                    self.winner = 2 if current == -1 else 1
                    return True, self.winner, cells

        # Kiểm tra theo hàng dọc
        for col in range(19):
            for row in range(15):  # Chỉ cần kiểm tra đến hàng 15
                cells = []
                current = self.values[row][col]
                if current == 0:
                    continue

                is_five = True
                for i in range(5):
                    if self.values[row + i][col] != current:
                        is_five = False
                        break
                    cells.append((row + i) * 19 + col)

                if is_five:
                    self.winner = 2 if current == -1 else 1
                    return True, self.winner, cells

        # Kiểm tra đường chéo chính (từ trái trên xuống phải dưới)
        for row in range(15):
            for col in range(15):
                cells = []
                current = self.values[row][col]
                if current == 0:
                    continue

                is_five = True
                for i in range(5):
                    if self.values[row + i][col + i] != current:
                        is_five = False
                        break
                    cells.append((row + i) * 19 + (col + i))

                if is_five:
                    self.winner = 2 if current == -1 else 1
                    return True, self.winner, cells

        # Kiểm tra đường chéo phụ (từ phải trên xuống trái dưới)
        for row in range(15):
            for col in range(4, 19):
                cells = []
                current = self.values[row][col]
                if current == 0:
                    continue

                is_five = True
                for i in range(5):
                    if self.values[row + i][col - i] != current:
                        is_five = False
                        break
                    cells.append((row + i) * 19 + (col - i))

                if is_five:
                    self.winner = 2 if current == -1 else 1
                    return True, self.winner, cells

        return False, 0, []  # Không có người thắng

    def is_full(self):
        return not np.any(self.values == piece.EMPTY)

    def check_pattern(self, pattern):
        for line in self.get_lines():
            cells = issub(line, pattern)
            if cells:
                return True, cells
        return False, None

    def get_lines(self):
        l = []

        # rows and cols
        for i in range(self.size):
            l.append(self.values[i, :])
            l.append(self.values[:, i])

        # 2 diags
        for i in range(-self.size + 5, self.size - 4):
            l.append(np.diag(self.values, k=i))
            l.append(np.diag(np.fliplr(self.values), k=i))

        for line in l:
            yield line

    def __getitem__(self, position):
        i, j = position
        return self.values[i, j]

    def __setitem__(self, position, value):
        i, j = position
        self.values[i, j] = value

    def __str__(self):
        out = " " * 3
        out += "{}\n".format(
            "".join(
                "{}{}".format((i + 1) % 10, i < 10 and " " or "'")
                for i in range(self.size)
            )
        )

        for i in range(self.size):
            out += "{}{} ".format(i + 1 < 10 and " " or "", i + 1)
            for j in range(self.size):
                out += piece.symbols[self[i, j]]
                if self.last_move and (i, j) == tuple(self.last_move):
                    out += "*"
                else:
                    out += " "
            if i == self.size - 1:
                out += ""
            else:
                out += "\n"
        return out

    def __repr__(self):
        return self.__str__()


def issub(l, subl):
    l_size = len(l)
    subl_size = len(subl)
    for i in range(l_size - subl_size + 1):
        curr = l[i : i + subl_size]
        if (curr == subl).all():
            # Trả về vị trí của 5 quân thắng
            return [(i + j) for j in range(subl_size)]
    return None


def expand_area(size, idxs):
    area_idxs = np.copy(idxs)
    for i in range(size):
        for j in range(size):
            if not idxs[i, j]:
                continue
            for direction in ((1, 0), (0, 1), (1, 1), (1, -1)):
                di, dj = direction
                for side in (1, -1):
                    ni = i + di * side
                    nj = j + dj * side
                    if not is_valid_position(size, (ni, nj)):
                        continue
                    area_idxs[ni, nj] = True
    return np.bitwise_xor(area_idxs, idxs)


def is_valid_position(board_size, position):
    i, j = position
    return i >= 0 and i < board_size and j >= 0 and j < board_size
