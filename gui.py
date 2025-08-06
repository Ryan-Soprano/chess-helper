import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import chess
from game_tracker import GameTracker
from engine import ChessEngine
from typing import Optional, Tuple
import os

class ChessGUI:
    """GUI interface for the chess helper app using tkinter."""
    
    def __init__(self, stockfish_path: Optional[str] = None):
        self.root = tk.Tk()
        self.root.title("Chess Helper")
        self.root.geometry("800x600")
        
        # Initialize game components
        self.game = GameTracker()
        self.engine = ChessEngine(stockfish_path)
        
        # GUI state
        self.selected_square = None
        self.square_size = 50
        self.board_canvas = None
        self.analysis_enabled = True
        self.player_color = None  # Will be set by color selection dialog
        
        # Chess piece symbols (Unicode) - High quality, scalable pieces
        self.piece_symbols = {
            'P': '♙', 'R': '♖', 'N': '♘', 'B': '♗', 'Q': '♕', 'K': '♔',  # White pieces
            'p': '♟', 'r': '♜', 'n': '♞', 'b': '♝', 'q': '♛', 'k': '♚'   # Black pieces
        }
        
        # Show color selection dialog first
        self.show_color_selection_dialog()
        
        self.setup_gui()
        self.update_display()
    
    def show_color_selection_dialog(self):
        """Show dialog to select player color."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Choose Your Color")
        dialog.geometry("320x240")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (320 // 2)
        y = (dialog.winfo_screenheight() // 2) - (240 // 2)
        dialog.geometry(f"320x240+{x}+{y}")
        
        # Main frame
        main_frame = ttk.Frame(dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Select your color for this game:", 
                               font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Color selection variable
        color_var = tk.StringVar(value="white")
        
        # White option
        white_frame = ttk.Frame(main_frame)
        white_frame.pack(fill=tk.X, pady=5)
        white_radio = ttk.Radiobutton(white_frame, text="White (I move first)", 
                                     variable=color_var, value="white")
        white_radio.pack(side=tk.LEFT)
        white_symbol = ttk.Label(white_frame, text="♔", font=('Arial', 16))
        white_symbol.pack(side=tk.RIGHT)
        
        # Black option
        black_frame = ttk.Frame(main_frame)
        black_frame.pack(fill=tk.X, pady=5)
        black_radio = ttk.Radiobutton(black_frame, text="Black (Opponent moves first)", 
                                     variable=color_var, value="black")
        black_radio.pack(side=tk.LEFT)
        black_symbol = ttk.Label(black_frame, text="♚", font=('Arial', 16))
        black_symbol.pack(side=tk.RIGHT)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        def on_confirm():
            self.player_color = color_var.get()
            dialog.destroy()
        
        def on_dialog_close():
            # If user closes dialog without selecting, exit the app
            self.root.quit()
            self.root.destroy()
        
        # Handle window close event (X button)
        dialog.protocol("WM_DELETE_WINDOW", on_dialog_close)
        
        confirm_button = ttk.Button(button_frame, text="Start Game", command=on_confirm)
        confirm_button.pack(side=tk.RIGHT)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        # If player_color is still None after dialog closes, user clicked X
        if self.player_color is None:
            self.root.quit()
            self.root.destroy()
    
    def setup_gui(self):
        """Set up the GUI layout."""
        # Create main container with grid for better responsiveness
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=2)  # Board gets more space
        self.root.grid_columnconfigure(1, weight=1)  # Right panel gets proportional space
        
        # Create main frames using grid instead of pack
        left_frame = ttk.Frame(self.root)
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        
        # Right frame with minimum width constraint
        right_frame = ttk.Frame(self.root)
        right_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        right_frame.grid_propagate(False)  # Don't let children control frame size
        
        # Set minimum width for right panel
        self.root.update_idletasks()
        right_frame.configure(width=300)
        
        # Chess board
        self.setup_chess_board(left_frame)
        
        # Control panel
        self.setup_control_panel(right_frame)
    
    def setup_chess_board(self, parent):
        """Set up the chess board canvas."""
        self.board_frame = ttk.LabelFrame(parent, text="Chess Board")
        self.board_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas for the chess board - will be resized dynamically
        self.board_canvas = tk.Canvas(
            self.board_frame, 
            bg='white',
            highlightthickness=0
        )
        self.board_canvas.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Bind resize event to update board size
        self.board_canvas.bind('<Configure>', self.on_canvas_resize)
        
        # Bind mouse events
        self.board_canvas.bind("<Button-1>", self.on_square_click)
        
        # Manual move input
        input_frame = ttk.Frame(self.board_frame)
        input_frame.pack(pady=10)
        
        ttk.Label(input_frame, text="Manual Move:").pack(side=tk.LEFT)
        self.move_entry = ttk.Entry(input_frame, width=10)
        self.move_entry.pack(side=tk.LEFT, padx=5)
        self.move_entry.bind("<Return>", self.on_manual_move)
        
        ttk.Button(input_frame, text="Make Move", command=self.on_manual_move).pack(side=tk.LEFT, padx=5)
    
    def setup_control_panel(self, parent):
        """Set up the control panel."""
        # Analysis panel
        analysis_frame = ttk.LabelFrame(parent, text="Engine Analysis")
        analysis_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # Analysis toggle
        self.analysis_var = tk.BooleanVar(value=True)
        analysis_check = ttk.Checkbutton(
            analysis_frame, 
            text="Enable Analysis", 
            variable=self.analysis_var,
            command=self.toggle_analysis
        )
        analysis_check.pack(pady=5)
        
        self.analysis_text = tk.Text(analysis_frame, width=25, state=tk.DISABLED, wrap=tk.WORD)
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Move history
        history_frame = ttk.LabelFrame(parent, text="Move History")
        history_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        
        # History text with scrollbar
        history_scroll_frame = ttk.Frame(history_frame)
        history_scroll_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.history_text = tk.Text(history_scroll_frame, width=25, state=tk.DISABLED, wrap=tk.WORD)
        history_scrollbar = ttk.Scrollbar(history_scroll_frame, orient=tk.VERTICAL, command=self.history_text.yview)
        self.history_text.configure(yscrollcommand=history_scrollbar.set)
        
        self.history_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Control buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Undo Move", command=self.undo_move).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="New Game", command=self.new_game).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Save PGN", command=self.save_pgn).pack(fill=tk.X, pady=2)
        ttk.Button(button_frame, text="Load PGN", command=self.load_pgn).pack(fill=tk.X, pady=2)
    
    def on_canvas_resize(self, event):
        """Handle canvas resize events to update board size."""
        if hasattr(self, '_last_canvas_size'):
            if (event.width, event.height) == self._last_canvas_size:
                return
        
        self._last_canvas_size = (event.width, event.height)
        
        # Calculate new square size based on available space
        # Use the smaller dimension to ensure the board fits
        available_size = min(event.width - 20, event.height - 20)  # Leave some padding
        self.square_size = max(30, available_size // 8)  # Minimum 30px squares
        
        # Redraw the board with new size
        self.draw_board()
    
    def draw_board(self):
        """Draw the chess board and pieces."""
        self.board_canvas.delete("all")
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                x1 = col * self.square_size
                y1 = row * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                
                # Determine square color
                is_light = (row + col) % 2 == 0
                color = "#F0D9B5" if is_light else "#B58863"
                
                # Convert to chess coordinates based on player orientation
                # User's pieces should always be at the bottom
                if self.player_color == "white":
                    square = chess.square(col, 7 - row)  # White at bottom (normal)
                else:
                    square = chess.square(7 - col, row)  # Black at bottom (flipped)
                
                # Highlight selected square
                if square == self.selected_square:
                    color = "#FFFF99"
                
                self.board_canvas.create_rectangle(
                    x1, y1, x2, y2, 
                    fill=color, 
                    outline="black",
                    tags=f"square_{square}"
                )
                
                # Draw piece if present
                piece = self.game.board.piece_at(square)
                if piece:
                    # Get piece symbol using simplified structure
                    piece_char = piece.symbol()  # Returns 'P', 'p', 'R', 'r', etc.
                    symbol = self.piece_symbols[piece_char]
                    
                    # Scale piece size with board size (larger board = larger pieces)
                    piece_font_size = max(16, int(self.square_size * 0.6))
                    
                    self.board_canvas.create_text(
                        x1 + self.square_size // 2,
                        y1 + self.square_size // 2,
                        text=symbol,
                        font=("Arial", piece_font_size),
                        fill="#000000",  # Solid black for better visibility
                        tags=f"piece_{square}"
                    )
        
        # Draw grid lines
        board_size = 8 * self.square_size
        for i in range(9):  # 9 lines for 8 squares
            # Vertical lines
            x = i * self.square_size
            self.board_canvas.create_line(
                x, 0, x, board_size,
                fill="black", width=1
            )
            # Horizontal lines
            y = i * self.square_size
            self.board_canvas.create_line(
                0, y, board_size, y,
                fill="black", width=1
            )
        
        # Draw coordinates in every square for chess novices
        coord_font_size = max(8, self.square_size // 8)  # Smaller font for in-square coordinates
        
        # Draw coordinates in each square to match board orientation
        for row in range(8):
            for col in range(8):
                # Calculate square position
                x1 = col * self.square_size
                y1 = row * self.square_size
                
                # Calculate file and rank to match the piece orientation
                # User's pieces are always at the bottom
                if self.player_color == "white":
                    file_letter = chr(ord('a') + col)
                    rank_number = str(8 - row)
                else:
                    # Black at bottom - flip the coordinates
                    file_letter = chr(ord('h') - col)
                    rank_number = str(row + 1)
                
                square_name = f"{file_letter}{rank_number}"
                
                # Determine text color based on square color for good contrast
                is_light = (row + col) % 2 == 0
                text_color = "#8B4513" if is_light else "#F5DEB3"  # Dark brown on light, light on dark
                
                # Draw square coordinate in top-left corner
                self.board_canvas.create_text(
                    x1 + 8,
                    y1 + 8,
                    text=square_name,
                    font=("Arial", coord_font_size, "bold"),
                    fill=text_color,
                    anchor="nw"
                )
        
        # Border coordinates removed - coordinates now shown in each square for novice players
    
    def square_from_coords(self, x: int, y: int) -> Optional[int]:
        """Convert canvas coordinates to chess square based on board orientation."""
        if 0 <= x < 8 * self.square_size and 0 <= y < 8 * self.square_size:
            col = x // self.square_size
            row = y // self.square_size
            
            # Convert to chess coordinates based on player orientation
            # This must match the logic in draw_board
            if self.player_color == "white":
                return chess.square(col, 7 - row)  # White at bottom (normal)
            else:
                return chess.square(7 - col, row)  # Black at bottom (flipped)
        return None
    
    def on_square_click(self, event):
        """Handle square clicks for piece movement."""
        square = self.square_from_coords(event.x, event.y)
        if square is None:
            return
        
        if self.selected_square is None:
            # Select piece if there's one on this square
            piece = self.game.board.piece_at(square)
            if piece and piece.color == self.game.board.turn:
                self.selected_square = square
                self.draw_board()
        else:
            # Try to make a move
            if square == self.selected_square:
                # Deselect
                self.selected_square = None
                self.draw_board()
            else:
                # Attempt move
                try:
                    move = chess.Move(self.selected_square, square)
                    
                    # Check for pawn promotion
                    piece = self.game.board.piece_at(self.selected_square)
                    if (piece and piece.piece_type == chess.PAWN and 
                        (chess.square_rank(square) == 7 or chess.square_rank(square) == 0)):
                        # Promote to queen by default (could add promotion dialog)
                        move.promotion = chess.QUEEN
                    
                    # Make the move
                    if move in self.game.board.legal_moves:
                        san_move = self.game.board.san(move)
                        self.game.make_move(san_move)
                        self.selected_square = None
                        self.update_display()
                    else:
                        # Invalid move
                        self.selected_square = None
                        self.draw_board()
                        
                except Exception as e:
                    self.selected_square = None
                    self.draw_board()
                    messagebox.showerror("Invalid Move", f"Cannot make that move: {e}")
    
    def on_manual_move(self, event=None):
        """Handle manual move input (case-insensitive)."""
        move_str = self.move_entry.get().strip()
        if not move_str:
            return
        
        # Make move input case-insensitive for user convenience
        # Convert to lowercase except for piece letters which should be uppercase
        normalized_move = ""
        for i, char in enumerate(move_str):
            if i == 0 and char.lower() in 'nbrqk':  # Piece notation (Knight, Bishop, Rook, Queen, King)
                normalized_move += char.upper()
            elif char in 'NBRQK':  # Handle uppercase piece letters anywhere
                normalized_move += char
            else:
                normalized_move += char.lower()
        
        if self.game.make_move(normalized_move):
            self.move_entry.delete(0, tk.END)
            self.update_display()
            result = self.game.get_game_result()
            result_text = {
                "1-0": "White wins!",
                "0-1": "Black wins!",
                "1/2-1/2": "Draw!",
                "*": "Game ongoing"
            }.get(result, "Game over")
            
            if result != "*":
                messagebox.showinfo("Game Over", result_text)
        else:
            messagebox.showerror("Invalid Move", f"Cannot make move: {move_str}")
    
    def update_display(self):
        """Update all display elements."""
        self.draw_board()
        self.update_analysis_panel()
        self.update_history_panel()
        
        # Check for game over
        if self.game.is_game_over():
            result = self.game.get_game_result()
            result_text = {
                "1-0": "White wins!",
                "0-1": "Black wins!",
                "1/2-1/2": "Draw!",
                "*": "Game ongoing"
            }.get(result, "Game over")
            
            if result != "*":
                messagebox.showinfo("Game Over", result_text)
    
    def update_analysis_panel(self):
        """Update the engine analysis panel."""
        if not self.analysis_enabled:
            self.analysis_text.config(state=tk.NORMAL)
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(1.0, "Analysis disabled")
            self.analysis_text.config(state=tk.DISABLED)
            return
        
        # Try to recover engine if it's crashed
        if not self.engine.is_available():
            if not self.engine.recover_engine():
                self.analysis_text.config(state=tk.NORMAL)
                self.analysis_text.delete(1.0, tk.END)
                self.analysis_text.insert(1.0, "Engine crashed\n\nTrying to recover...\n\nIf problems persist,\nrestart the application")
                self.analysis_text.config(state=tk.DISABLED)
                return
        
        if self.game.is_game_over():
            self.analysis_text.config(state=tk.NORMAL)
            self.analysis_text.delete(1.0, tk.END)
            self.analysis_text.insert(1.0, "Game over")
            self.analysis_text.config(state=tk.DISABLED)
            return
        
        # Show analysis for both user and opponent moves
        current_turn = self.game.board.turn  # True for White, False for Black
        turn_color = "White" if current_turn else "Black"
        
        self.analysis_text.config(state=tk.NORMAL)
        self.analysis_text.delete(1.0, tk.END)
        
        try:
            analysis_text = self.engine.get_move_analysis_text(self.game.get_board_fen())
            # Add turn indicator
            self.analysis_text.insert(1.0, f"{turn_color} to move\n\n{analysis_text}")
        except Exception as e:
            self.analysis_text.insert(1.0, f"Analysis error: {e}")
        
        self.analysis_text.config(state=tk.DISABLED)
    
    def update_history_panel(self):
        """Update the move history panel."""
        history = self.game.get_move_history_san()
        
        history_lines = []
        for i in range(0, len(history), 2):
            move_num = (i // 2) + 1
            white_move = history[i]
            black_move = history[i + 1] if i + 1 < len(history) else ""
            
            if black_move:
                history_lines.append(f"{move_num:2d}. {white_move:8s} {black_move}")
            else:
                history_lines.append(f"{move_num:2d}. {white_move}")
        
        self.history_text.config(state=tk.NORMAL)
        self.history_text.delete(1.0, tk.END)
        if history_lines:
            self.history_text.insert(1.0, "\n".join(history_lines))
        self.history_text.config(state=tk.DISABLED)
        
        # Auto-scroll to bottom
        self.history_text.see(tk.END)
    
    def toggle_analysis(self):
        """Toggle engine analysis."""
        self.analysis_enabled = self.analysis_var.get()
        self.update_analysis_panel()
    
    def undo_move(self):
        """Undo the last move."""
        if self.game.undo_move():
            self.selected_square = None
            self.update_display()
        else:
            messagebox.showinfo("Undo", "No moves to undo.")
    
    def new_game(self):
        """Start a new game with save prompt and color selection."""
        # Check if there are moves to save
        if len(self.game.move_history) > 0:
            # Ask user what to do with current game
            result = messagebox.askyesnocancel(
                "New Game", 
                "Would you like to save the current game before starting a new one?\n\n"
                "Yes = Save and start new game\n"
                "No = Discard and start new game\n"
                "Cancel = Continue current game"
            )
            
            if result is None:  # Cancel
                return
            elif result:  # Yes - Save first
                if not self.save_pgn():  # If save was cancelled, don't start new game
                    return
        
        # Reset the game state
        self.game.reset_game()
        self.selected_square = None
        
        # Show color selection dialog for the new game
        self.show_color_selection_dialog()
        
        # If user cancelled color selection, restore the previous game
        if self.player_color is None:
            # User cancelled color selection, so we don't start a new game
            # The dialog close handler will exit the app if needed
            return
        
        # Update display with new game
        self.update_display()
    
    def save_pgn(self):
        """Save the current game as PGN.
        
        Returns:
            True if save was successful, False if cancelled or failed
        """
        filename = filedialog.asksaveasfilename(
            defaultextension=".pgn",
            filetypes=[("PGN files", "*.pgn"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.game.export_pgn(filename)
                messagebox.showinfo("Save", f"Game saved to {filename}")
                return True
            except Exception as e:
                messagebox.showerror("Save Error", f"Could not save game: {e}")
                return False
        else:
            # User cancelled the save dialog
            return False
    
    def load_pgn(self):
        """Load a game from PGN file."""
        filename = filedialog.askopenfilename(
            filetypes=[("PGN files", "*.pgn"), ("All files", "*.*")]
        )
        if filename:
            try:
                # This is a basic implementation - could be enhanced
                messagebox.showinfo("Load", "PGN loading not yet implemented.")
            except Exception as e:
                messagebox.showerror("Load Error", f"Could not load game: {e}")
    
    def run(self):
        """Start the GUI main loop."""
        # Show initial help if engine not available
        if not self.engine.is_available():
            messagebox.showwarning(
                "Engine Not Found",
                "Stockfish engine not found.\n\n"
                "Download from: https://stockfishchess.org/download/\n"
                "Place the executable in your PATH or the same directory as this script.\n\n"
                "The app will work without analysis features."
            )
        
        self.root.mainloop()

def main():
    """Main entry point for GUI."""
    import sys
    
    stockfish_path = None
    if len(sys.argv) > 1:
        stockfish_path = sys.argv[1]
    
    gui = ChessGUI(stockfish_path)
    gui.run()

if __name__ == "__main__":
    main()