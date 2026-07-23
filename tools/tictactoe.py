#!/usr/bin/env python3
# tools/tictactoe.py — wrapper that proxies to games/tiktaktoe.py
import os, sys
from pathlib import Path
import json
import subprocess

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# File to store the game state (for CLI mode)
STATE_FILE = Path("/tmp/marin_tiktaktoe_state.json")

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

def new_game():
    # Start a new game state: 3x3 board, empty, next player is 'X'
    return {
        "board": ["", "", "", "", "", "", "", "", ""],
        "next_player": "X",
        "winner": None,
        "game_over": False
    }

def make_move(state, position):
    """Make a move on the board. Position is 0-8.
    Returns new state or None if invalid."""
    if state["game_over"] or state["winner"] is not None:
        return state  # game already over
    if position < 0 or position > 8:
        return None
    if state["board"][position] != "":
        return None  # cell already taken
    # Make a copy
    new_board = state["board"].copy()
    new_board[position] = state["next_player"]
    # Check for winner
    winner = None
    win_patterns = [
        [0,1,2], [3,4,5], [6,7,8],  # rows
        [0,3,6], [1,4,7], [2,5,8],  # columns
        [0,4,8], [2,4,6]            # diagonals
    ]
    for pattern in win_patterns:
        if new_board[pattern[0]] == new_board[pattern[1]] == new_board[pattern[2]] != "":
            winner = new_board[pattern[0]]
            break
    game_over = winner is not None or all(cell != "" for cell in new_board)
    next_player = "O" if state["next_player"] == "X" else "X"
    return {
        "board": new_board,
        "next_player": next_player,
        "winner": winner,
        "game_over": game_over
    }

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Tic Tac Toe game - CLI for state and moves')
    parser.add_argument('--get-state', action='store_true', help='Get the current state as JSON')
    parser.add_argument('--move', type=int, help='Make a move (0-8) and get the new state as JSON')
    parser.add_argument('--gui', action='store_true', help='Launch the GUI version (default)')
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
        from games.tiktaktoe import launch_game
        launch_game()
    finally:
        os.dup2(_se, 2)
        os.close(_se)
        os.close(_dn)

if __name__ == '__main__':
    main()