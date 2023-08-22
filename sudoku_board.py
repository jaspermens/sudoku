import numpy as np
import pickle as pk

class SudokuBoard:
    def __init__(self) -> None:
        self.board_file = "saved_board.pk"
        self.sidelength = 9  # standard sudoku size
        n_layers = 11   # front-facing + 9x "can-be" + block membership
        self.board = np.ones((n_layers, self.sidelength, self.sidelength), dtype=int)
        
        self.board[0, :, :] = 0 # front face is empty for now
        
        # last layer contains 3x3 cluster membership
        cluster = 1
        for i in range(3):
            for j in range(3):
                self.board[10, 3*i:3*(i+1), 3*j:3*(j+1)] = cluster
                cluster += 1
                

    def cluster_slice_of(self, i: int, j: int) -> np.array:    
        """ Little helper method for easier selection of the 3x3 cluster"""
        return (self.board[10, :, :] == self.board[10, i, j])
    

    def set_cell(self, i: int, j: int, value: int) -> None:
        """ Sets the value of a cell in the sudoku and updates the 'can-be' portion of the board accordingly"""
        if value == 0 and self.board[0, i, j] > 0:
            print(f"clearing cell! {i=} {j=}")
            self.board[0, i, j] = 0
            self.recompute_possibilities()
            return
            
        if self.board[0, i, j]:
            print("Cell is already filled!")
            return
        
        if not self.is_valid(i, j, value):
            print("Invalid move! Cringe!")
            return
        
        self.board[0, i, j] = value
        self.board[1:10, i, j] = False
        self.board[value, :, j] = False
        self.board[value, i, :] = False
        self.board[value, self.cluster_slice_of(i,j)] = False

    def recompute_possibilities(self) -> None:
        self.board[1:10, :, :] = True 
        for (i,j), value in np.ndenumerate(self.board[0,:,:]):
            if value == 0:
                continue
            self.board[1:10, i, j] = False
            self.board[value, :, j] = False
            self.board[value, i, :] = False
            self.board[value, self.cluster_slice_of(i,j)] = False

    def is_valid(self, i: int, j: int, value: int) -> bool:
        """ Returns False if the move is not allowed given the rest of the board"""
        return self.board[value, i, j] == True
    
    def __str__(self) -> str:
        return str(self.board)#.replace('0', "-")
    
    def save_board(self) -> None:
        with open(self.board_file, 'wb') as f:
            pk.dump(self.board, f)
    
    def load_board(self) -> None:
        with open(self.board_file, 'rb') as f: 
            self.board = pk.load(f)

if __name__ == "__main__":
    board = SudokuBoard(9)
    print(board)
    board.set_cell(1,1, 4)
    print(board)