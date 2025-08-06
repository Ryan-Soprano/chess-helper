# Chess Helper Application

A Python chess analysis tool with Stockfish engine integration for move recommendations and game analysis. Perfect for analyzing positions, studying games, and improving your chess skills.

## Features

- **Visual GUI**: Interactive chessboard with drag-and-drop movement
- **Engine Analysis**: Real-time Stockfish analysis with best moves and evaluations
- **Move History**: Track and review all moves in your games
- **Multiple Interfaces**: Both GUI and CLI modes available
- **Game Management**: Save/load games in PGN format
- **Coordinate Display**: Square coordinates for chess novices
- **Player Color Selection**: Choose to play as White or Black

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Ryan-Soprano/chess-helper.git
   cd chess-helper
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Stockfish Engine:**
   - **Windows**: Download from [Stockfish official site](https://stockfishchess.org/download/) and place `stockfish.exe` in the project directory
   - **Linux/Mac**: Install via package manager or download binary
   ```bash
   # Ubuntu/Debian
   sudo apt install stockfish
   
   # macOS
   brew install stockfish
   ```

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
- tkinter (usually included with Python)
- python-chess
- Stockfish engine binary

## Contributing

Feel free to submit issues and pull requests to improve the Chess Helper application!

## Troubleshooting

If you encounter any issues with the Stockfish engine, ensure that:
1. The `stockfish.exe` file is in the same directory as the Python scripts
2. You have the required Python packages installed
3. Your system allows execution of the Stockfish binary

For more help, run the application with the `--help` flag.
