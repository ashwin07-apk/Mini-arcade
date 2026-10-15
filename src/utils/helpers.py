"""Small, reusable Pygame drawing helpers."""

from __future__ import annotations

import pygame

from src.utils.constants import TEXT


def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: tuple[int, int, int],
    position: tuple[int, int],
    *,
    center: bool = True,
) -> pygame.Rect:
    """Render text at a center point, or at a top-left position."""
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = position
    else:
        rect.topleft = position
    surface.blit(rendered, rect)
    return rect


def draw_button(
    surface: pygame.Surface,
    rect: pygame.Rect,
    label: str,
    mouse_pos: tuple[int, int],
    *,
    color: tuple[int, int, int],
    font: pygame.font.Font,
    text_color: tuple[int, int, int] = TEXT,
) -> None:
    """Draw a rounded button with a simple hover highlight."""
    hovered = rect.collidepoint(mouse_pos)
    fill = tuple(min(channel + (14 if hovered else 0), 255) for channel in color)
    pygame.draw.rect(surface, fill, rect, border_radius=12)
    draw_text(surface, label, font, text_color, rect.center)


def draw_panel(
    surface: pygame.Surface,
    rect: pygame.Rect,
    *,
    color: tuple[int, int, int],
    border_color: tuple[int, int, int] | None = None,
    radius: int = 18,
) -> None:
    """Draw a rounded panel and an optional outline."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)
    if border_color is not None:
        pygame.draw.rect(surface, border_color, rect, width=1, border_radius=radius)
