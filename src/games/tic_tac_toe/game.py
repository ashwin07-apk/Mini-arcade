"""Tic-Tac-Toe game implementation."""

def print_board(board):
    print()
    for i in range(0, 9, 3):
        print(" | ".join(board[i:i + 3]))
        if i < 6:
            print("---+---+---")
    print()


def check_winner(board, player):
    winning_combinations = [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6)
    ]

    for a, b, c in winning_combinations:
        if board[a] == board[b] == board[c] == player:
            return True
    return False


def play():
    board = [str(i) for i in range(1, 10)]
    current_player = "X"

    print("\n=== TIC-TAC-TOE ===")
    print("Choose a position from 1 to 9.")

    while True:
        print_board(board)
        move = input(
            f"Player {current_player}, enter position (1-9): "
        ).strip()

        if move not in "123456789" or len(move) != 1:
            print("Invalid input! Enter a number from 1 to 9.")
            continue

        position = int(move) - 1

        if board[position] in ("X", "O"):
            print("That position is already taken. Try again.")
            continue

        board[position] = current_player

        if check_winner(board, current_player):
            print_board(board)
            print(f"Player {current_player} wins!")
            break

        if all(cell in ("X", "O") for cell in board):
            print_board(board)
            print("It's a draw!")
            break

        current_player = "O" if current_player == "X" else "X"


def main():
    play()


if __name__ == "__main__":
    main()
