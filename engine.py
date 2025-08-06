import chess
from stockfish import Stockfish
from typing import Optional, List, Dict
import os

class ChessEngine:
    """Interface for chess engine analysis using Stockfish."""
    
    # CONSTRUCTOR
    
    def __init__(self, stockfish_path: Optional[str] = None, depth: int = 15):
        """
        Initialize the chess engine.
        
        Args:
            stockfish_path: Path to Stockfish executable. If None, uses system PATH
            depth: Search depth for analysis
        """
        self.depth = depth
        self.stockfish = None
        self.engine_path = stockfish_path
        
        # Try to initialize Stockfish
        self._initialize_engine()
        
    
    # CORE ENGINE FUNCTIONS
    
    def is_available(self) -> bool:
        """Check if the engine is available for analysis."""
        if self.stockfish is None:
            return False
        
        # Test if engine is responsive
        try:
            # Try a simple operation to check if engine is alive
            self.stockfish.is_fen_valid("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
            return True
        except:
            # Engine has crashed, mark as unavailable
            self.stockfish = None
            return False
    
    def get_best_move(self, fen: str) -> Optional[str]:
        """
        Get the best move for the current position.
        
        Args:
            fen: Position in FEN notation
            
        Returns:
            Best move in UCI notation (e.g., 'e2e4') or None if engine unavailable
        """
        if not self.is_available():
            return None
            
        try:
            self.stockfish.set_fen_position(fen)
            best_move = self.stockfish.get_best_move()
            return best_move
        except Exception as e:
            print(f"Error getting best move: {e}")
            # Mark engine as crashed
            self.stockfish = None
            return None
    
    def get_evaluation(self, fen: str) -> Optional[float]:
        """
        Get position evaluation in centipawns.
        
        Args:
            fen: Position in FEN notation
            
        Returns:
            Evaluation in centipawns (positive = white advantage) or None
        """
        if not self.is_available():
            return None
            
        try:
            self.stockfish.set_fen_position(fen)
            evaluation = self.stockfish.get_evaluation()
            
            if evaluation['type'] == 'cp':
                return evaluation['value'] / 100.0  # Convert centipawns to pawns
            elif evaluation['type'] == 'mate':
                # Convert mate scores to large numbers
                mate_in = evaluation['value']
                if mate_in > 0:
                    return 999.0 - mate_in  # Positive mate score
                else:
                    return -999.0 - mate_in  # Negative mate score
            
        except Exception as e:
            print(f"Error getting evaluation: {e}")
            # Mark engine as crashed
            self.stockfish = None
            return None
    
    def analyze_position(self, fen: str) -> Dict:
        """
        Comprehensive position analysis.
        
        Args:
            fen: Position in FEN notation
            
        Returns:
            Dictionary with analysis results
        """
        if not self.is_available():
            return {'error': 'Engine not available'}
        
        analysis = {
            'best_move': self.get_best_move(fen),
            'evaluation': self.get_evaluation(fen),
            'top_moves': self.get_top_moves(fen, 3),
            'fen': fen
        }
        
        return analysis
    
    # ADVANCED ANALYSIS FUNCTIONS

    def get_top_moves(self, fen: str, num_moves: int = 3) -> List[Dict]:
        """
        Get top moves with evaluations.
        
        Args:
            fen: Position in FEN notation
            num_moves: Number of top moves to return
            
        Returns:
            List of dictionaries with 'move' and 'evaluation' keys
        """
        if not self.is_available():
            return []
            
        try:
            self.stockfish.set_fen_position(fen)
            top_moves = self.stockfish.get_top_moves(num_moves)
            
            result = []
            for move_info in top_moves:
                move_data = {
                    'move': move_info['Move'],
                    'evaluation': move_info['Centipawn'] / 100.0 if move_info['Centipawn'] is not None else None,
                    'mate': move_info.get('Mate', None)
                }
                result.append(move_data)
            
            return result
            
        except Exception as e:
            print(f"Error getting top moves: {e}")
            # Mark engine as crashed
            self.stockfish = None
            return []
    
    def analyze_multiple_positions(self, fen_list: List[str]) -> List[Dict]:
        """Analyze multiple positions efficiently."""
        results = []
        for fen in fen_list:
            analysis = self.analyze_position(fen)
            results.append(analysis)
        return results

    # CONFIGURATION FUNCTIONS
    
    def configure_for_game_analysis(self):
        """Configure engine for live game analysis (faster, less depth)."""
        if self.is_available():
            self.stockfish.set_depth(10)  # Faster for real-time
            self.stockfish.set_time(0.5)   # Quick analysis
            print("Engine configured for live game analysis")

    def configure_for_deep_analysis(self):
        """Configure engine for post-game deep analysis."""
        if self.is_available():
            self.stockfish.set_depth(20)  # Deeper analysis
            self.stockfish.set_time(3.0)   # More thorough
            print("Engine configured for deep analysis")
    
    def set_skill_level(self, level: int):
        """
        Set engine skill level (0-20, where 20 is strongest).
        
        Args:
            level: Skill level from 0 (weakest) to 20 (strongest)
        """
        if self.is_available():
            # Stockfish skill level goes from 0-20
            skill = max(0, min(20, level))
            try:
                self.stockfish.set_skill_level(skill)
                print(f"Engine skill level set to: {skill}")
            except:
                print("Could not set skill level")

    def get_engine_info(self) -> dict:
        """Get information about the engine."""
        if not self.is_available():
            return {"available": False}
    
        return {
            "available": True,
            "depth": self.depth,
            "path": self.engine_path,
            "version": "Stockfish (version detection not implemented)"
        }

    # UTILITY FUNCTIONS

    def convert_uci_to_san(self, uci_move: str, fen: str) -> Optional[str]:
        """
        Convert UCI move to Standard Algebraic Notation.
        
        Args:
            uci_move: Move in UCI format (e.g., 'e2e4')
            fen: Current position in FEN notation
            
        Returns:
            Move in SAN format (e.g., 'e4') or None if conversion fails
        """
        try:
    
            board = chess.Board(fen)
            move = chess.Move.from_uci(uci_move)
            if move in board.legal_moves:
                return board.san(move)
        except:
            pass
        return None
    
    def get_move_analysis_text(self, fen: str) -> str:
        """
        Get formatted analysis text for display.
        
        Args:
            fen: Position in FEN notation
            
        Returns:
            Formatted analysis string
        """
        if not self.is_available():
            return "Engine not available for analysis."
        
        analysis = self.analyze_position(fen)
        
        if 'error' in analysis:
            return analysis['error']
        
        result = []
        
        # Best move
        if analysis['best_move']:
            san_move = self.convert_uci_to_san(analysis['best_move'], fen)
            move_display = san_move if san_move else analysis['best_move']
            result.append(f"Best move: {move_display}")
        
        # Evaluation
        if analysis['evaluation'] is not None:
            eval_score = analysis['evaluation']
            if abs(eval_score) > 900:  # Mate score
                mate_in = int(999 - abs(eval_score))
                color = "White" if eval_score > 0 else "Black"
                result.append(f"Evaluation: {color} mates in {mate_in}")
            else:
                result.append(f"Evaluation: {eval_score:+.2f}")
        
        # Alternative moves
        if analysis['top_moves'] and len(analysis['top_moves']) > 1:
            result.append("\nAlternative moves:")
            for i, move_info in enumerate(analysis['top_moves'][1:], 2):
                san_move = self.convert_uci_to_san(move_info['move'], fen)
                move_display = san_move if san_move else move_info['move']
                if move_info['evaluation'] is not None:
                    result.append(f"  {i}. {move_display} ({move_info['evaluation']:+.2f})")
                else:
                    result.append(f"  {i}. {move_display}")
        
        return "\n".join(result)
    
    def close(self):
        """Close the engine connection."""
        if self.stockfish:
            try:
                # Stockfish library doesn't have explicit close method
                self.stockfish = None
            except:
                pass

    # PRIVATE METHODS
    
    def _initialize_engine(self):
        """Initialize the Stockfish engine."""
        try:
            if self.engine_path and os.path.exists(self.engine_path):
                self.stockfish = Stockfish(path=self.engine_path)
                print(f"Stockfish engine initialized at: {self.engine_path}")
            else:
                # Direct path to stockfish.exe in the project directory
                current_dir = os.path.dirname(os.path.abspath(__file__))
                stockfish_path = os.path.join(current_dir, "stockfish.exe")
                
                if os.path.exists(stockfish_path):
                    self.stockfish = Stockfish(path=stockfish_path)
                    self.engine_path = stockfish_path
                    print(f"Stockfish engine initialized at: {stockfish_path}")
                else:
                    # Fallback: try system PATH
                    try:
                        self.stockfish = Stockfish(path="stockfish")
                        self.engine_path = "stockfish"
                        print("Stockfish engine initialized from system PATH")
                    except:
                        self.stockfish = None
                        
            if self.stockfish is None:
                print("Warning: Could not initialize Stockfish engine.")
                print("Ensure stockfish.exe is in the project directory or system PATH.")
                return
                
            # Configure engine settings
            self.stockfish.set_depth(self.depth)
            print(f"Stockfish engine initialized successfully at: {self.engine_path}")
            
        except Exception as e:
            print(f"Error initializing engine: {e}")
            self.stockfish = None

    def recover_engine(self) -> bool:
        """Attempt to recover from engine crash by reinitializing."""
        if self.stockfish is not None:
            return True  # Engine is fine
        
        print("Attempting to recover Stockfish engine...")
        self._initialize_engine()
        return self.stockfish is not None