# Chess Helper Application

A Python app to help during home chess games with move analysis and tracking.

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Stockfish Engine:**
   The Stockfish engine (`stockfish.exe`) is already included in this project directory. No additional setup required!

## Usage

```bash
python main.py                    # Start GUI version
python main.py --cli              # Start command-line version
python main.py --stockfish-path /path/to/stockfish  # Use custom Stockfish path
```

## GUI Features

- Visual chessboard with drag-and-drop piece movement
- Manual move input box for algebraic notation (e4, Nf3, O-O, etc.)
- Real-time engine analysis showing best moves and evaluation
- Move history tracking
- Game save/load (PGN format)
- Undo/redo functionality

## CLI Features

- Command-line interface for manual move input
- Engine analysis after each move
- Move history and game tracking
- All standard chess commands (help, undo, save, etc.)

## Commands (CLI mode)

| Command | Description |
|---------|-------------|
| `[move]` | Make a move (e.g., e4, Nf3, O-O) |
| `help` | Show available commands |
| `board` | Display current position |
| `moves` | Show legal moves |
| `history` | Show move history |
| `undo` | Undo last move |
| `analysis` | Toggle engine analysis |
| `eval` | Detailed position evaluation |
| `save [file]` | Save game as PGN |
| `reset` | Start new game |
| `quit` | Exit the application |

## Requirements

- Python 3.7+
- python-chess
- stockfish (Python package)
- tkinter (usually included with Python)

## Troubleshooting

If you encounter any issues with the Stockfish engine, ensure that:
1. The `stockfish.exe` file is in the same directory as the Python scripts
2. You have the required Python packages installed
3. Your system allows execution of the Stockfish binary

For more help, run the application with the `--help` flag.
