import chess
import chess.pgn
from typing import List, Optional
from datetime import datetime

class GameTracker:
    """Manages chess game state, move history, and PGN export."""
    
    def __init__(self, player_color: chess.Color = chess.WHITE):
        self.board = chess.Board()
        self.move_history: List[chess.Move] = []
        self.player_color = player_color
        self.game_start_time = datetime.now()
        
    def make_move(self, move_str: str) -> bool:
        """
        Make a move on the board.
        
        Args:
            move_str: Move in algebraic notation (e.g., 'e4', 'Nf3', 'O-O')
            
        Returns:
            True if move was successful, False otherwise
        """
        try:
            # Try to parse the move
            move = self.board.parse_san(move_str)
            
            # Check if move is legal
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move)
                return True
            else:
                print(f"Illegal move: {move_str}")
                return False
                
        except ValueError as e:
            print(f"Invalid move format: {move_str}. Error: {e}")
            return False
    
    def make_move_uci(self, uci_move: str) -> bool:
        """
        Make a move using UCI notation (e.g., 'e2e4').
        
        Args:
            uci_move: Move in UCI format
            
        Returns:
            True if move was successful, False otherwise
        """
        try:
            move = chess.Move.from_uci(uci_move)
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move)
                return True
            else:
                print(f"Illegal move: {uci_move}")
                return False
        except ValueError as e:
            print(f"Invalid UCI move: {uci_move}. Error: {e}")
            return False
    
    def undo_move(self) -> bool:
        """
        Undo the last move.
        
        Returns:
            True if undo was successful, False if no moves to undo
        """
        if self.move_history:
            self.board.pop()
            self.move_history.pop()
            return True
        return False
    
    def get_legal_moves(self) -> List[str]:
        """Get all legal moves in algebraic notation."""
        return [self.board.san(move) for move in self.board.legal_moves]
    
    def get_board_fen(self) -> str:
        """Get current board position in FEN notation."""
        return self.board.fen()
    
    def get_move_history_san(self) -> List[str]:
        """Get move history in algebraic notation."""
        # Recreate board to get SAN notation
        temp_board = chess.Board()
        san_moves = []
        for move in self.move_history:
            san_moves.append(temp_board.san(move))
            temp_board.push(move)
        return san_moves
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.board.is_game_over()
    
    def get_game_result(self) -> str:
        """Get the game result."""
        if self.board.is_checkmate():
            if self.board.turn == chess.WHITE:
                return "0-1"  # Black wins
            else:
                return "1-0"  # White wins
        elif self.board.is_stalemate() or self.board.is_insufficient_material():
            return "1/2-1/2"  # Draw
        else:
            return "*"  # Game ongoing
    
    def export_pgn(self, filename: Optional[str] = None) -> str:
        """
        Export the game as PGN.
        
        Args:
            filename: Optional filename to save PGN to
            
        Returns:
            PGN string representation of the game
        """
        game = chess.pgn.Game()
        
        # Set game headers
        game.headers["Event"] = "Home Game"
        game.headers["Site"] = "Chess Helper App"
        game.headers["Date"] = self.game_start_time.strftime("%Y.%m.%d")
        game.headers["Round"] = "1"
        game.headers["White"] = "White" if self.player_color == chess.WHITE else "Player"
        game.headers["Black"] = "Black" if self.player_color == chess.BLACK else "Player"
        game.headers["Result"] = self.get_game_result()
        
        # Add moves
        node = game
        temp_board = chess.Board()
        for move in self.move_history:
            node = node.add_variation(move)
            temp_board.push(move)
        
        pgn_string = str(game)
        
        # Save to file if filename provided
        if filename:
            with open(filename, 'w') as f:
                f.write(pgn_string)
            print(f"Game saved to {filename}")
        
        return pgn_string
    
    def get_board_display(self) -> str:
        """Get a text representation of the board."""
        return str(self.board)
    
    def reset_game(self):
        """Reset the game to starting position."""
        self.board = chess.Board()
        self.move_history = []
        self.game_start_time = datetime.now()
        
    def get_position_info(self) -> dict:
        """Get detailed information about current position."""
        return {
            'turn': 'White' if self.board.turn == chess.WHITE else 'Black',
            'move_number': self.board.fullmove_number,
            'is_check': self.board.is_check(),
            'is_checkmate': self.board.is_checkmate(),
            'is_stalemate': self.board.is_stalemate(),
            'legal_moves_count': len(list(self.board.legal_moves)),
            'fen': self.board.fen()
        }