import numpy as np
import customtkinter
import time
import pickle as pk

customtkinter.set_default_color_theme("dark-blue")

class NumberCell:
    NUMBER_NULL = ""
    def __init__(self) -> None:
        self.possible_values = [self.NUMBER_NULL, 0, 1]
        self.statemaker = self._statecycle()
        self.state = next(self.statemaker)

    def cycle_state(self):
        self.state = next(self.statemaker)

    def _statecycle(self):
        while True:
            for state in self.possible_values:
                yield state

    def __str__(self) -> str:
        return str(self.state) if self.state is not None else '|'

    def __eq__(self, other) -> bool:
        return self.state == other.state and self.state != self.NUMBER_NULL
    
    def __bool__(self) -> bool:
        return self.state != self.NUMBER_NULL

class BPBoard:
    def __init__(self, size) -> None:
        self.step = 0
        self.size = size
        self.board = np.empty(shape=(size, size), dtype=NumberCell)
        self.fill_board()

    def fill_board(self):
        for i in range(self.size):
            for j in range(self.size):
                self.board[i, j] = NumberCell()

    def cell_value(self, i, j):
        return self.board[i, j].state

    def cycle_cell(self, i, j):
        self.board[i,j].cycle_state()

    def update_board(self):
        def is_surrounded_horizontal(row, col) -> bool:
            horizontal_possible = (0 < col < self.size-1)
            surrounded = False
            
            if horizontal_possible:
                left = self.board[row, col-1]
                right = self.board[row, col+1]
                surrounded = (
                    left == right == self.board[row, col] or 
                    left == right and not self.board[row, col]
                    )
                # surrounded = (left == right)

            return surrounded  
        
        def is_surrounded_vertical(row, col) -> bool:
            vertical_possible = (0 < row < self.size-1)
            surrounded = False

            if vertical_possible:
                above = self.board[row-1, col]
                below = self.board[row+1, col]
                surrounded = (
                    above == below == self.board[row, col] or  
                    above == below and not self.board[row, col]
                    )

            return surrounded
        
        def two_horizontal(row, col) -> bool:
            possible_left = (1 < col < self.size)
            possible_right = (-1 < col < self.size-2)
            third = False

            if possible_left:
                third = (
                    self.board[row, col-2] == self.board[row, col-1] == self.board[row, col] or \
                    self.board[row, col-2] == self.board[row, col-1] and not self.board[row, col]
                    )
                
            if possible_right:
                third = third or (
                    self.board[row, col+2] == self.board[row, col+1] == self.board[row, col] or \
                    self.board[row, col+2] == self.board[row, col+1] and not self.board[row, col]
                    )
                
            return third
        

        def two_vertical(row,col) -> bool:
            possible_down = (1 < row < self.size)
            possible_up = (-1 < row < self.size-2)
            third = False

            if possible_down:
                third = (
                    self.board[row-2,col] == self.board[row-1, col] == self.board[row, col] or \
                    self.board[row-2, col] == self.board[row-1, col] and not self.board[row, col]
                    )
                
            if possible_up:
                third = third or (
                    self.board[row+2, col] == self.board[row+1, col] == self.board[row, col] or \
                    self.board[row+2, col] == self.board[row+1, col] and not self.board[row, col]
                    )

            return third
        

        rules = (is_surrounded_horizontal, is_surrounded_vertical, two_horizontal, two_vertical)
        
        needs_flip = lambda i, j: any([rule(i, j) for rule in rules])

        for (row, col), cell in np.ndenumerate(self.board):
            if not cell:
                while needs_flip(row, col):
                    self.cycle_cell(row, col)
                if cell:
                    break

        # def count_neighbors(row, col) -> int:
        #     neighbor_cells = self.board[row-1:row+2, col-1:col+2]
        #     cell = self.board[row, col]

        #     if self.board[row, col] == self.board[row+1, col] and self.board[row-1, col].state is None:
        #         self.board[row-1, col].cycle_state()
        #         if self.board[row-1, col] == self.board[row, col]:
        #             self.board[row-1, col].cycle_state()
                
        #     num_neighbors = np.count_nonzero(neighbor_cells==self.alive)

        #     if self.board[row, col] == self.alive:
        #         num_neighbors -= 1

        #     return num_neighbors
        
        # nextboard = np.copy(self.board)

        # for (x, y), cell in np.ndenumerate(self.board[1:-1, 1:-1]):
        #     i = x + 1
        #     j = y + 1
        #     nn = count_neighbors(i,j)
        #     if cell == self.dead and nn == 3:
        #         nextboard[i, j] = self.alive

        #     elif cell == self.alive and (nn < 2 or nn > 3):
        #         nextboard[i, j] = self.dead

        # self.board = nextboard
        # self.step += 1

    def get_board_view(self):
        # output = f"{f'Generation {self.step}':^{self.size+2}0}\n"
        # ncols = len(' '.join(self.board[0]))
        displayboard = np.zeros_like(self.board, dtype=str)
        ncols = self.size * 2 + 2
        for index, cell in np.ndenumerate(self.board):
            displayboard[index] = str(cell)

        output = f"{f'Generation {self.step}':^{ncols+1}}\n"
        for row in displayboard:
            output += " ".join(row)
            output += "\n"
        
        return output
    
    def print_board(self):
        output = self.get_board_view()
        print(output)
        # print(self.board)


class Interface(customtkinter.CTk):
    def __init__(self, game: BPBoard):
        super().__init__()
        self.game = game
        self.board_path = "saved_bp_board.pk"
        self.stop = False
        framelength = 1000
        self.gamelength = 800
        self.boxsize = self.gamelength/(self.game.size)
        self.geometry(f"{framelength}x{framelength}")

        self._last_i, self._last_j = -1,-1
        self.generation_time = 0.2

        buttons = customtkinter.CTkCanvas(self, width=self.gamelength, height=self.gamelength/10, bg='black')
        buttons.pack(padx=10, pady=10)
        self.advance_button = customtkinter.CTkButton(buttons, text="Advance", command=lambda: self.evolve(1))
        self.advance_button.pack(padx=20, pady=30, side=customtkinter.LEFT)

        self.load_button = customtkinter.CTkButton(buttons, text="load", command=self.load_board)
        self.load_button.pack(padx=20, pady=30, side=customtkinter.LEFT)

        self.gamescreen = customtkinter.CTkCanvas(self, 
                                                width=self.gamelength, 
                                                height=self.gamelength)
        self.gamescreen.pack(padx=10, pady=10)

        self.button_grid = np.zeros_like(self.game.board)
        for (row, col), cell in np.ndenumerate(self.game.board):
            cell_button = customtkinter.CTkButton(self.gamescreen, text=cell.state, height=self.boxsize, width=self.boxsize, command=lambda row=row, col=col: self.flip_cell(row, col))
            cell_button.grid(row=row, column=col)
            self.button_grid[row, col] = cell_button

        self.show_board()
        
        # self.repop_button = customtkinter.CTkButton(buttons, text="Repopulate Random", command=self.randomize_board)
        # self.repop_button.pack(padx=20, pady=30, side=customtkinter.LEFT)

        self.save_button = customtkinter.CTkButton(buttons, text="save", command=self.save_board)
        self.save_button.pack(padx=20, pady=30, side=customtkinter.LEFT)
        
        self.speed_slider_box = customtkinter.CTkCanvas(self, width=self.gamelength, height=self.gamelength/10, bg='black')
        self.speed_slider_box.pack(padx=10, pady=10)

        self.speed_slider = customtkinter.CTkSlider(self.speed_slider_box, from_=0.5, to=3)
        self.speed_slider.pack(padx=10, pady=10, side=customtkinter.BOTTOM)

        self.speed_slider_name = customtkinter.CTkLabel(self.speed_slider_box, text='speed', text_color='white')
        self.speed_slider_name.pack(padx=10, pady=10)

    def save_board(self):
        with open(self.board_path, 'wb') as f:
            pk.dump(self.game, f)

    def load_board(self):
        with open(self.board_path, "rb") as f:
            self.game = pk.load(f)        
        
        self.button_grid = np.zeros_like(self.game.board)
        for (row, col), cell in np.ndenumerate(self.game.board):
            cell_button = customtkinter.CTkButton(self.gamescreen, text=cell.state, height=self.boxsize, width=self.boxsize, command=lambda row=row, col=col: self.flip_cell(row, col))
            cell_button.grid(row=row, column=col)
            self.button_grid[row, col] = cell_button

        self.show_board()
        

    def flip_cell(self, row, col):
        self.game.cycle_cell(row, col)
        # print(self.button_grid[row, col]["text"])
        # self.button_grid[row, col]["text"] = self.game.cell_value(row, col)
        # self.button_grid[row, col].configure(text = self.game.cell_value(row, col))
        self.show_board()

    def randomize_board(self):
        self.game.populate_random()
        self.show_board()

    def flip_stop(self):
        if not self.stop:
            self.stop = True
        else:
            self.stop = False

    def show_board(self):
        for (row, col), button in np.ndenumerate(self.button_grid):
            button.configure(text=self.game.cell_value(row, col))
        # for button, cell in zip(self.button_grid, self.game.board):
            # button.configure(text = cell.state)
        self.gamescreen.update()

    def evolve(self, num_steps=50):
        self.stop = False
        step = 0
        while not self.stop and step < num_steps:
            self.game.update_board()
            self.show_board()
            time.sleep(np.exp(-self.speed_slider.get()))
            step += 1


if __name__ in '__main__':
    board = BPBoard(12)
    # board.cycle_cell(4,4)
    # board.cycle_cell(4,5)
    # board.cycle_cell(4,5)
    # board.cycle_cell(4,6)
    # board.cycle_cell(5,6)
    # board.print_board()
    # board.populate_random()

    app = Interface(game=board)
    app.mainloop()