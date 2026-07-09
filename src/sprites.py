from __future__ import annotations
import pygame
from . import palette as C

PLAYER_SHIP = [
    "00011000",
    "00111100",
    "01111110",
    "11111111",
    "11011011",
    "10011001",
    "00011000",
]

DRONE = [
    "0110",
    "1111",
    "1001",
    "0110",
]

ENEMY_MATRICES = {
    "tile": [
        "00111100",
        "01111110",
        "11011011",
        "11111111",
        "00100100",
        "01000010",
    ],
    "diver": [
        "00011000",
        "01111110",
        "11111111",
        "10111101",
        "00100100",
        "01000010",
    ],
    "splitter": [
        "00111100",
        "11100111",
        "11111111",
        "01111110",
        "00111100",
        "01000010",
    ],
    "mirror": [
        "01111110",
        "11011011",
        "11111111",
        "01111110",
        "00111100",
        "01000010",
    ],
    "builder": [
        "00100100",
        "01111110",
        "11011011",
        "11111111",
        "01111110",
        "10100101",
    ],
    "elite": [
        "00111100",
        "11111111",
        "11011011",
        "11111111",
        "01111110",
        "11100111",
        "01000010",
    ],
}

BOSS_MATRICES = {
    "medic": [
        "0000011111110000",
        "0001111111111100",
        "0011110011001110",
        "0111101111011110",
        "0111111111111110",
        "0011111001111100",
        "0001111111111000",
        "0000111111110000",
        "0011111111111100",
        "0111011111101110",
        "1110011111100111",
        "1100011111100011",
        "0000011001100000",
        "0000110000110000",
    ],
    "duo": [
        "1111000000001111",
        "1111100000011111",
        "1101110000111011",
        "1111111111111111",
        "0111111111111110",
        "0011011111101100",
        "0111111111111110",
        "1111110110111111",
        "1111100110011111",
        "0111001111001110",
        "0010001111000100",
        "0110011001100110",
        "1100110000110011",
    ],
    "wall": [
        "11111111111111111111",
        "10011001100110011001",
        "11111111111111111111",
        "11000111100111100011",
        "11111111111111111111",
        "10111100111100111101",
        "11111111111111111111",
        "11100111111111100111",
        "11111110011001111111",
        "00111111111111111100",
        "01100111111111100110",
        "11000011111111000011",
        "10000001111110000001",
    ],
}

_digit_cache: dict[tuple[str, int, tuple, bool], pygame.Surface] = {}


def make_mosaic_surface(matrix: list[str], tile: int, colors: list[tuple[int, int, int]] | tuple[tuple[int, int, int], ...], outline: bool = True) -> pygame.Surface:
    key = ("/".join(matrix), tile, tuple(colors), outline)
    if key in _digit_cache:
        return _digit_cache[key].copy()
    w = max(len(row) for row in matrix) * tile
    h = len(matrix) * tile
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y, row in enumerate(matrix):
        for x, ch in enumerate(row):
            if ch == "0":
                continue
            idx = (x * 3 + y * 5 + ord(ch)) % len(colors)
            col = colors[idx]
            rect = pygame.Rect(x * tile, y * tile, tile, tile)
            if outline:
                pygame.draw.rect(surf, C.MORTAR, rect)
                inner = rect.inflate(-1, -1)
                if inner.width > 0 and inner.height > 0:
                    pygame.draw.rect(surf, col, inner)
            else:
                pygame.draw.rect(surf, col, rect)
    _digit_cache[key] = surf.copy()
    return surf


def draw_text(surface: pygame.Surface, font: pygame.font.Font, text: str, x: int, y: int, color=C.WHITE, center=False):
    img = font.render(text, False, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)
    return rect


def draw_bar(surface: pygame.Surface, rect: pygame.Rect, fraction: float, fill, border=C.WHITE, back=C.DARK_GREY):
    pygame.draw.rect(surface, back, rect)
    pygame.draw.rect(surface, border, rect, 1)
    inner = rect.inflate(-2, -2)
    inner.width = max(0, int(inner.width * max(0.0, min(1.0, fraction))))
    if inner.width > 0:
        pygame.draw.rect(surface, fill, inner)
