"""Simple text menu for the Mini Arcade scaffold."""

from src.utils.constants import ARCADE_TITLE, GAME_NAMES


def main() -> None:
    """Display the games currently planned for the arcade."""
    print(ARCADE_TITLE)
    print("=" * len(ARCADE_TITLE))
    for number, game_name in enumerate(GAME_NAMES, start=1):
        print(f"{number}. {game_name}")
    print("\nGame implementations are coming soon.")


if __name__ == "__main__":
    main()
