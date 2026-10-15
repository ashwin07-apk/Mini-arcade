"""Logic and shared-loop tests for Mini Arcade."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame

from src.games.memory_match.game import (
    MISMATCH_DELAY_MS,
    GameState,
    MemoryMatchGame,
)
from src.games.rock_paper_scissors.game import (
    RockPaperScissorsGame,
    decide_winner,
)
from src.games.snake.game import (
    BASE_MOVE_INTERVAL_MS,
    GRID_COLUMNS,
    GRID_ROWS,
    SnakeGame,
    generate_food,
)
from src.games.tic_tac_toe.game import (
    TicTacToeGame,
    check_winner,
    find_winner,
    is_draw,
)
from src.menu.main_menu import (
    CARD_RECTS,
    EXIT_RECT,
    MainMenu,
    run_application,
)


class PygameTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        pygame.init()
        pygame.display.set_mode((1000, 700))

    @classmethod
    def tearDownClass(cls) -> None:
        pygame.quit()


class TicTacToeTests(PygameTestCase):
    def test_winner_draw_and_occupied_cells(self) -> None:
        self.assertEqual(find_winner(["X", "X", "X", None, None, None, None, None, None]), "X")
        self.assertTrue(check_winner(["X", "X", "X", None, None, None, None, None, None], "X"))
        drawn_board = ["X", "O", "X", "X", "O", "O", "O", "X", "X"]
        self.assertTrue(is_draw(drawn_board))
        self.assertIsNone(find_winner(drawn_board))

        game = TicTacToeGame()
        game.board[0] = "X"
        game.current_player = "O"
        event = pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            {"button": 1, "pos": game_cell_center(0)},
        )
        game.handle_event(event)
        self.assertEqual(game.board[0], "X")
        self.assertEqual(game.current_player, "O")

        game = TicTacToeGame()
        for index in (0, 3, 1, 4, 2):
            game.handle_event(
                pygame.event.Event(
                    pygame.MOUSEBUTTONDOWN,
                    {"button": 1, "pos": game_cell_center(index)},
                )
            )
        self.assertEqual(game.winner, "X")
        game.draw(pygame.display.get_surface())

    def test_restart_and_menu_action(self) -> None:
        game = TicTacToeGame()
        game.board[0] = "X"
        game.reset()
        self.assertEqual(game.board, [None] * 9)
        escape = pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})
        self.assertEqual(game.handle_event(escape), "menu")


class RockPaperScissorsTests(PygameTestCase):
    def test_every_choice_combination(self) -> None:
        expected = {
            ("rock", "rock"): "draw",
            ("rock", "paper"): "computer",
            ("rock", "scissors"): "player",
            ("paper", "rock"): "player",
            ("paper", "paper"): "draw",
            ("paper", "scissors"): "computer",
            ("scissors", "rock"): "computer",
            ("scissors", "paper"): "player",
            ("scissors", "scissors"): "draw",
        }
        for choices, result in expected.items():
            with self.subTest(choices=choices):
                self.assertEqual(decide_winner(*choices), result)

    def test_score_and_replay(self) -> None:
        game = RockPaperScissorsGame(chooser=lambda choices: "scissors")
        game.play("rock")
        self.assertEqual(game.player_score, 1)
        self.assertEqual(game.result, "player")
        game.draw(pygame.display.get_surface())
        game.reset_round()
        self.assertEqual(game.player_score, 1)
        self.assertIsNone(game.result)
        with self.assertRaises(ValueError):
            game.play("papaer")


class MemoryMatchTests(PygameTestCase):
    def test_matching_mismatch_limits_and_win(self) -> None:
        game = MemoryMatchGame()
        pairs: dict[int, list[int]] = {}
        for index, card in enumerate(game.cards):
            pairs.setdefault(card.pair_id, []).append(index)
        self.assertEqual(len(game.cards), 16)
        self.assertEqual(len(pairs), 8)
        self.assertTrue(all(len(indexes) == 2 for indexes in pairs.values()))

        pair = next(iter(pairs.values()))
        game.select_card(pair[0])
        game.select_card(pair[0])
        game.select_card(pair[1])
        self.assertEqual(game.moves, 1)
        self.assertEqual(game.state, GameState.CHECKING_MATCH)
        game.select_card(next(i for i in range(16) if i not in pair))
        self.assertEqual(len(game.selected_indices), 2)
        game.update(MISMATCH_DELAY_MS - 1)
        self.assertEqual(game.matches, 0)
        game.update(1)
        self.assertEqual(game.matches, 1)
        self.assertTrue(all(game.cards[index].matched for index in pair))

        game.reset()
        indexes_by_pair: dict[int, list[int]] = {}
        for index, card in enumerate(game.cards):
            indexes_by_pair.setdefault(card.pair_id, []).append(index)
        for indexes in indexes_by_pair.values():
            game.select_card(indexes[0])
            game.select_card(indexes[1])
            game.update(MISMATCH_DELAY_MS)
        self.assertEqual(game.matches, 8)
        self.assertEqual(game.moves, 8)
        self.assertEqual(game.state, GameState.GAME_WON)
        game.draw(pygame.display.get_surface())

    def test_mismatch_turns_back_over_and_restart(self) -> None:
        game = MemoryMatchGame()
        indexes = [
            (a, b)
            for a in range(len(game.cards))
            for b in range(a + 1, len(game.cards))
            if game.cards[a].pair_id != game.cards[b].pair_id
        ][0]
        game.select_card(indexes[0])
        game.select_card(indexes[1])
        game.update(MISMATCH_DELAY_MS - 1)
        self.assertTrue(game.cards[indexes[0]].revealed)
        game.update(1)
        self.assertFalse(game.cards[indexes[0]].revealed)
        game.reset()
        self.assertEqual((game.moves, game.matches), (0, 0))
        self.assertTrue(all(not card.revealed for card in game.cards))

    def test_reset_shuffles_a_new_card_order(self) -> None:
        game = MemoryMatchGame()
        expected = list(reversed(list(range(8)) * 2))
        with patch(
            "src.games.memory_match.game.random.shuffle",
            side_effect=lambda values: values.reverse(),
        ):
            game.reset()
        self.assertEqual([card.pair_id for card in game.cards], expected)


class SnakeTests(PygameTestCase):
    def test_food_never_occupies_snake_and_full_board(self) -> None:
        snake = [(1, 0)]
        self.assertEqual(
            generate_food(snake, columns=2, rows=1, chooser=lambda cells: cells[0]),
            (0, 0),
        )
        full_board = [(x, y) for y in range(2) for x in range(2)]
        self.assertIsNone(generate_food(full_board, columns=2, rows=2))

    def test_growth_wall_and_self_collision(self) -> None:
        game = SnakeGame(chooser=lambda cells: cells[0])
        game.snake = [(5, 5), (4, 5), (3, 5)]
        game.direction = game.next_direction = (1, 0)
        game.food = (6, 5)
        game.update(BASE_MOVE_INTERVAL_MS)
        self.assertEqual(game.snake[0], (6, 5))
        self.assertEqual(len(game.snake), 4)
        self.assertEqual(game.score, 1)
        self.assertNotIn(game.food, game.snake)

        game.reset()
        game.snake = [(GRID_COLUMNS - 1, 0), (GRID_COLUMNS - 2, 0)]
        game.direction = game.next_direction = (1, 0)
        game.update(BASE_MOVE_INTERVAL_MS)
        self.assertTrue(game.game_over)

        game.reset()
        game.snake = [(2, 2), (2, 3), (1, 3), (1, 2)]
        game.direction = game.next_direction = (0, 1)
        game.food = (GRID_COLUMNS - 1, GRID_ROWS - 1)
        game.update(BASE_MOVE_INTERVAL_MS)
        self.assertTrue(game.game_over)

    def test_restart_after_game_over(self) -> None:
        game = SnakeGame()
        game.score = 4
        game.game_over = True
        game.handle_event(
            pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_r})
        )
        self.assertFalse(game.game_over)
        self.assertEqual(game.score, 0)
        self.assertEqual(len(game.snake), 3)

    def test_filling_board_ends_as_a_win(self) -> None:
        game = SnakeGame()
        last_cell = (1, 0)
        game.snake = [(0, 0)] + [
            (x, y)
            for y in range(GRID_ROWS)
            for x in range(GRID_COLUMNS)
            if (x, y) not in ((0, 0), last_cell)
        ]
        game.direction = game.next_direction = (1, 0)
        game.food = last_cell
        game.update(BASE_MOVE_INTERVAL_MS)
        self.assertTrue(game.game_over)
        self.assertTrue(game.won)
        self.assertIsNone(game.food)
        self.assertEqual(len(game.snake), GRID_COLUMNS * GRID_ROWS)
        game.draw(pygame.display.get_surface())


class ApplicationTests(PygameTestCase):
    def test_menu_cards_exit_and_repeated_game_switching(self) -> None:
        menu = MainMenu()
        click = lambda pos: pygame.event.Event(
            pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": pos}
        )
        for game_id, rect in CARD_RECTS.items():
            with self.subTest(game_id=game_id):
                self.assertEqual(menu.handle_event(click(rect.center)), game_id)
        self.assertEqual(menu.handle_event(click(EXIT_RECT.center)), "exit")

        batches = [
            [click(CARD_RECTS["tic_tac_toe"].center)],
            [pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})],
            [click(CARD_RECTS["rock_paper_scissors"].center)],
            [pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})],
            [click(CARD_RECTS["memory_match"].center)],
            [pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})],
            [click(CARD_RECTS["snake"].center)],
            [pygame.event.Event(pygame.KEYDOWN, {"key": pygame.K_ESCAPE})],
            [pygame.event.Event(pygame.QUIT)],
        ]
        with patch("pygame.event.get", side_effect=batches):
            run_application()
        self.assertFalse(pygame.get_init())

        with patch("pygame.event.get", return_value=[click(EXIT_RECT.center)]):
            run_application()
        self.assertFalse(pygame.get_init())


def game_cell_center(index: int) -> tuple[int, int]:
    from src.games.tic_tac_toe.game import BOARD_RECT, CELL_SIZE

    row, column = divmod(index, 3)
    return (
        BOARD_RECT.left + column * CELL_SIZE + CELL_SIZE // 2,
        BOARD_RECT.top + row * CELL_SIZE + CELL_SIZE // 2,
    )


if __name__ == "__main__":
    unittest.main()
