"""Keyboard-controlled Snake for the shared Mini Arcade window."""

from __future__ import annotations

import random
from collections.abc import Callable, Sequence

import pygame

from src.utils.constants import (
    BACKGROUND,
    CARD,
    DANGER,
    MUTED,
    PANEL,
    PRIMARY,
    SCREEN_WIDTH,
    SECONDARY,
    SUCCESS,
    TEXT,
)
from src.utils.helpers import draw_button, draw_panel, draw_text


CELL_SIZE = 22
GRID_COLUMNS = 32
GRID_ROWS = 20
GRID_LEFT = (SCREEN_WIDTH - GRID_COLUMNS * CELL_SIZE) // 2
GRID_TOP = 145
GRID_RECT = pygame.Rect(
    GRID_LEFT,
    GRID_TOP,
    GRID_COLUMNS * CELL_SIZE,
    GRID_ROWS * CELL_SIZE,
)
RESTART_RECT = pygame.Rect(352, 625, 140, 46)
MENU_RECT = pygame.Rect(508, 625, 140, 46)
BASE_MOVE_INTERVAL_MS = 120
MIN_MOVE_INTERVAL_MS = 60
DIRECTIONS = {
    pygame.K_UP: (0, -1),
    pygame.K_w: (0, -1),
    pygame.K_DOWN: (0, 1),
    pygame.K_s: (0, 1),
    pygame.K_LEFT: (-1, 0),
    pygame.K_a: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_d: (1, 0),
}


def generate_food(
    snake: Sequence[tuple[int, int]],
    *,
    columns: int = GRID_COLUMNS,
    rows: int = GRID_ROWS,
    chooser: Callable[[Sequence[tuple[int, int]]], tuple[int, int]] = random.choice,
) -> tuple[int, int] | None:
    """Choose an unoccupied grid cell, or return None when the board is full."""
    occupied = set(snake)
    free_cells = [
        (x, y)
        for y in range(rows)
        for x in range(columns)
        if (x, y) not in occupied
    ]
    return chooser(free_cells) if free_cells else None


class SnakeGame:
    """Owns snake movement, collision checks, score, and drawing."""

    def __init__(self, chooser: Callable = random.choice) -> None:
        self.chooser = chooser
        self.reset()

    def reset(self) -> None:
        """Start a fresh run from the center of the board."""
        center_x, center_y = GRID_COLUMNS // 2, GRID_ROWS // 2
        self.snake = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y),
        ]
        self.direction = (1, 0)
        self.next_direction = self.direction
        self.food = self._new_food()
        self.score = 0
        self.game_over = False
        self.won = False
        self.elapsed_ms = 0

    @property
    def move_interval_ms(self) -> int:
        """Increase the original game's speed by two steps every five foods."""
        speed_steps = self.score // 5
        return max(MIN_MOVE_INTERVAL_MS, BASE_MOVE_INTERVAL_MS - speed_steps * 10)

    def _new_food(self) -> tuple[int, int] | None:
        return generate_food(
            self.snake,
            columns=GRID_COLUMNS,
            rows=GRID_ROWS,
            chooser=self.chooser,
        )

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Handle steering, restart, and main-menu navigation."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
            if self.game_over and event.key in (
                pygame.K_r,
                pygame.K_RETURN,
                pygame.K_SPACE,
            ):
                self.reset()
                return None
            requested = DIRECTIONS.get(event.key)
            if requested and requested != (-self.direction[0], -self.direction[1]):
                self.next_direction = requested
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if MENU_RECT.collidepoint(event.pos):
                return "menu"
            if RESTART_RECT.collidepoint(event.pos):
                self.reset()
        return None

    def update(self, dt_ms: int) -> None:
        """Advance at fixed movement intervals without blocking the app loop."""
        if self.game_over:
            return
        self.elapsed_ms += dt_ms
        while self.elapsed_ms >= self.move_interval_ms and not self.game_over:
            self.elapsed_ms -= self.move_interval_ms
            self._move()

    def _move(self) -> None:
        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = (head_x + dx, head_y + dy)
        eating = new_head == self.food

        if not (0 <= new_head[0] < GRID_COLUMNS and 0 <= new_head[1] < GRID_ROWS):
            self.game_over = True
            return

        body_to_check = self.snake if eating else self.snake[:-1]
        if new_head in body_to_check:
            self.game_over = True
            return

        self.snake.insert(0, new_head)
        if eating:
            self.score += 1
            self.food = self._new_food()
            if self.food is None:
                self.game_over = True
                self.won = True
        else:
            self.snake.pop()

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the board, score, and game-over controls."""
        screen.fill(BACKGROUND)
        title_font = pygame.font.SysFont("segoeui", 32, bold=True)
        body_font = pygame.font.SysFont("segoeui", 17)
        button_font = pygame.font.SysFont("segoeui", 15, bold=True)

        draw_panel(screen, pygame.Rect(180, 22, 640, 105), color=PANEL)
        draw_text(screen, "SNAKE", title_font, TEXT, (500, 57))
        draw_text(screen, f"SCORE  {self.score}", body_font, SECONDARY, (500, 98))
        draw_panel(screen, GRID_RECT.inflate(12, 12), color=PANEL, radius=16)
        pygame.draw.rect(screen, (12, 20, 38), GRID_RECT, border_radius=10)

        for x in range(GRID_COLUMNS):
            for y in range(GRID_ROWS):
                cell_rect = self._cell_rect((x, y))
                pygame.draw.rect(screen, (20, 31, 52), cell_rect, width=1)

        if self.food is not None:
            food_rect = self._cell_rect(self.food).inflate(-5, -5)
            pygame.draw.ellipse(screen, DANGER, food_rect)
        for index, segment in enumerate(self.snake):
            segment_rect = self._cell_rect(segment).inflate(-2, -2)
            color = SECONDARY if index == 0 else SUCCESS
            pygame.draw.rect(screen, color, segment_rect, border_radius=6)

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

        if self.game_over:
            shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
            shade.fill((4, 8, 20, 190))
            screen.blit(shade, (0, 0))
            panel = pygame.Rect(300, 250, 400, 260)
            draw_panel(screen, panel, color=PANEL, border_color=(64, 83, 119), radius=24)
            message = "BOARD CLEARED!" if self.won else "GAME OVER"
            color = SUCCESS if self.won else DANGER
            draw_text(screen, message, title_font, color, (500, 315))
            draw_text(screen, f"Final score: {self.score}", body_font, TEXT, (500, 360))
            draw_text(
                screen,
                "Press R or click Restart to play again",
                body_font,
                MUTED,
                (500, 390),
            )

    @staticmethod
    def _cell_rect(position: tuple[int, int]) -> pygame.Rect:
        x, y = position
        return pygame.Rect(
            GRID_LEFT + x * CELL_SIZE,
            GRID_TOP + y * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
        )
