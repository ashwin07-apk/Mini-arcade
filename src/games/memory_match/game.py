"""A self-contained Pygame Memory Match game."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum, auto

import pygame

from src.utils.constants import (
    BACKGROUND,
    DANGER,
    MUTED,
    PANEL,
    PRIMARY,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SECONDARY,
    SUCCESS,
    TEXT,
)
from src.utils.helpers import draw_button, draw_text

WINDOW_WIDTH = SCREEN_WIDTH
WINDOW_HEIGHT = SCREEN_HEIGHT
CARD_COLUMNS = 4
CARD_ROWS = 4
PAIR_COUNT = CARD_COLUMNS * CARD_ROWS // 2
CARD_WIDTH = 130
CARD_HEIGHT = 98
CARD_GAP = 16
CARD_FLIP_MS = 150
MISMATCH_DELAY_MS = 850

CARD_BACK = (30, 41, 67)
CARD_FACE = (31, 42, 68)
PAIR_COLORS = (
    (167, 139, 250),
    (34, 211, 238),
    (251, 191, 36),
    (244, 114, 182),
    (74, 222, 128),
    (251, 146, 60),
    (96, 165, 250),
    (232, 121, 249),
)


class GameState(Enum):
    """The three states used while a round is in progress."""

    PLAYING = auto()
    CHECKING_MATCH = auto()
    GAME_WON = auto()


@dataclass
class Card:
    """One card in the randomized grid."""

    pair_id: int
    rect: pygame.Rect
    revealed: bool = False
    matched: bool = False
    flip_started_ms: int | None = None


def _make_cards() -> list[Card]:
    """Create and shuffle two cards for each pair."""
    pair_ids = list(range(PAIR_COUNT)) * 2
    random.shuffle(pair_ids)

    grid_width = CARD_COLUMNS * CARD_WIDTH + (CARD_COLUMNS - 1) * CARD_GAP
    grid_left = (WINDOW_WIDTH - grid_width) // 2
    grid_top = 164
    cards = []

    for index, pair_id in enumerate(pair_ids):
        row, column = divmod(index, CARD_COLUMNS)
        card_rect = pygame.Rect(
            grid_left + column * (CARD_WIDTH + CARD_GAP),
            grid_top + row * (CARD_HEIGHT + CARD_GAP),
            CARD_WIDTH,
            CARD_HEIGHT,
        )
        cards.append(Card(pair_id=pair_id, rect=card_rect))
    return cards


def _button_rects() -> tuple[pygame.Rect, pygame.Rect]:
    """Return the restart and main-menu button rectangles."""
    return (
        pygame.Rect(352, 625, 140, 46),
        pygame.Rect(508, 625, 140, 46),
    )


def _draw_centered_text(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    color: tuple[int, int, int],
    center: tuple[int, int],
) -> None:
    draw_text(surface, text, font, color, center)


def _draw_symbol(
    surface: pygame.Surface,
    pair_id: int,
    center: tuple[int, int],
    color: tuple[int, int, int],
) -> None:
    """Draw a simple vector icon so the game needs no image assets or emoji font."""
    x, y = center
    size = 21

    if pair_id == 0:
        pygame.draw.circle(surface, color, center, size)
    elif pair_id == 1:
        pygame.draw.rect(
            surface,
            color,
            pygame.Rect(x - size, y - size, size * 2, size * 2),
            border_radius=6,
        )
    elif pair_id == 2:
        pygame.draw.polygon(
            surface,
            color,
            ((x, y - size - 2), (x + size + 2, y + size), (x - size - 2, y + size)),
        )
    elif pair_id == 3:
        pygame.draw.polygon(
            surface,
            color,
            ((x, y - size - 3), (x + size + 3, y), (x, y + size + 3), (x - size - 3, y)),
        )
    elif pair_id == 4:
        points = []
        for point in range(10):
            radius = size if point % 2 == 0 else size * 0.45
            angle = -math.pi / 2 + point * math.pi / 5
            points.append((x + math.cos(angle) * radius, y + math.sin(angle) * radius))
        pygame.draw.polygon(surface, color, points)
    elif pair_id == 5:
        points = [
            (
                x + math.cos(-math.pi / 2 + point * math.pi / 3) * size,
                y + math.sin(-math.pi / 2 + point * math.pi / 3) * size,
            )
            for point in range(6)
        ]
        pygame.draw.polygon(surface, color, points)
    elif pair_id == 6:
        pygame.draw.rect(
            surface,
            color,
            pygame.Rect(x - 6, y - size, 12, size * 2),
            border_radius=5,
        )
        pygame.draw.rect(
            surface,
            color,
            pygame.Rect(x - size, y - 6, size * 2, 12),
            border_radius=5,
        )
    else:
        pygame.draw.circle(surface, color, center, size, width=6)


class MemoryMatchGame:
    """Owns the board, score, and rules for one round."""

    def __init__(self) -> None:
        self.cards: list[Card] = []
        self.selected_indices: list[int] = []
        self.state = GameState.PLAYING
        self.moves = 0
        self.matches = 0
        self.hide_cards_at_ms = 0
        self.elapsed_ms = 0
        self.status = "Find all eight matching pairs."
        self.status_color = MUTED
        self.reset()

    def reset(self) -> None:
        """Start a fresh round with a newly shuffled board."""
        self.cards = _make_cards()
        self.selected_indices = []
        self.state = GameState.PLAYING
        self.moves = 0
        self.matches = 0
        self.hide_cards_at_ms = 0
        self.elapsed_ms = 0
        self.status = "Find all eight matching pairs."
        self.status_color = MUTED

    def handle_event(self, event: pygame.event.Event) -> str | None:
        """Handle clicks and keys; return ``menu`` for a menu request."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"
            if event.key == pygame.K_r:
                self.reset()
            return None
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        if self.state is GameState.GAME_WON:
            if pygame.Rect(365, 397, 270, 46).collidepoint(event.pos):
                self.reset()
            elif pygame.Rect(365, 456, 270, 46).collidepoint(event.pos):
                return "menu"
            return None

        restart_rect, menu_rect = _button_rects()
        if menu_rect.collidepoint(event.pos):
            return "menu"
        if restart_rect.collidepoint(event.pos):
            self.reset()
            return None
        if self.state is GameState.PLAYING:
            for index, card in enumerate(self.cards):
                if card.rect.collidepoint(event.pos):
                    self.select_card(index, self.elapsed_ms)
                    break
        return None

    def select_card(self, index: int, now_ms: int | None = None) -> None:
        """Reveal a card, or begin checking once a second card is selected."""
        if now_ms is None:
            now_ms = self.elapsed_ms
        if self.state is not GameState.PLAYING:
            return
        if not 0 <= index < len(self.cards):
            return

        card = self.cards[index]
        if card.revealed or card.matched:
            return

        card.revealed = True
        card.flip_started_ms = now_ms
        self.selected_indices.append(index)

        if len(self.selected_indices) == 2:
            self.moves += 1
            self.state = GameState.CHECKING_MATCH
            self.hide_cards_at_ms = now_ms + MISMATCH_DELAY_MS
            self.status = "Checking your pair..."
            self.status_color = SECONDARY

    def update(self, dt_ms: int) -> None:
        """Resolve the selected pair after the display delay, without blocking."""
        self.elapsed_ms += max(0, dt_ms)
        if (
            self.state is not GameState.CHECKING_MATCH
            or self.elapsed_ms < self.hide_cards_at_ms
        ):
            return

        first = self.cards[self.selected_indices[0]]
        second = self.cards[self.selected_indices[1]]

        if first.pair_id == second.pair_id:
            first.matched = True
            second.matched = True
            self.matches += 1
            self.status = "Match found! Keep going."
            self.status_color = SUCCESS
        else:
            first.revealed = False
            second.revealed = False
            first.flip_started_ms = self.elapsed_ms
            second.flip_started_ms = self.elapsed_ms
            self.status = "Not a match. Try another pair."
            self.status_color = DANGER

        self.selected_indices.clear()
        self.state = (
            GameState.GAME_WON if self.matches == PAIR_COUNT else GameState.PLAYING
        )
        if self.state is GameState.GAME_WON:
            self.status = "Every pair matched!"
            self.status_color = SUCCESS

    def draw(
        self,
        surface: pygame.Surface,
        now_ms: int | None = None,
        mouse_pos: tuple[int, int] | None = None,
    ) -> None:
        """Draw the background, score, cards, buttons, and win overlay."""
        if now_ms is None:
            now_ms = self.elapsed_ms
        if mouse_pos is None:
            mouse_pos = pygame.mouse.get_pos()
        surface.fill(BACKGROUND)
        title_font = pygame.font.SysFont("segoeui", 31, bold=True)
        label_font = pygame.font.SysFont("segoeui", 16, bold=True)
        body_font = pygame.font.SysFont("segoeui", 17)
        card_font = pygame.font.SysFont("segoeui", 29, bold=True)
        small_font = pygame.font.SysFont("segoeui", 12, bold=True)

        pygame.draw.rect(surface, PANEL, pygame.Rect(170, 24, 660, 126), border_radius=20)
        pygame.draw.rect(surface, PRIMARY, pygame.Rect(192, 49, 4, 25), border_radius=2)
        _draw_centered_text(surface, title_font, "MEMORY MATCH", TEXT, (500, 61))

        pygame.draw.line(surface, (48, 61, 88), (500, 96), (500, 131), 1)
        _draw_centered_text(surface, label_font, "MOVES", MUTED, (365, 103))
        _draw_centered_text(surface, body_font, str(self.moves), TEXT, (365, 126))
        _draw_centered_text(surface, label_font, "MATCHES", MUTED, (635, 103))
        _draw_centered_text(
            surface,
            body_font,
            f"{self.matches}/{PAIR_COUNT}",
            TEXT,
            (635, 126),
        )

        _draw_centered_text(
            surface,
            body_font,
            self.status,
            self.status_color,
            (WINDOW_WIDTH // 2, 153),
        )

        for card in self.cards:
            self._draw_card(
                surface,
                card,
                now_ms,
                mouse_pos,
                card_font,
                small_font,
            )

        restart_rect, menu_rect = _button_rects()
        self._draw_button(surface, restart_rect, "RESTART", mouse_pos, PRIMARY, label_font)
        self._draw_button(
            surface,
            menu_rect,
            "MAIN MENU",
            mouse_pos,
            (51, 65, 92),
            label_font,
        )

        if self.state is GameState.GAME_WON:
            self._draw_win_overlay(surface, mouse_pos, title_font, body_font, label_font)

    def _draw_card(
        self,
        surface: pygame.Surface,
        card: Card,
        now_ms: int,
        mouse_pos: tuple[int, int],
        card_font: pygame.font.Font,
        small_font: pygame.font.Font,
    ) -> None:
        hovered = card.rect.collidepoint(mouse_pos) and not card.matched
        lift = 3 if hovered and self.state is GameState.PLAYING else 0
        draw_rect = card.rect.move(0, -lift)

        progress = 1.0
        if card.flip_started_ms is not None:
            progress = min(1.0, max(0.0, (now_ms - card.flip_started_ms) / CARD_FLIP_MS))
            if progress == 1.0:
                card.flip_started_ms = None

        width_scale = abs(progress * 2 - 1) if progress < 1 else 1
        card_width = max(18, round(draw_rect.width * width_scale))
        animated_rect = pygame.Rect(0, 0, card_width, draw_rect.height)
        animated_rect.center = draw_rect.center
        showing_face = card.revealed and progress >= 0.5

        shadow = animated_rect.move(0, 5)
        pygame.draw.rect(surface, (8, 13, 27), shadow, border_radius=15)

        if showing_face:
            face_color = (28, 56, 64) if card.matched else CARD_FACE
            border_color = SUCCESS if card.matched else PAIR_COLORS[card.pair_id]
            pygame.draw.rect(surface, face_color, animated_rect, border_radius=15)
            pygame.draw.rect(surface, border_color, animated_rect, width=2, border_radius=15)
            if card_width > 45:
                _draw_symbol(
                    surface,
                    card.pair_id,
                    (animated_rect.centerx, animated_rect.centery - 5),
                    PAIR_COLORS[card.pair_id],
                )
                _draw_centered_text(
                    surface,
                    small_font,
                    f"PAIR {card.pair_id + 1}",
                    MUTED,
                    (animated_rect.centerx, animated_rect.bottom - 15),
                )
        else:
            back_color = (38, 52, 83) if hovered else CARD_BACK
            pygame.draw.rect(surface, back_color, animated_rect, border_radius=15)
            pygame.draw.rect(
                surface,
                (58, 75, 111),
                animated_rect,
                width=1,
                border_radius=15,
            )
            if card_width > 36:
                _draw_centered_text(
                    surface,
                    card_font,
                    "?",
                    SECONDARY,
                    animated_rect.center,
                )

    def _draw_button(
        self,
        surface: pygame.Surface,
        rect: pygame.Rect,
        text: str,
        mouse_pos: tuple[int, int],
        color: tuple[int, int, int],
        font: pygame.font.Font,
    ) -> None:
        draw_button(
            surface,
            rect,
            text,
            mouse_pos,
            color=color,
            font=font,
        )

    def _draw_win_overlay(
        self,
        surface: pygame.Surface,
        mouse_pos: tuple[int, int],
        title_font: pygame.font.Font,
        body_font: pygame.font.Font,
        button_font: pygame.font.Font,
    ) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((4, 8, 20, 205))
        surface.blit(overlay, (0, 0))

        panel = pygame.Rect(300, 191, 400, 320)
        pygame.draw.rect(surface, PANEL, panel, border_radius=24)
        pygame.draw.rect(surface, (64, 83, 119), panel, width=1, border_radius=24)
        pygame.draw.circle(surface, SUCCESS, (500, 246), 25)
        pygame.draw.line(surface, BACKGROUND, (488, 246), (497, 255), 4)
        pygame.draw.line(surface, BACKGROUND, (497, 255), (513, 237), 4)
        _draw_centered_text(surface, title_font, "YOU WIN!", TEXT, (500, 294))
        _draw_centered_text(
            surface,
            body_font,
            "All pairs matched!",
            MUTED,
            (500, 330),
        )
        _draw_centered_text(
            surface,
            body_font,
            f"Moves: {self.moves}",
            TEXT,
            (500, 366),
        )

        play_again = pygame.Rect(365, 397, 270, 46)
        main_menu = pygame.Rect(365, 456, 270, 46)
        self._draw_button(surface, play_again, "PLAY AGAIN", mouse_pos, PRIMARY, button_font)
        self._draw_button(
            surface,
            main_menu,
            "MAIN MENU",
            mouse_pos,
            (51, 65, 92),
            button_font,
        )
