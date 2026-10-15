"""Mouse-controlled Tic-Tac-Toe for the shared Mini Arcade window."""

from __future__ import annotations

import pygame

from src.utils.constants import (
    BACKGROUND,
    CARD,
    MUTED,
    PANEL,
    PRIMARY,
    SECONDARY,
    SUCCESS,
    TEXT,
)
from src.utils.helpers import draw_button, draw_panel, draw_text


WINNING_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)
BOARD_RECT = pygame.Rect(350, 180, 300, 300)
CELL_SIZE = BOARD_RECT.width // 3
RESTART_RECT = pygame.Rect(360, 535, 130, 46)
MENU_RECT = pygame.Rect(510, 535, 130, 46)
PLAY_AGAIN_RECT = pygame.Rect(365, 405, 270, 46)
OVERLAY_MENU_RECT = pygame.Rect(365, 465, 270, 46)


def find_winner(board: list[str | None]) -> str | None:
    """Return the winning mark, if a complete row, column, or diagonal exists."""
    if len(board) != 9:
        raise ValueError("A Tic-Tac-Toe board must contain nine cells.")
    for first, second, third in WINNING_LINES:
        mark = board[first]
        if mark is not None and mark == board[second] == board[third]:
            return mark
    return None


def check_winner(board: list[str | None], player: str) -> bool:
    """Compatibility helper that checks for a particular player's win."""
    return find_winner(board) == player


def is_draw(board: list[str | None]) -> bool:
    """A draw is a full board with no winner."""
    return len(board) == 9 and all(cell is not None for cell in board) and find_winner(board) is None


class TicTacToeGame:
    """Owns one Tic-Tac-Toe round and follows the shared game interface."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Start a new round."""
        self.board: list[str | None] = [None] * 9
        self.current_player = "X"
        self.winner: str | None = None
        self.is_draw = False

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Handle input; return ``menu`` when the player requests navigation."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "menu"
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        if self.winner is not None or self.is_draw:
            if PLAY_AGAIN_RECT.collidepoint(event.pos):
                self.reset()
            elif OVERLAY_MENU_RECT.collidepoint(event.pos):
                return "menu"
            return None

        if RESTART_RECT.collidepoint(event.pos):
            self.reset()
            return None
        if MENU_RECT.collidepoint(event.pos):
            return "menu"
        if not BOARD_RECT.collidepoint(event.pos):
            return None

        column = (event.pos[0] - BOARD_RECT.left) // CELL_SIZE
        row = (event.pos[1] - BOARD_RECT.top) // CELL_SIZE
        index = row * 3 + column
        if self.board[index] is None:
            self.board[index] = self.current_player
            self.winner = find_winner(self.board)
            self.is_draw = self.winner is None and is_draw(self.board)
            if self.winner is None and not self.is_draw:
                self.current_player = "O" if self.current_player == "X" else "X"
        return None

    def update(self, dt_ms: int) -> None:
        """Tic-Tac-Toe has no time-based updates."""

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the board and round controls."""
        screen.fill(BACKGROUND)
        title_font = pygame.font.SysFont("segoeui", 34, bold=True)
        body_font = pygame.font.SysFont("segoeui", 19)
        mark_font = pygame.font.SysFont("segoeui", 64, bold=True)
        button_font = pygame.font.SysFont("segoeui", 15, bold=True)

        draw_panel(screen, pygame.Rect(210, 30, 580, 112), color=PANEL)
        draw_text(screen, "TIC-TAC-TOE", title_font, TEXT, (500, 64))
        if self.winner:
            status, status_color = f"Player {self.winner} wins!", SUCCESS
        elif self.is_draw:
            status, status_color = "It's a draw!", SECONDARY
        else:
            status, status_color = f"Player {self.current_player}'s turn", MUTED
        draw_text(screen, status, body_font, status_color, (500, 108))

        pygame.draw.rect(screen, CARD, BOARD_RECT, border_radius=18)
        for line in (1, 2):
            offset = line * CELL_SIZE
            pygame.draw.line(
                screen,
                (71, 85, 115),
                (BOARD_RECT.left + offset, BOARD_RECT.top + 14),
                (BOARD_RECT.left + offset, BOARD_RECT.bottom - 14),
                3,
            )
            pygame.draw.line(
                screen,
                (71, 85, 115),
                (BOARD_RECT.left + 14, BOARD_RECT.top + offset),
                (BOARD_RECT.right - 14, BOARD_RECT.top + offset),
                3,
            )

        for index, mark in enumerate(self.board):
            if mark is None:
                continue
            row, column = divmod(index, 3)
            center = (
                BOARD_RECT.left + column * CELL_SIZE + CELL_SIZE // 2,
                BOARD_RECT.top + row * CELL_SIZE + CELL_SIZE // 2,
            )
            draw_text(
                screen,
                mark,
                mark_font,
                SECONDARY if mark == "X" else PRIMARY,
                center,
            )

        mouse_pos = pygame.mouse.get_pos()
        draw_button(
            screen,
            RESTART_RECT,
            "RESTART",
            mouse_pos,
            color=PRIMARY,
            font=button_font,
        )
        draw_button(
            screen,
            MENU_RECT,
            "MAIN MENU",
            mouse_pos,
            color=CARD,
            font=button_font,
        )

        if self.winner is not None or self.is_draw:
            shade = pygame.Surface((1000, 700), pygame.SRCALPHA)
            shade.fill((4, 8, 20, 195))
            screen.blit(shade, (0, 0))
            panel = pygame.Rect(300, 250, 400, 285)
            draw_panel(screen, panel, color=PANEL, border_color=(64, 83, 119), radius=24)
            message = f"PLAYER {self.winner} WINS!" if self.winner else "IT'S A DRAW!"
            color = SUCCESS if self.winner else SECONDARY
            draw_text(screen, message, title_font, color, (500, 315))
            draw_text(screen, "Great game!", body_font, MUTED, (500, 360))
            draw_button(
                screen,
                PLAY_AGAIN_RECT,
                "PLAY AGAIN",
                mouse_pos,
                color=PRIMARY,
                font=button_font,
            )
            draw_button(
                screen,
                OVERLAY_MENU_RECT,
                "MAIN MENU",
                mouse_pos,
                color=CARD,
                font=button_font,
            )
