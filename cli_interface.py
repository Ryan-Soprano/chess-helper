import chess  # ← MISSING IMPORT - ADD THIS LINE
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
  flip        - Flip board perspective
  quit        - Exit the application
        """
        print(help_text)
    
    def print_board(self):
        """Print the current board position."""
        print("\nCurrent position:")
        
        # Show board from player's perspective
        if self.player_color == 'black':
            # Show board flipped for black player
            board_str = str(self.game.board).split('\n')
            board_str.reverse()  # Flip vertically
            for line in board_str:
                print(line[::-1])  # Flip horizontally
        else:
            print(self.game.get_board_display())
        
        # Show position info
        info = self.game.get_position_info()
        print(f"\nTo move: {info['turn']}")
        print(f"Move #{info['move_number']}")
        
        if info['is_check']:
            print("🔥 CHECK!")
        if info['is_checkmate']:
            print("🏆 CHECKMATE!")
        if info['is_stalemate']:
            print("🤝 STALEMATE!")
    
    def print_analysis(self):
        """Print engine analysis if available and enabled."""
        if not self.analysis_mode:
            return
            
        if not self.engine.is_available():
            print("⚠️  Engine analysis not available.")
            return
        
        print("\n🤖 Engine Analysis:")
        analysis_text = self.engine.get_move_analysis_text(self.game.get_board_fen())
        print(analysis_text)
    
    def handle_move(self, move_str: str) -> bool:
        """
        Handle a move input with better error messages.
        
        Args:
            move_str: Move in algebraic notation
            
        Returns:
            True if move was successful
        """
        if self.game.make_move(move_str):
            print(f"\n✅ Move played: {move_str}")
            self.print_board()
            
            # Show analysis after the move
            if self.analysis_mode and not self.game.is_game_over():
                self.print_analysis()
            
            # Check for game over
            if self.game.is_game_over():
                result = self.game.get_game_result()
                result_text = {
                    "1-0": "🏆 Game Over! White wins!",
                    "0-1": "🏆 Game Over! Black wins!",
                    "1/2-1/2": "🤝 Game Over! It's a draw!",
                    "*": "Game ongoing"
                }.get(result, "Game over")
                print(f"\n{result_text}")
            
            return True
        else:
            # More helpful error message
            legal_moves = self.game.get_legal_moves()
            print(f"❌ Invalid move: {move_str}")
            
            # Suggest similar moves if possible
            similar_moves = [m for m in legal_moves if move_str.lower() in m.lower()]
            if similar_moves:
                print(f"💡 Did you mean: {', '.join(similar_moves[:5])}")
            
            return False
    
    def show_legal_moves(self):
        """Display all legal moves with better formatting."""
        moves = self.game.get_legal_moves()
        if moves:
            print(f"\n⚡ LEGAL MOVES ({len(moves)} available):")
            
            # Group moves by type for better readability
            pawn_moves = [m for m in moves if not any(c in m for c in 'NBRQK')]
            piece_moves = [m for m in moves if any(c in m for c in 'NBRQ')]
            king_moves = [m for m in moves if 'K' in m or 'O' in m]
            
            if pawn_moves:
                print("  Pawn moves:", "  ".join(pawn_moves))
            if piece_moves:
                print("  Piece moves:", "  ".join(piece_moves))
            if king_moves:
                print("  King moves:", "  ".join(king_moves))
        else:
            print("\n❌ No legal moves available.")
    
    def show_move_history(self):
        """Display the move history with improved formatting."""
        history = self.game.get_move_history_san()
        if not history:
            print("\n📜 No moves played yet.")
            return
        
        print(f"\n📜 MOVE HISTORY ({len(history)} moves):")
        print("─" * 40)
        
        # Display moves in pairs (White, Black) with better alignment
        for i in range(0, len(history), 2):
            move_num = (i // 2) + 1
            white_move = history[i]
            black_move = history[i + 1] if i + 1 < len(history) else ""
            
            if black_move:
                print(f"{move_num:2d}. {white_move:<10s} {black_move}")
            else:
                print(f"{move_num:2d}. {white_move}")
    
    def toggle_analysis(self):
        """Toggle engine analysis on/off."""
        self.analysis_mode = not self.analysis_mode
        status = "enabled ✅" if self.analysis_mode else "disabled ❌"
        print(f"\n🤖 Engine analysis {status}")
    
    def flip_board(self):
        """Toggle board perspective."""
        self.player_color = 'black' if self.player_color == 'white' else 'white'
        print(f"\n🔄 Board flipped! Now showing from {self.player_color} perspective.")
        self.print_board()
    
    def show_detailed_evaluation(self):
        """Show detailed position evaluation with better formatting."""
        if not self.engine.is_available():
            print("❌ Engine not available for analysis.")
            return
        
        fen = self.game.get_board_fen()
        analysis = self.engine.analyze_position(fen)
        
        print("\n" + "="*50)
        print("🔍 DETAILED POSITION ANALYSIS")
        print("="*50)
        
        if analysis.get('evaluation') is not None:
            eval_score = analysis['evaluation']
            if abs(eval_score) > 900:
                mate_in = int(999 - abs(eval_score))
                color = "White" if eval_score > 0 else "Black"
                print(f"📊 Evaluation: {color} mates in {mate_in}")
            else:
                # Convert to more readable format
                if eval_score > 0:
                    print(f"📊 Evaluation: +{eval_score:.2f} (White advantage)")
                elif eval_score < 0:
                    print(f"📊 Evaluation: {eval_score:.2f} (Black advantage)")
                else:
                    print(f"📊 Evaluation: {eval_score:.2f} (Equal position)")
        
        best_move = analysis.get('best_move', 'N/A')
        if best_move != 'N/A':
            san_move = self.engine.convert_uci_to_san(best_move, fen)
            move_display = san_move if san_move else best_move
            print(f"🎯 Best move: {move_display}")
        
        if analysis.get('top_moves'):
            print("\n🏆 Top alternatives:")
            for i, move_info in enumerate(analysis['top_moves'][:5], 1):
                san_move = self.engine.convert_uci_to_san(move_info['move'], fen)
                move_display = san_move if san_move else move_info['move']
                if move_info['evaluation'] is not None:
                    print(f"  {i}. {move_display} ({move_info['evaluation']:+.2f})")
                else:
                    print(f"  {i}. {move_display}")
    
    def save_game(self, filename: Optional[str] = None):
        """Save the current game as PGN with confirmation."""
        if not self.game.move_history:
            print("❌ No moves to save yet.")
            return
            
        if not filename:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chess_game_{timestamp}.pgn"
        
        try:
            pgn = self.game.export_pgn(filename)
            print(f"💾 Game saved to: {filename}")
            print(f"📝 {len(self.game.move_history)} moves saved")
        except Exception as e:
            print(f"❌ Error saving game: {e}")
    
    def reset_game(self):
        """Reset to a new game with confirmation."""
        if self.game.move_history:
            print("\n⚠️  This will discard the current game.")
            confirm = input("Type 'yes' to confirm or press Enter to cancel: ").strip().lower()
            if confirm != 'yes':
                print("Reset cancelled.")
                return
        
        self.game.reset_game()
        print("\n🆕 New game started!")
        self.print_board()
        if self.analysis_mode:
            self.print_analysis()
    
    def select_player_color(self):
        """Prompt user to select their color with improved UX."""
        print("\n" + "="*50)
        print("♟️  CHESS HELPER - COLOR SELECTION")
        print("="*50)
        print("\nFor live home games, please select your color:")
        print("\n1. ♔ White (I move first)")
        print("2. ♚ Black (Opponent moves first)")
        print("3. 👀 Observer (Watch both sides)")
        
        while True:
            try:
                choice = input("\nEnter your choice (1, 2, or 3): ").strip()
                if choice == '1':
                    self.player_color = 'white'
                    print("\n✅ You are playing as White. You move first!")
                    break
                elif choice == '2':
                    self.player_color = 'black' 
                    print("\n✅ You are playing as Black. Your opponent moves first.")
                    break
                elif choice == '3':
                    self.player_color = 'observer'
                    print("\n👀 Observer mode. Board will show from White's perspective.")
                    self.player_color = 'white'  # Default to white view for observer
                    break
                else:
                    print("❌ Please enter 1, 2, or 3.")
            except (KeyboardInterrupt, EOFError):
                print("\n\n👋 Exiting Chess Helper...")
                exit(0)
    
    def run(self):
        """Main command loop with improved startup."""
        print("♟️  Welcome to Chess Helper! ♟️")
        
        # Select player color first
        self.select_player_color()
        
        print("\n💡 Type 'help' for available commands.")
        print("💡 Just type moves like: e4, Nf3, O-O, Qxd5")
        
        if not self.engine.is_available():
            print("\n⚠️  Stockfish engine not found.")
            print("   Download from: https://stockfishchess.org/download/")
            print("   Analysis features will be disabled.")
        else:
            print("\n🤖 Stockfish engine ready for analysis!")
        
        self.print_board()
        if self.analysis_mode and self.engine.is_available():
            self.print_analysis()
        
        while True:
            try:
                user_input = input("\n♟️  Chess Helper> ").strip()
                
                if not user_input:
                    continue
                
                # Parse command
                parts = user_input.split()
                command = parts[0].lower()
                args = parts[1:] if len(parts) > 1 else []
                
                if command in ['quit', 'exit', 'q', 'bye']:
                    print("👋 Thanks for using Chess Helper! Good game!")
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
                        print("↩️  Move undone!")
                        self.print_board()
                        if self.analysis_mode:
                            self.print_analysis()
                    else:
                        print("❌ No moves to undo.")
                elif command == 'analysis':
                    self.toggle_analysis()
                elif command == 'eval':
                    self.show_detailed_evaluation()
                elif command == 'flip':
                    self.flip_board()
                elif command == 'save':
                    filename = args[0] if args else None
                    self.save_game(filename)
                elif command == 'reset':
                    self.reset_game()
                else:
                    # Treat as move input
                    self.handle_move(user_input)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Exiting Chess Helper...")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                print("💡 Type 'help' for available commands")

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