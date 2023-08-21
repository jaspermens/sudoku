import numpy as np

from sudoku_board import SudokuBoard


class SudokuSolver:
    def __init__(self) -> None:
        ...

    def solve_step(self, sudoku: SudokuBoard):
        for (i, j), value in np.ndenumerate(sudoku.board[0, :, :]):
            if value > 0:
                continue
            possibilities = sudoku.board[1:10, i, j]
            num_possibilities = sum(possibilities)
            if num_possibilities == 1:
                print(f"SIMPLE: cell {(i,j)}, value {np.where(possibilities)}+1")
                sudoku.set_cell(i, j, np.where(possibilities)[0]+1)
                return
            
        for n in range(1, sudoku.sidelength+1):
            layer = sudoku.board[n, :, :]
            for i, row in enumerate(layer):
                possible_places = np.where(row)[0]
                if len(possible_places) == 1:
                    print(f"ROW: cell {(i,possible_places[0])}, value {n}")
                    sudoku.set_cell(i, possible_places[0], n)
                    return
                
            for j, col in enumerate(layer.T):
                possible_places = np.where(col)[0]
                if len(possible_places) == 1:
                    print(f"COL: cell {(possible_places[0], j)}, value {n}")
                    sudoku.set_cell(possible_places[0], j, n)
                    return
            
        print("failed to find a next step :/")