"""Graphical main menu and the application-owned Pygame event loop."""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

import pygame

from src.games.memory_match.game import MemoryMatchGame
from src.games.rock_paper_scissors.game import RockPaperScissorsGame
from src.games.snake.game import SnakeGame
from src.games.tic_tac_toe.game import TicTacToeGame
from src.utils.constants import (
    BACKGROUND,
    CARD,
    FPS,
    MUTED,
    PANEL,
    PRIMARY,
    SCREEN_SIZE,
    SECONDARY,
    TEXT,
)
from src.utils.helpers import draw_button, draw_panel, draw_text


CARD_RECTS = {
    "tic_tac_toe": pygame.Rect(195, 225, 280, 145),
    "rock_paper_scissors": pygame.Rect(525, 225, 280, 145),
    "memory_match": pygame.Rect(195, 400, 280, 145),
    "snake": pygame.Rect(525, 400, 280, 145),
}
EXIT_RECT = pygame.Rect(425, 590, 150, 48)
GAME_CARDS = (
    ("tic_tac_toe", "TIC-TAC-TOE", "A classic for two players", "X O"),
    ("rock_paper_scissors", "ROCK PAPER SCISSORS", "Choose your move", "R P S"),
    ("memory_match", "MEMORY MATCH", "Find all eight pairs", "? ?"),
    ("snake", "SNAKE", "Grow without crashing", "S"),
)


class ArcadeGame(Protocol):
    """Methods each game provides to the shared application loop."""

    def handle_event(self, event: pygame.event.Event) -> str | None: ...

    def update(self, dt_ms: int) -> None: ...

    def draw(self, screen: pygame.Surface) -> None: ...


GAME_FACTORIES: dict[str, Callable[[], ArcadeGame]] = {
    "tic_tac_toe": TicTacToeGame,
    "rock_paper_scissors": RockPaperScissorsGame,
    "memory_match": MemoryMatchGame,
    "snake": SnakeGame,
}


class MainMenu:
    """Draws and handles the menu without owning the Pygame window."""

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "exit"
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None
        for game_id, rect in CARD_RECTS.items():
            if rect.collidepoint(event.pos):
                return game_id
        if EXIT_RECT.collidepoint(event.pos):
            return "exit"
        return None

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill(BACKGROUND)
        title_font = pygame.font.SysFont("segoeui", 46, bold=True)
        subtitle_font = pygame.font.SysFont("segoeui", 17, bold=True)
        card_title_font = pygame.font.SysFont("segoeui", 19, bold=True)
        body_font = pygame.font.SysFont("segoeui", 14)
        icon_font = pygame.font.SysFont("segoeui", 24, bold=True)
        button_font = pygame.font.SysFont("segoeui", 15, bold=True)

        draw_panel(screen, pygame.Rect(130, 28, 740, 150), color=PANEL)
        draw_text(screen, "MINI ARCADE", title_font, TEXT, (500, 83))
        draw_text(screen, "CHOOSE YOUR GAME", subtitle_font, SECONDARY, (500, 137))

        mouse_pos = pygame.mouse.get_pos()
        for game_id, title, description, icon in GAME_CARDS:
            rect = CARD_RECTS[game_id]
            hovered = rect.collidepoint(mouse_pos)
            border = SECONDARY if hovered else (62, 78, 111)
            draw_panel(
                screen,
                rect,
                color=(37, 49, 78) if hovered else CARD,
                border_color=border,
                radius=18,
            )
            pygame.draw.circle(screen, PRIMARY, (rect.left + 47, rect.centery), 26)
            draw_text(screen, icon, icon_font, TEXT, (rect.left + 47, rect.centery))
            draw_text(
                screen,
                title,
                card_title_font,
                TEXT,
                (rect.left + 88, rect.top + 52),
                center=False,
            )
            draw_text(
                screen,
                description,
                body_font,
                MUTED,
                (rect.left + 88, rect.top + 83),
                center=False,
            )
            draw_text(
                screen,
                "PLAY  >",
                body_font,
                SECONDARY,
                (rect.right - 55, rect.bottom - 25),
            )

        draw_button(
            screen,
            EXIT_RECT,
            "EXIT",
            mouse_pos,
            color=(91, 45, 64),
            font=button_font,
        )
        draw_text(
            screen,
            "Press ESC to exit",
            body_font,
            MUTED,
            (500, 665),
        )


def run_application() -> None:
    """Create the one application window and run the centralized event loop."""
    pygame.init()
    try:
        screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Mini Arcade")
        clock = pygame.time.Clock()
        menu = MainMenu()
        current_game: ArcadeGame | None = None
        running = True

        while running:
            dt_ms = clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if current_game is None:
                    action = menu.handle_event(event)
                    if action == "exit":
                        running = False
                        break
                    if action in GAME_FACTORIES:
                        current_game = GAME_FACTORIES[action]()
                else:
                    action = current_game.handle_event(event)
                    if action == "menu":
                        current_game = None

            if not running:
                break

            if current_game is None:
                menu.draw(screen)
            else:
                current_game.update(dt_ms)
                current_game.draw(screen)
            pygame.display.flip()
    finally:
        pygame.quit()


def main() -> None:
    """Public entry point used by ``main.py``."""
    run_application()
