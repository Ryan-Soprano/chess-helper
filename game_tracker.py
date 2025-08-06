import chess
import chess.pgn
from typing import List, Optional
from datetime import datetime

class GameTracker:
    """Manages chess game state, move history, and PGN export."""
    
    # CONSTRUCTOR

    def __init__(self, player_color: chess.Color = chess.WHITE):
        self.board = chess.Board()
        self.move_history: List[chess.Move] = []
        self.player_color = player_color
        self.game_start_time = datetime.now()
        
    # CORE GAME FUNCTIONS

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
    
    # GAME STATE QUERIES

    def get_legal_moves(self) -> List[str]:
        """Get all legal moves in algebraic notation."""
        return [self.board.san(move) for move in self.board.legal_moves]
    
    def get_board_fen(self) -> str:
        """Get current board position in FEN notation."""
        return self.board.fen()
    
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
    # DISPLAY METHODS

    def get_board_display(self) -> str:
        """Get a text representation of the board."""
        return str(self.board)

    def get_move_history_san(self) -> List[str]:
        """Get move history in algebraic notation."""
        # Recreate board to get SAN notation
        temp_board = chess.Board()
        san_moves = []
        for move in self.move_history:
            san_moves.append(temp_board.san(move))
            temp_board.push(move)
        return san_moves
    
    # ANALYSIS METHODS
    
    def get_game_statistics(self) -> dict:
        """Get comprehensive game statistics."""
        stats = {
            'total_moves': len(self.move_history),
            'game_duration': (datetime.now() - self.game_start_time).total_seconds() / 60,  # minutes
            'captures': 0,
        'checks': 0,
        'castles': 0,
        'promotions': 0,
        'current_material': self._calculate_material()
    }
    
        # Analyze moves for statistics
        temp_board = chess.Board()
        for move in self.move_history:
            move_obj = temp_board.parse_san(move) if isinstance(move, str) else move
            
            # Count captures
            if temp_board.is_capture(move_obj):
                stats['captures'] += 1
            
            # Count checks
            temp_board.push(move_obj)
            if temp_board.is_check():
                stats['checks'] += 1
            
            # Count castles
            if temp_board.is_castling(move_obj):
                stats['castles'] += 1
            
            # Count promotions  
            if move_obj.promotion:
                stats['promotions'] += 1
        
        return stats

    def analyze_game_quality(self, engine) -> dict:
        """Analyze the overall quality of the game using engine."""
        if not engine.is_available():
            return {"error": "Engine not available"}
    
        analysis = {
        'total_moves': len(self.move_history),
        'blunders': 0,
        'mistakes': 0,
        'inaccuracies': 0,
        'excellent_moves': 0,
        'average_centipawn_loss': 0
    }
    
        temp_board = chess.Board()
        total_loss = 0
        move_count = 0
    
        for i, move in enumerate(self.move_history):
            if isinstance(move, str):
                move_obj = temp_board.parse_san(move)
            else:
                move_obj = move
            
        # Get position before move
        pos_before = temp_board.fen()
        
        # Make the move
        temp_board.push(move_obj)
        
        # Get position after move
        pos_after = temp_board.fen()
        
        # Analyze both positions
        eval_before = engine.get_evaluation(pos_before)
        eval_after = engine.get_evaluation(pos_after)
        
        if eval_before is not None and eval_after is not None:
            # Calculate centipawn loss (from the moving player's perspective)
            if temp_board.turn == chess.BLACK:  # White just moved
                loss = eval_before - eval_after
            else:  # Black just moved
                loss = eval_after - eval_before
            
            total_loss += abs(loss)
            move_count += 1
            
            # Categorize move quality
            if loss <= -2.0:
                analysis['excellent_moves'] += 1
            elif loss <= 0.5:
                pass  # Good move, no penalty
            elif loss <= 1.0:
                analysis['inaccuracies'] += 1
            elif loss <= 2.0:
                analysis['mistakes'] += 1
            else:
                analysis['blunders'] += 1
    
        if move_count > 0:
            analysis['average_centipawn_loss'] = total_loss / move_count
    
        return analysis

    # EXPORT/IMPORT METHODS

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
    
    def export_analysis_report(self, engine, filename: Optional[str] = None) -> str:
        """Export a comprehensive game analysis report."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"game_analysis_{timestamp}.txt"
    
        stats = self.get_game_statistics()
        quality = self.analyze_game_quality(engine)
    
        report_lines = [
            "CHESS GAME ANALYSIS REPORT",
            "=" * 50,
        f"Date: {self.game_start_time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"Duration: {stats['game_duration']:.1f} minutes",
        f"Total Moves: {stats['total_moves']}",
        f"Result: {self.get_game_result()}",
        "",
        "GAME STATISTICS:",
        f"  Captures: {stats['captures']}",
        f"  Checks: {stats['checks']}",
        f"  Castles: {stats['castles']}",
        f"  Promotions: {stats['promotions']}",
        f"  Material Balance: {stats['current_material']['advantage']:+d}",
        "",
        "MOVE QUALITY ANALYSIS:",
        f"  Excellent moves: {quality.get('excellent_moves', 0)}",
        f"  Inaccuracies: {quality.get('inaccuracies', 0)}",
        f"  Mistakes: {quality.get('mistakes', 0)}",
        f"  Blunders: {quality.get('blunders', 0)}",
        f"  Average centipawn loss: {quality.get('average_centipawn_loss', 0):.2f}",
        "",
        "MOVE HISTORY:",
        *self._format_move_history_for_report()
    ]
    
        report_content = "\n".join(report_lines)
    
        with open(filename, 'w') as f:
            f.write(report_content)
    
        return filename

    def reset_game(self):
        """Reset the game to starting position."""
        self.board = chess.Board()
        self.move_history = []
        self.game_start_time = datetime.now()

    def _calculate_material(self) -> dict:
        """Calculate current material balance."""
        piece_values = {
            chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3,
            chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0
        }
    
        white_material = 0
        black_material = 0
    
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                value = piece_values[piece.piece_type]
                if piece.color == chess.WHITE:
                    white_material += value
                else:
                    black_material += value
    
        return {
            'white': white_material,
            'black': black_material,
            'advantage': white_material - black_material
        }
    
    def _format_move_history_for_report(self) -> List[str]:
        """Format move history for the analysis report."""
        history = self.get_move_history_san()
        formatted_lines = []
    
        for i in range(0, len(history), 2):
            move_num = (i // 2) + 1
            white_move = history[i]
            black_move = history[i + 1] if i + 1 < len(history) else ""
        
        if black_move:
            formatted_lines.append(f"{move_num:2d}. {white_move:<10s} {black_move}")
        else:
            formatted_lines.append(f"{move_num:2d}. {white_move}")
    
        return formatted_lines
    
    
    
    
    
    
        
    