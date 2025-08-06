#!/usr/bin/env python3
"""
Chess Helper Application

A Python app to help during home chess games with:
- Manual move input and drag-and-drop chessboard
- Real-time move analysis using Stockfish
- Game tracking and PGN export

Usage:
    python main.py [--cli] [--stockfish-path PATH]
    
Options:
    --cli               Use command-line interface instead of GUI
    --stockfish-path    Path to Stockfish executable
    --help             Show this help message
"""

import sys
import argparse
import os
from typing import Optional

def check_dependencies():
    """Check if required dependencies are installed."""
    missing_deps = []
    
    try:
        import chess
    except ImportError:
        missing_deps.append("python-chess")
    
    try:
        import stockfish
    except ImportError:
        missing_deps.append("stockfish")
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    if missing_deps:
        print("Missing required dependencies:")
        for dep in missing_deps:
            print(f"  - {dep}")
        print("\nInstall with: pip install -r requirements.txt")
        return False
    
    return True

def find_stockfish():
    """Get path to Stockfish executable in project directory."""
    # Direct path to stockfish.exe in the project directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    stockfish_path = os.path.join(current_dir, "stockfish.exe")
    
    if os.path.exists(stockfish_path):
        return stockfish_path
    
    # Fallback: check if stockfish is in PATH
    import shutil
    system_stockfish = shutil.which("stockfish")
    if system_stockfish:
        return system_stockfish
    
    return None

def main():
    """Main entry point for the Chess Helper application."""
    parser = argparse.ArgumentParser(
        description="Chess Helper - Analyze your chess games with engine assistance",
        add_help=False  # We'll handle help ourselves
    )
    
    parser.add_argument(
        "--cli", 
        action="store_true", 
        help="Use command-line interface"
    )
    
    parser.add_argument(
        "--stockfish-path", 
        type=str, 
        help="Path to Stockfish executable"
    )
    
    parser.add_argument(
        "--help", 
        action="store_true", 
        help="Show detailed help information"
    )
    
    args = parser.parse_args()
    
    if args.help:
        print_help()
        return
    
    print("Chess Helper - Starting up...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Find Stockfish if path not provided
    stockfish_path = args.stockfish_path
    if not stockfish_path:
        stockfish_path = find_stockfish()
        if stockfish_path:
            print(f"Found Stockfish at: {stockfish_path}")
        else:
            print("Warning: Stockfish not found. Analysis features will be disabled.")
            print("Download from: https://stockfishchess.org/download/")
    
    # Launch appropriate interface
    try:
        if args.cli:
            print("Starting CLI mode...")
            from cli_interface import ChessCliInterface
            cli = ChessCliInterface(stockfish_path)
            cli.run()
        else:
            print("Starting GUI mode...")
            from gui import ChessGUI
            gui = ChessGUI(stockfish_path)
            gui.run()
            
    except KeyboardInterrupt:
        print("\nShutting down Chess Helper...")
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting Chess Helper: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()