import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import copy
from sudokusolver import Sudoku, read_board

class SudokuGame:
    def __init__(self, board_string):
        self.start_puzzle = [[0 for _ in range(9)] for _ in range(9)]
        self.puzzle = [[0 for _ in range(9)] for _ in range(9)]
        self.load_puzzle(board_string)

    def start(self):
        """Reset the puzzle to its initial state"""
        self.puzzle = [row[:] for row in self.start_puzzle]

    def load_puzzle(self, board_string):
        """Load a puzzle from a string of 81 digits"""
        if len(board_string) != 81:
            raise ValueError("Board string must be 81 characters")
            
        for i in range(9):
            for j in range(9):
                val = int(board_string[i * 9 + j])
                self.start_puzzle[i][j] = val
        self.start()

    def check_valid(self):
        """Check if the current solution is valid"""
        # Check rows
        for row in self.puzzle:
            if not self._check_group(row):
                return False
                
        # Check columns
        for j in range(9):
            column = [self.puzzle[i][j] for i in range(9)]
            if not self._check_group(column):
                return False
                
        # Check 3x3 boxes
        for box_i in range(3):
            for box_j in range(3):
                box = []
                for i in range(3):
                    for j in range(3):
                        box.append(self.puzzle[box_i * 3 + i][box_j * 3 + j])
                if not self._check_group(box):
                    return False
                    
        return True

    def _check_group(self, group):
        """Check if a group (row/column/box) contains valid numbers"""
        # Remove zeros (empty cells)
        numbers = [n for n in group if n != 0]
        # Check if there are any duplicates
        return len(numbers) == len(set(numbers))

class ModernSudokuUI(tk.Frame):
    def __init__(self, master, game):
        self.game = game
        self.master = master
        super().__init__(master)
        
        # Configure color scheme
        self.colors = {
            'bg': '#f0f0f0',
            'button_bg': '#4a90e2',
            'button_fg': 'black',
            'grid_lines': '#2c3e50',
            'subgrid_lines': '#34495e',
            'original_numbers': '#2c3e50',
            'solved_numbers': '#27ae60',
            'victory_text': '#e67e22',
            'entry_bg': 'white'
        }
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('Modern.TButton',
                           padding=6,
                           relief="flat",
                           background=self.colors['button_bg'],
                           foreground=self.colors['button_fg'])
        
        self.master.title("Modern Sudoku")
        self.master.configure(bg=self.colors['bg'])
        self.configure(bg=self.colors['bg'])
        self.setup_ui()

    def setup_ui(self):
        self.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create main containers
        self.left_frame = tk.Frame(self, bg=self.colors['bg'])
        self.right_frame = tk.Frame(self, bg=self.colors['bg'])
        
        self.left_frame.pack(side='left', fill='both', expand=True, padx=10)
        self.right_frame.pack(side='right', fill='y', padx=10)
        
        # Setup canvas with modern styling
        self.canvas = tk.Canvas(
            self.left_frame,
            width=470,
            height=470,
            bg='white',
            highlightthickness=1,
            highlightbackground=self.colors['grid_lines']
        )
        self.canvas.pack(padx=10, pady=10)
        
        # Create control panel
        self.setup_control_panel()
        
        # Draw initial board
        self.draw_grid()
        self.draw_puzzle()

    def setup_control_panel(self):
        # Control panel title
        title_label = tk.Label(
            self.right_frame,
            text="Controls",
            font=('Helvetica', 16, 'bold'),
            bg=self.colors['bg'],
            fg=self.colors['grid_lines']
        )
        title_label.pack(pady=(0, 20))
        
        # Buttons with modern styling
        buttons = [
            ("Clear Solutions", self.clear_click),
            ("Solve (AC3)", self.solve_click_infer_ac3),
            ("Solve (Improved)", self.solve_click_infer_improved),
            ("Solve (with Guessing)", self.solve_click_infer_with_guessing)
        ]
        
        for text, command in buttons:
            btn = tk.Button(
                self.right_frame,
                text=text,
                command=command,
                bg=self.colors['button_bg'],
                fg=self.colors['button_fg'],
                font=('Helvetica', 10),
                relief='flat',
                padx=10,
                pady=5,
                width=20
            )
            btn.pack(pady=5)
            
            # Add hover effect
            btn.bind('<Enter>', lambda e, b=btn: b.configure(bg='#357abd'))
            btn.bind('<Leave>', lambda e, b=btn: b.configure(bg=self.colors['button_bg']))
        
        # Puzzle input section
        input_frame = tk.Frame(self.right_frame, bg=self.colors['bg'])
        input_frame.pack(pady=20)
        
        tk.Label(
            input_frame,
            text="Enter Puzzle:",
            font=('Helvetica', 10),
            bg=self.colors['bg'],
            fg=self.colors['grid_lines']
        ).pack()
        
        self.puzzle_entry = tk.Entry(
            input_frame,
            width=25,
            font=('Helvetica', 10),
            bg=self.colors['entry_bg']
        )
        self.puzzle_entry.pack(pady=5)
        
        tk.Button(
            input_frame,
            text="Reset Puzzle",
            command=self.get_puzzle,
            bg=self.colors['button_bg'],
            fg=self.colors['button_fg'],
            font=('Helvetica', 10),
            relief='flat',
            padx=10,
            pady=5
        ).pack()

    def draw_grid(self):
        self.canvas.delete("grid")
        for i in range(10):
            width = 2 if i % 3 == 0 else 1
            color = self.colors['subgrid_lines'] if i % 3 == 0 else self.colors['grid_lines']
            
            # Vertical lines
            self.canvas.create_line(
                50 * i + 20, 20,
                50 * i + 20, 470,
                width=width,
                fill=color,
                tags="grid"
            )
            
            # Horizontal lines
            self.canvas.create_line(
                20, 50 * i + 20,
                470, 50 * i + 20,
                width=width,
                fill=color,
                tags="grid"
            )

    def draw_puzzle(self):
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                answer = self.game.puzzle[i][j]
                if answer != 0:
                    x = 20 + j * 50 + 25
                    y = 20 + i * 50 + 25
                    original = self.game.start_puzzle[i][j]
                    color = self.colors['original_numbers'] if answer == original else self.colors['solved_numbers']
                    
                    self.canvas.create_text(
                        x, y,
                        text=answer,
                        tags="numbers",
                        fill=color,
                        font=("Helvetica", 16)
                    )

    def draw_victory(self):
        self.canvas.delete("winner")
        x = y = 245
        text = "Victory!" if self.game.check_valid() else "Invalid Solution"
        color = self.colors['victory_text']
        
        # Create a semi-transparent background
        self.canvas.create_rectangle(
            x-100, y-30, x+100, y+30,
            fill='white',
            tags="winner"
        )
        
        self.canvas.create_text(
            x, y,
            text=text,
            tags="winner",
            fill=color,
            font=("Helvetica", 24, "bold")
        )

    # Keep all the original method implementations for game logic
    def list2dict(self):
        board_dict = {}
        for i in range(9):
            for j in range(9):
                value = self.game.start_puzzle[i][j]
                if value == 0:
                    board_dict[(i, j)] = set(range(1, 10))
                else:
                    board_dict[(i, j)] = {value}
        return board_dict

    def dict2list(self, board_dict):
        for key, value in board_dict.items():
            if len(value) == 1:
                self.game.puzzle[key[0]][key[1]] = list(value)[0]
            else:
                self.game.puzzle[key[0]][key[1]] = list(value)

    def solve_click_infer_ac3(self):
        board_dict = self.list2dict()
        SUDOKU = Sudoku(board_dict)
        SUDOKU.infer_ac3()
        self.dict2list(SUDOKU.board)
        self.draw_puzzle()
        self.draw_victory()

    def solve_click_infer_improved(self):
        board_dict = self.list2dict()
        SUDOKU = Sudoku(board_dict)
        SUDOKU.infer_improved()
        self.dict2list(SUDOKU.board)
        self.draw_puzzle()
        self.draw_victory()

    def solve_click_infer_with_guessing(self):
        board_dict = self.list2dict()
        SUDOKU = Sudoku(board_dict)
        SUDOKU.infer_with_guessing()
        self.dict2list(SUDOKU.board)
        self.draw_puzzle()
        self.draw_victory()

    def clear_click(self):
        self.game.start()
        self.canvas.delete("winner")
        self.draw_puzzle()

    def get_puzzle(self):
        board_string = self.puzzle_entry.get()
        
        if not board_string:
            messagebox.showwarning("Input Error", "Please enter a puzzle string")
            return
            
        if board_string.endswith(".txt"):
            try:
                board_string = read_board(board_string)
            except FileNotFoundError:
                messagebox.showerror("Error", "Invalid file path")
                return
            except IsADirectoryError:
                messagebox.showerror("Error", "Path is a directory")
                return

        elif len(board_string.split("\n")) > 1:
            board_list = board_string.split("\n")
            board_string_new = "".join(board_list)
            board_string = ""
            for char in board_string_new:
                if char == "*":
                    board_string += "0"
                else:
                    board_string += char

        if len(board_string) != 81:
            messagebox.showerror("Error", "Invalid puzzle length")
            return
            
        self.game = SudokuGame(board_string)
        self.game.start()
        self.draw_puzzle()

if __name__ == "__main__":
    game = SudokuGame("004300209005009001070060043006002087190007400050083000600000105003508690042910300")
    game.start()
    root = tk.Tk()
    root.title("Modern Sudoku")
    
    # Set window size and position it in the center of the screen
    window_width = 800
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    center_x = int(screen_width/2 - window_width/2)
    center_y = int(screen_height/2 - window_height/2)
    
    root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
    
    # Set minimum window size
    root.minsize(700, 500)
    
    app = ModernSudokuUI(root, game)
    root.mainloop()