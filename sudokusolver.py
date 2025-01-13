import collections

def sudoku_cells():
    return [(i, j) for i in range(9) for j in range(9)]


def sudoku_arcs():
    arcs = []
    for r in range(9):
        for c in range(9):
            cell = (r, c)
            # row neighbors (same row, different column)
            for col in range(9):
                if col != c:
                    arcs.append((cell, (r, col)))
            # column neighbors (same column, different row)
            for row in range(9):
                if row != r:
                    arcs.append((cell, (row, c)))
            # box neighbors (same 3x3 box, different position)
            subgrid_row_start = (r // 3) * 3
            subgrid_col_start = (c // 3) * 3
            for i in range(subgrid_row_start, subgrid_row_start + 3):
                for j in range(subgrid_col_start, subgrid_col_start + 3):
                    if ((i, j) != cell and
                        (i, j) not in [(r, col) for col in range(9)] and
                            (i, j) not in [(row, c) for row in range(9)]):
                        arcs.append((cell, (i, j)))
    return arcs


def read_board(path):
    with open(path, 'r') as file:
        # separate items in line as tuple
        board = [line.strip().split() for line in file.readlines()]
    # convert to ints and * tuples
    converted_board = []
    for row in board:
        converted_row = []
        for char in row[0]:
            if char.isdigit():
                converted_row.append(int(char))
            else:
                converted_row.append(char)
        converted_board.append(tuple(converted_row))
    tuple_board = tuple(converted_board)
    # turn into dictionary
    final_board = {}
    for row in range(9):
        for col in range(9):
            if tuple_board[row][col] != "*":
                final_board[(row, col)] = {tuple_board[row][col]}
            else:
                final_board[(row, col)] = set(range(1, 10))
    return final_board


class Sudoku(object):

    CELLS = sudoku_cells()
    ARCS = sudoku_arcs()

    def __init__(self, board):
        self.board = board

    def get_board(self):
        return self.board

    def get_values(self, cell):
        return self.board[cell]
    # removes any value in the set of possibilities for cell1 for which
    # there are no values in the
    # set of possibilities for cell2 satisfying the corresponding inequality
    # constraint (which we have represented as an arc)

    def remove_inconsistent_values(self, cell1, cell2):
        removed = False
        if (cell1, cell2) in self.ARCS:
            if len(self.board[cell2]) == 1 and list(self.board[cell2])[0] in \
                    self.board[cell1]:
                self.board[cell1].remove(list(self.board[cell2])[0])
                removed = True
        return removed

    def infer_ac3(self):
        queue = collections.deque(self.ARCS)
        while queue:
            (x, y) = queue.popleft()
            if self.remove_inconsistent_values(x, y):
                if len(self.board[x]) == 0:
                    return False
                for z in self.CELLS:
                    if (z, x) in self.ARCS and z != y:
                        queue.append((z, x))
        return True

    def infer_improved(self, visited_states=None):
        if visited_states is None:
            visited_states = set()
        self.infer_ac3()
        # check if board is solved
        if all(len(self.board[cell]) == 1 for cell in self.CELLS):
            return True
        # backtrack
        if any(len(self.board[cell]) == 0 for cell in self.CELLS):
            return False
        # create state
        state = tuple(
            (cell, next(iter(self.board[cell])) if len(self.board[cell])
                == 1 else tuple(sorted(self.board[cell])))
            for cell in self.CELLS
        )
        if state in visited_states:
            return False
        visited_states.add(state)

        # find cells with more than one value
        candidates = [c for c in self.CELLS if len(self.board[c]) > 1]
        if not candidates:
            return False
        # cell with fewest possibilities
        cell = min(candidates, key=lambda c: len(self.board[c]))
        # try possibilities
        possible_values = self.board[cell].copy()
        for value in possible_values:
            backup = {c: self.board[c].copy() for c in self.CELLS}
            self.board[cell] = {value}
            if self.infer_improved(visited_states):
                return True
            # backtrack to backup
            self.board = backup
        return False

    def infer_with_guessing(self, visited_states=None):
        if visited_states is None:
            visited_states = set()
        self.infer_ac3()
        # check if board is solved
        if all(len(self.board[cell]) == 1 for cell in self.CELLS):
            return True
        # backtrack
        if any(len(self.board[cell]) == 0 for cell in self.CELLS):
            return False
        # create state
        state = tuple(
            (cell, next(iter(self.board[cell])) if len(self.board[cell])
                == 1 else tuple(sorted(self.board[cell])))
            for cell in self.CELLS
        )
        if state in visited_states:
            return False

        visited_states.add(state)

        # find cells with more than one value
        candidates = [c for c in self.CELLS if len(self.board[c]) > 1]
        if not candidates:
            return False
        # cell with fewest possibilities
        cell = min(candidates, key=lambda c: len(self.board[c]))

        # try possibilities
        possible_values = self.board[cell].copy()
        for value in possible_values:
            backup = {c: self.board[c].copy() for c in self.CELLS}

            self.board[cell] = {value}
            if self.infer_improved(visited_states):
                return True
            # backtrack to backup
            self.board = backup

        return False