"""Graphical Rock Paper Scissors for the shared Mini Arcade window."""

from __future__ import annotations

import random
from collections.abc import Callable

import pygame

from src.utils.constants import (
    BACKGROUND,
    CARD,
    DANGER,
    MUTED,
    PANEL,
    PRIMARY,
    SECONDARY,
    SUCCESS,
    TEXT,
)
from src.utils.helpers import draw_button, draw_panel, draw_text


CHOICES = ("rock", "paper", "scissors")
CHOICE_RECTS = {
    choice: pygame.Rect(185 + index * 215, 292, 190, 120)
    for index, choice in enumerate(CHOICES)
}
REPLAY_RECT = pygame.Rect(352, 590, 140, 46)
MENU_RECT = pygame.Rect(508, 590, 140, 46)


def decide_winner(player: str, computer: str) -> str:
    """Return ``player``, ``computer``, or ``draw`` for a valid round."""
    if player not in CHOICES or computer not in CHOICES:
        raise ValueError("Choices must be rock, paper, or scissors.")
    if player == computer:
        return "draw"
    player_wins = {
        ("rock", "scissors"),
        ("paper", "rock"),
        ("scissors", "paper"),
    }
    return "player" if (player, computer) in player_wins else "computer"


class RockPaperScissorsGame:
    """One-player Rock Paper Scissors with cumulative score and replay."""

    def __init__(self, chooser: Callable[[tuple[str, ...]], str] | None = None) -> None:
        self.chooser = chooser or random.choice
        self.player_score = 0
        self.computer_score = 0
        self.reset_round()

    def reset_round(self) -> None:
        """Clear the current choices while keeping the score."""
        self.player_choice: str | None = None
        self.computer_choice: str | None = None
        self.result: str | None = None

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Handle a choice, replay, or request to return to the menu."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "menu"
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        if MENU_RECT.collidepoint(event.pos):
            return "menu"
        if REPLAY_RECT.collidepoint(event.pos):
            self.reset_round()
            return None
        if self.result is not None:
            return None

        for choice, rect in CHOICE_RECTS.items():
            if rect.collidepoint(event.pos):
                self.play(choice)
                break
        return None

    def play(self, player_choice: str) -> None:
        """Play one round and update the score."""
        if player_choice not in CHOICES:
            raise ValueError("Choice must be rock, paper, or scissors.")
        if self.result is not None:
            return
        self.player_choice = player_choice
        self.computer_choice = self.chooser(CHOICES)
        self.result = decide_winner(self.player_choice, self.computer_choice)
        if self.result == "player":
            self.player_score += 1
        elif self.result == "computer":
            self.computer_score += 1

    def update(self, dt_ms: int) -> None:
        """Rock Paper Scissors has no time-based updates."""

    def draw(self, screen: pygame.Surface) -> None:
        """Draw choices, result, score, and navigation controls."""
        screen.fill(BACKGROUND)
        title_font = pygame.font.SysFont("segoeui", 34, bold=True)
        body_font = pygame.font.SysFont("segoeui", 20)
        label_font = pygame.font.SysFont("segoeui", 16, bold=True)
        choice_font = pygame.font.SysFont("segoeui", 22, bold=True)
        button_font = pygame.font.SysFont("segoeui", 15, bold=True)

        draw_panel(screen, pygame.Rect(175, 28, 650, 122), color=PANEL)
        draw_text(screen, "ROCK  PAPER  SCISSORS", title_font, TEXT, (500, 67))
        draw_text(
            screen,
            f"YOU  {self.player_score}     :     {self.computer_score}  CPU",
            body_font,
            SECONDARY,
            (500, 117),
        )
        draw_text(screen, "Choose your move", body_font, MUTED, (500, 218))

        mouse_pos = pygame.mouse.get_pos()
        symbols = {"rock": "R", "paper": "P", "scissors": "S"}
        for choice, rect in CHOICE_RECTS.items():
            hovered = rect.collidepoint(mouse_pos)
            border = SECONDARY if hovered else (61, 78, 112)
            draw_panel(
                screen,
                rect,
                color=CARD,
                border_color=border,
                radius=18,
            )
            draw_text(
                screen,
                symbols[choice],
                title_font,
                PRIMARY if choice == "paper" else SECONDARY,
                (rect.centerx, rect.centery - 17),
            )
            draw_text(
                screen,
                choice.upper(),
                label_font,
                TEXT,
                (rect.centerx, rect.bottom - 25),
            )

        if self.result is None:
            status = "Select Rock, Paper, or Scissors to play."
            status_color = MUTED
        elif self.result == "draw":
            status = f"You both chose {self.player_choice}. It's a draw!"
            status_color = SECONDARY
        elif self.result == "player":
            status = f"{self.player_choice.title()} beats {self.computer_choice}. You win!"
            status_color = SUCCESS
        else:
            status = f"{self.computer_choice.title()} beats {self.player_choice}. CPU wins!"
            status_color = DANGER
        draw_text(screen, status, body_font, status_color, (500, 485))

        draw_button(
            screen,
            REPLAY_RECT,
            "PLAY AGAIN",
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
