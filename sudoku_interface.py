import numpy as np
import customtkinter
from sudoku_board import SudokuBoard
from simple_solver import SudokuSolver

customtkinter.set_default_color_theme("dark-blue")
customtkinter.DrawEngine.preferred_drawing_method = "polygon_shapes"

# TODO: 
# - pipe print statements from the board to a text box in the interface (sexy)
# - highlight selected cell?
# - grid lines
# - make main board prettier in general bc damn

class Interface(customtkinter.CTk):
    def __init__(self, sudoku: SudokuBoard, solver: SudokuSolver) -> None:
        super().__init__()
        self.game = sudoku
        self.solver = solver
        
        framelength = 1200
        self.gamelength = 800
        self.boxsize = self.gamelength/(self.game.sidelength)
        self.geometry(f"{framelength}x{framelength}")

        buttons = customtkinter.CTkFrame(self, 
                                          width=self.gamelength, 
                                          height=self.gamelength/10, 
                                        #   bg_color='grey30',
                                          
                                          )
        buttons.pack(padx=20, pady=30)

        save_button = customtkinter.CTkButton(buttons, 
                                              text="save", 
                                              command=self.save_game, 
                                            #   width=500,
                                            width=150, height=50,
                                            font=("roman", 25),
                                            #   fg_color='white',
                                            #   bg_color='green',
                                            #   corner_radius=50, 
                                            #   border_width=10,
                                            #   border_color='grey',
                                            #   border_spacing=50,
                                            #   height=50

                                              )
        save_button.pack(
            padx=20, 
            pady=20, 
            side=customtkinter.LEFT)
        
        load_button = customtkinter.CTkButton(buttons, 
                                            text="load", 
                                            command=self.load_game,
                                            width=150, height=50,
                                            font=("roman", 25),
                                            )
        
        load_button.pack(padx=20, pady=20, side=customtkinter.LEFT)

        solve_button = customtkinter.CTkButton(buttons, 
                                               text="solve step", 
                                               command=self.solve_step,
                                               width=150, height=50,
                                               font=("roman", 25),
                                               )
        solve_button.pack(padx=20, pady=20, side=customtkinter.LEFT)

   
        # numbers tray stuff:
        segment_values = ["clear", *range(1,10)]
        # segment_values = range(10)

        # selected_segment = customtkinter.StringVar(value="clear")
        # selected_segment = "clear"
        self.selected_number = 0
        segments = customtkinter.CTkSegmentedButton(self, values=segment_values,
                                                        command=self.select_number,
                                                        corner_radius=10,
                                                        font=("Arial", 25),
                                                        # border_width=20,
                                                        width=self.gamelength//10,
                                                        height = self.gamelength//10,
                                                        # fg_color='black',
                                                        # variable=segment_to_num[selected_segment],
                                                        )
        segments.pack(padx=20, pady=10, side=customtkinter.TOP)
        segments.set('clear')

        # game grid itself:
        self.gamescreen = customtkinter.CTkFrame(self, width=self.gamelength, height=self.gamelength)
        self.gamescreen.pack(padx=10, pady=10)

        self.button_grid = np.zeros_like(self.game.board[0, :, :], dtype=customtkinter.CTkButton)
        for (row, col), cell_value in np.ndenumerate(self.game.board[0, :, :]):
            if cell_value == 0:
                cell_value = ' '
            cell_button = customtkinter.CTkButton(self.gamescreen, 
                                                  text=cell_value, 
                                                  font=("Arial", 30), 
                                                  height=self.boxsize, 
                                                  width=self.boxsize, 
                                                  command=lambda row=row, col=col: self.set_cell_selected(row, col),
                                                  fg_color='#194168' if self.game.board[10, row, col] % 2 == 0 else '#1D518B')
            cell_button.grid(row=row, column=col)
            self.button_grid[row, col] = cell_button

        self.show_board()
    
        self.text_box = customtkinter.CTkTextbox(self, 
                                            width=self.gamelength, 
                                            height=self.gamelength/10,
                                            font=("roman", 15))
        self.text_box.pack(padx=20, pady=20, side=customtkinter.BOTTOM)


    def select_number(self, i):
        if i == 'clear':
            i = 0
        self.selected_number = i
        self.show_board()

        # all_i_cells = self.game.board[0, :, :] == i
        # for button in self.button_grid[all_i_cells]:
            # button.configure(text_color='black') 

    def cell_value(self, row: int, col: int) -> int:
        """ quick short-hand method for fetching the sudoku value at a certain row and column index """ 
        return self.game.board[0, row, col]
        
    def flip_cell(self, row: int, col: int) -> None:
        """ deprecated. method that flips through values (dumb)"""
        current_value = self.cell_value(row, col)
        next_value = (current_value + 1) % self.game.sidelength
        self.game.set_cell(row, col, next_value)
        self.show_board()

    def set_cell_selected(self, row: int, col: int) -> None:
        if self.selected_number is None:
            return
        self.game.set_cell(row, col, self.selected_number)
        self.show_board()

    def show_board(self) -> None:
        """ shows/updates the board interface to reflect any changes """
        for (row, col), button in np.ndenumerate(self.button_grid):
            cell_value = self.cell_value(row, col)
            if cell_value == 0:
                button_text = " "
            else:
                button_text = str(cell_value)

            button.configure(text=button_text, 
                             text_color="orange" if cell_value == self.selected_number else "white",
                            #  fg_color="blue" if self.game.board[self.selected_number, row, col] else "darkblue",
                            #  state="enabled" if self.game.board[self.selected_number, row, col] else "disabled",
                             )

        self.gamescreen.update()
    
    def save_game(self):
        self.game.save_board()
        self.text_box.insert("0.0", f"Board saved to {self.game.board_file}\n")
        # self.show_board()

    def load_game(self):
        self.game.load_board()
        self.text_box.insert("0.0", f"Board loaded from {self.game.board_file}\n")
        self.show_board()

    def solve_step(self) -> None:
        if not self.solver.solve_step(sudoku=self.game):
            self.text_box.insert("0.0", "Solver too dumb :/\n")
        else:
            self.show_board()

if __name__ in '__main__':
    solver =SudokuSolver()
    sudoku = SudokuBoard()

    app = Interface(sudoku=sudoku, solver=solver)
    app.mainloop()