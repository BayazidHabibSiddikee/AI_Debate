#!/usr/bin/env python3
# tools/connect4.py — wrapper that proxies to games/connect4_ai.py or games/connect4_2p.py
import os, sys
from pathlib import Path
import json
import subprocess

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# File to store the game state (for CLI mode)
STATE_FILE = Path("/tmp/marin_connect4_state.json")

# Constants for the game
COLUMN_COUNT = 7
ROW_COUNT = 6
EMPTY = ""
PLAYER_RED = "R"   # human? 
PLAYER_YELLOW = "Y" # AI?

def new_game():
    return {
        "board": [[EMPTY for _ in range(COLUMN_COUNT)] for _ in range(ROW_COUNT)],
        "next_player": PLAYER_RED,
        "winner": None,
        "game_over": False
    }

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def load_state():
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    return None

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == EMPTY

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == EMPTY:
            return r
    return None

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def winning_move(board, piece):
    # Check horizontal
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    # Check vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    # Check positively sloped diaganols
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    # Check negatively sloped diaganols
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True
    return False

def make_move(state, col):
    """Make a move in column col (0-6). Returns new state or None if invalid."""
    if state["game_over"] or state["winner"] is not None:
        return state  # game already over
    if col < 0 or col >= COLUMN_COUNT:
        return None
    board = state["board"]
    if not is_valid_location(board, col):
        return None
    row = get_next_open_row(board, col)
    piece = state["next_player"]
    # Make a deep copy of board
    new_board = [row_copy[:] for row_copy in board]
    drop_piece(new_board, row, col, piece)
    winner = winning_move(new_board, piece)
    game_over = winner is not None or all(all(cell != EMPTY for cell in row) for row in new_board)
    next_player = PLAYER_YELLOW if state["next_player"] == PLAYER_RED else PLAYER_RED
    return {
        "board": new_board,
        "next_player": next_player,
        "winner": winner if winner else None,
        "game_over": game_over
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Connect Four game - CLI for state and moves')
    parser.add_argument('--get-state', action='store_true', help='Get the current state as JSON')
    parser.add_argument('--move', type=int, help='Make a move (column 0-6) and get the new state as JSON')
    parser.add_argument('--gui', action='store_true', help='Launch the GUI version (default if no CLI args)')
    parser.add_argument('--two', action='store_true', help='Two player mode (for GUI)')
    args = parser.parse_args()

    if args.get_state:
        state = load_state()
        if state is None:
            state = new_game()
            save_state(state)
        print(json.dumps(state))
        return

    if args.move is not None:
        state = load_state()
        if state is None:
            state = new_game()
        new_state = make_move(state, args.move)
        if new_state is None:
            print(json.dumps({"error": "Invalid move"}), file=sys.stderr)
            sys.exit(1)
        save_state(new_state)
        print(json.dumps(new_state))
        return

    # Default: launch GUI
    _dn = os.open(os.devnull, os.O_WRONLY)
    _se = os.dup(2)
    os.dup2(_dn, 2)
    try:
        from games.connect4_ai import ConnectFour as ConnectFourAI
        from games.connect4_2p import ConnectFourTwoPlayer
    finally:
        os.dup2(_se, 2)
        os.close(_se)
        os.close(_dn)

    is_2p = len(sys.argv) > 1 and sys.argv[1] == '--two' or args.two
    game = ConnectFourTwoPlayer() if is_2p else ConnectFourAI()
    game.start()

if __name__ == '__main__':
    main()