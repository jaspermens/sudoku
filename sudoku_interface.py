import numpy as np
import customtkinter
from sudoku_board import SudokuBoard

customtkinter.set_default_color_theme("dark-blue")

# TODO: 
# - cell value selection (drag & drop or pick from menu- either way extra bit of canvas     OR: numpad)
# - pipe print statements from the board to a text box in the interface (sexy)
# - highlight selected cell?

class Interface(customtkinter.CTk):
    def __init__(self, sudoku: SudokuBoard) -> None:
        super().__init__()
        self.game = sudoku
        
        framelength = 1000
        self.gamelength = 800
        self.boxsize = self.gamelength/(self.game.sidelength)
        self.geometry(f"{framelength}x{framelength}")

        buttons = customtkinter.CTkCanvas(self, width=self.gamelength, height=self.gamelength/10, bg='black')
        buttons.pack(padx=10, pady=10)

        self.save_button = customtkinter.CTkButton(buttons, text="save", command=self.game.save_board)
        self.save_button.pack(padx=20, pady=30, side=customtkinter.LEFT)
        
        self.load_button = customtkinter.CTkButton(buttons, text="load", command=self.game.load_board)
        self.load_button.pack(padx=20, pady=30, side=customtkinter.LEFT)

        self.gamescreen = customtkinter.CTkCanvas(self, 
                                                width=self.gamelength, 
                                                height=self.gamelength)
        self.gamescreen.pack(padx=10, pady=10)

        self.button_grid = np.zeros_like(self.game.board[0, :, :], dtype=customtkinter.CTkButton)
        for (row, col), cell_value in np.ndenumerate(self.game.board[0, :, :]):
            if cell_value == 0:
                cell_value = ' '
            cell_button = customtkinter.CTkButton(self.gamescreen, text=cell_value, height=self.boxsize, width=self.boxsize, command=lambda row=row, col=col: self.flip_cell(row, col))
            cell_button.grid(row=row, column=col)
            self.button_grid[row, col] = cell_button

        self.show_board()

    def cell_value(self, row: int, col: int) -> int:
        """ quick short-hand method for fetching the sudoku value at a certain row and column index """ 
        return self.game.board[0, row, col]
        
    def flip_cell(self, row: int, col: int) -> None:
        """ deprecated. method that flips through values (dumb)"""
        current_value = self.cell_value(row, col)
        next_value = (current_value + 1) % self.game.sidelength
        self.game.set_cell(row, col, next_value)
        self.show_board()

    def show_board(self) -> None:
        """ shows/updates the board interface to reflect any changes """
        for (row, col), button in np.ndenumerate(self.button_grid):
            cell_value = self.cell_value(row, col)
            if cell_value == 0:
                button_text = " "
            else:
                button_text = str(cell_value)

            button.configure(text=button_text)

        self.gamescreen.update()


if __name__ in '__main__':
    sudoku = SudokuBoard()

    app = Interface(sudoku=sudoku)
    app.mainloop()