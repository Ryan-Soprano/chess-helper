from game_tracker import GameTracker
from engine import ChessEngine
from typing import Optional

class ChessCliInterface:
    """Command-line interface for the chess helper app."""
    
    def __init__(self, stockfish_path: Optional[str] = None):
        self.game = GameTracker()
        self.engine = ChessEngine(stockfish_path)
        self.analysis_mode = True  # Whether to show engine analysis
        self.player_color = None  # Will be set by color selection
        
    def print_help(self):
        """Print available commands."""
        help_text = """
Available commands:
  [move]      - Make a move (e.g., e4, Nf3, O-O, Qxe7+)
  help        - Show this help message
  board       - Display current board position
  moves       - Show legal moves
  history     - Show move history
  undo        - Undo last move
  analysis    - Toggle engine analysis on/off
  eval        - Show detailed position evaluation
  save [file] - Save game as PGN (optional filename)
  reset       - Start a new game
  quit        - Exit the application
        """
        print(help_text)
    
    def print_board(self):
        """Print the current board position."""
        print("\nCurrent position:")
        print(self.game.get_board_display())
        
        # Show position info
        info = self.game.get_position_info()
        print(f"\nTo move: {info['turn']}")
        print(f"Move #{info['move_number']}")
        
        if info['is_check']:
            print("CHECK!")
        if info['is_checkmate']:
            print("CHECKMATE!")
        if info['is_stalemate']:
            print("STALEMATE!")
    
    def print_analysis(self):
        """Print engine analysis if available and enabled."""
        if not self.analysis_mode:
            return
            
        if not self.engine.is_available():
            print("Engine analysis not available.")
            return
        
        print("\nEngine Analysis:")
        analysis_text = self.engine.get_move_analysis_text(self.game.get_board_fen())
        print(analysis_text)
    
    def handle_move(self, move_str: str) -> bool:
        """
        Handle a move input.
        
        Args:
            move_str: Move in algebraic notation
            
        Returns:
            True if move was successful
        """
        if self.game.make_move(move_str):
            print(f"\nMove played: {move_str}")
            self.print_board()
            
            # Show analysis after the move
            if self.analysis_mode and not self.game.is_game_over():
                self.print_analysis()
            
            # Check for game over
            if self.game.is_game_over():
                result = self.game.get_game_result()
                print(f"\nGame Over! Result: {result}")
            
            return True
        else:
            print(f"Invalid or illegal move: {move_str}")
            return False
    
    def show_legal_moves(self):
        """Display all legal moves."""
        moves = self.game.get_legal_moves()
        if moves:
            print(f"\nLegal moves ({len(moves)}):")
            # Group moves for better display
            for i in range(0, len(moves), 8):
                print("  " + "  ".join(moves[i:i+8]))
        else:
            print("\nNo legal moves available.")
    
    def show_move_history(self):
        """Display the move history."""
        history = self.game.get_move_history_san()
        if not history:
            print("\nNo moves played yet.")
            return
        
        print(f"\nMove history ({len(history)} moves):")
        
        # Display moves in pairs (White, Black)
        for i in range(0, len(history), 2):
            move_num = (i // 2) + 1
            white_move = history[i]
            black_move = history[i + 1] if i + 1 < len(history) else ""
            
            if black_move:
                print(f"{move_num:2d}. {white_move:8s} {black_move}")
            else:
                print(f"{move_num:2d}. {white_move}")
    
    def toggle_analysis(self):
        """Toggle engine analysis on/off."""
        self.analysis_mode = not self.analysis_mode
        status = "enabled" if self.analysis_mode else "disabled"
        print(f"\nEngine analysis {status}.")
    
    def show_detailed_evaluation(self):
        """Show detailed position evaluation."""
        if not self.engine.is_available():
            print("Engine not available for analysis.")
            return
        
        fen = self.game.get_board_fen()
        analysis = self.engine.analyze_position(fen)
        
        print("\nDetailed Position Analysis:")
        print(f"FEN: {fen}")
        
        if analysis.get('evaluation') is not None:
            eval_score = analysis['evaluation']
            if abs(eval_score) > 900:
                mate_in = int(999 - abs(eval_score))
                color = "White" if eval_score > 0 else "Black"
                print(f"Evaluation: {color} mates in {mate_in}")
            else:
                print(f"Evaluation: {eval_score:+.2f} pawns")
        
        print(f"Best move: {analysis.get('best_move', 'N/A')}")
        
        if analysis.get('top_moves'):
            print("\nTop moves:")
            for i, move_info in enumerate(analysis['top_moves'], 1):
                san_move = self.engine.convert_uci_to_san(move_info['move'], fen)
                move_display = san_move if san_move else move_info['move']
                if move_info['evaluation'] is not None:
                    print(f"  {i}. {move_display} ({move_info['evaluation']:+.2f})")
                else:
                    print(f"  {i}. {move_display}")
    
    def save_game(self, filename: Optional[str] = None):
        """Save the current game as PGN."""
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chess_game_{timestamp}.pgn"
        
        pgn = self.game.export_pgn(filename)
        print(f"\nGame saved to {filename}")
    
    def reset_game(self):
        """Reset to a new game."""
        self.game.reset_game()
        print("\nNew game started!")
        self.print_board()
        if self.analysis_mode:
            self.print_analysis()
    
    def select_player_color(self):
        """Prompt user to select their color."""
        print("\n" + "="*50)
        print("CHESS HELPER - COLOR SELECTION")
        print("="*50)
        print("\nFor live home games, please select your color:")
        print("\n1. White (I move first)")
        print("2. Black (Opponent moves first)")
        
        while True:
            try:
                choice = input("\nEnter your choice (1 or 2): ").strip()
                if choice == '1':
                    self.player_color = 'white'
                    print("\nYou are playing as White. You move first!")
                    break
                elif choice == '2':
                    self.player_color = 'black'
                    print("\nYou are playing as Black. Your opponent moves first.")
                    break
                else:
                    print("Please enter 1 for White or 2 for Black.")
            except (KeyboardInterrupt, EOFError):
                print("\nExiting Chess Helper...")
                exit(0)
    
    def run(self):
        """Main command loop."""
        print("Welcome to Chess Helper!")
        
        # Select player color first
        self.select_player_color()
        
        print("\nType 'help' for available commands.")
        
        if not self.engine.is_available():
            print("\nWarning: Stockfish engine not found.")
            print("Download Stockfish from https://stockfishchess.org/download/")
            print("Analysis features will be disabled.")
        
        self.print_board()
        if self.analysis_mode:
            self.print_analysis()
        
        while True:
            try:
                user_input = input("\nChess Helper> ").strip()
                
                if not user_input:
                    continue
                
                # Parse command
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if command in ['quit', 'exit', 'q']:
                    print("Thanks for using Chess Helper!")
                    break
                elif command == 'help':
                    self.print_help()
                elif command == 'board':
                    self.print_board()
                elif command == 'moves':
                    self.show_legal_moves()
                elif command == 'history':
                    self.show_move_history()
                elif command == 'undo':
                    if self.game.undo_move():
                        print("Move undone.")
                        self.print_board()
                        if self.analysis_mode:
                            self.print_analysis()
                    else:
                        print("No moves to undo.")
                elif command == 'analysis':
                    self.toggle_analysis()
                elif command == 'eval':
                    self.show_detailed_evaluation()
                elif command == 'save':
                    filename = args[0] if args else None
                    self.save_game(filename)
                elif command == 'reset':
                    self.reset_game()
                else:
                    # Treat as move input
                    self.handle_move(user_input)
                    
            except KeyboardInterrupt:
                print("\n\nExiting Chess Helper...")
                break
            except Exception as e:
                print(f"Error: {e}")

def main():
    """Main entry point for CLI interface."""
    import sys
    
    stockfish_path = None
    if len(sys.argv) > 1:
        stockfish_path = sys.argv[1]
    
    cli = ChessCliInterface(stockfish_path)
    cli.run()

if __name__ == "__main__":
    main()