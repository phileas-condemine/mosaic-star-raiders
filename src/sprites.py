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

# Faithful reproductions of real "Invader" street-art mosaics (ceramic tile
# installations photographed in various cities). Unlike ENEMY_MATRICES above
# (which pick a color per cell via a position hash), each cell here is an
# explicit palette index so the real artwork's colors are reproduced exactly.
INVADER_SKINS = {
    "pa_classic": {
        "tile": 3,
        "matrix": [
            "0000000000000",
            "0000100010000",
            "0001111111000",
            "0011211121100",
            "0111111111110",
            "0101111111110",
            "0101000001010",
            "0100110110010",
            "0000000000000",
        ],
        "palette": [(0, 0, 0), (72, 144, 174), (190, 60, 50)],
    },
    "rom_classic": {
        "tile": 3,
        "matrix": [
            "001000100",
            "001000100",
            "011111110",
            "111111111",
            "111111111",
            "123111321",
            "111111111",
            "110111011",
            "100000001",
        ],
        "palette": [(0, 0, 0), (214, 42, 34), (225, 232, 236), (24, 24, 26)],
    },
    "hk_spider": {
        "tile": 3,
        "matrix": [
            "0000000000000",
            "0110000000110",
            "0010001000100",
            "0000011100000",
            "1100021200011",
            "0000011100000",
            "0010001000100",
            "0110000000110",
            "0000000000000",
        ],
        "palette": [(0, 0, 0), (42, 42, 110), (250, 190, 40)],
    },
    "tk_wide": {
        "tile": 3,
        "matrix": [
            "0000010100000",
            "0000111110000",
            "0011321321100",
            "1111111111111",
            "0011101011100",
            "0110000000110",
        ],
        "palette": [(0, 0, 0), (240, 190, 20), (30, 30, 32), (250, 240, 225)],
    },
    "mars_ghost": {
        "tile": 3,
        "matrix": [
            "00111111100",
            "01111111110",
            "11111111111",
            "11111111111",
            "11231112311",
            "11231112311",
            "11111111111",
            "11111111111",
            "11011011011",
        ],
        "palette": [(0, 0, 0), (200, 50, 45), (240, 240, 238), (20, 30, 90)],
    },
    "la_mono": {
        "tile": 3,
        "matrix": [
            "001000100",
            "011111110",
            "112111211",
            "111111111",
            "110111011",
            "010000010",
        ],
        "palette": [(0, 0, 0), (48, 48, 54), (230, 230, 225)],
    },
    "bab_flag": {
        "tile": 3,
        "matrix": [
            "0045000000000",
            "0054100101000",
            "0000111111100",
            "0000111111110",
            "0000112112110",
            "0000111111110",
            "0000110110110",
            "0000100000010",
        ],
        "palette": [(0, 0, 0), (212, 40, 40), (40, 150, 140), (0, 0, 0), (60, 140, 70), (235, 235, 230)],
    },
    "tk_face": {
        "tile": 3,
        "matrix": [
            "010000010",
            "112222211",
            "122222221",
            "123424321",
            "122222221",
            "122232221",
            "122222221",
            "011111110",
        ],
        "palette": [(0, 0, 0), (120, 150, 175), (235, 180, 165), (25, 25, 28), (245, 245, 240)],
    },
    "la_green": {
        "tile": 3,
        "matrix": [
            "00011111000",
            "00111111100",
            "01123132110",
            "01111111110",
            "11111111111",
            "01111111110",
            "01010101010",
        ],
        "palette": [(0, 0, 0), (120, 190, 60), (235, 238, 235), (20, 20, 22)],
    },
}

# New bosses (act 2): the "key" the caller passes to Boss() still selects the
# attack pattern (medic/duo/wall) -- these only override the appearance.
BOSS_SKINS = {
    "mia_shades": {
        "name": "LE SURFEUR A LUNETTES",
        "tile": 4,
        "matrix": [
            "000000101000000",
            "000000101000000",
            "000001111100000",
            "000011111110000",
            "000122222221000",
            "000111111111000",
            "011111111111110",
            "001111111111100",
            "000111111111000",
            "000111111111000",
            "001010101010100",
        ],
        "palette": [(0, 0, 0), (235, 238, 240), (15, 15, 18)],
    },
    "djba_target": {
        "name": "LA CIBLE BLEUE",
        "tile": 4,
        "matrix": [
            "11111111111111111",
            "12222222222222221",
            "12111111111111121",
            "12122222222222121",
            "12121111111112121",
            "12121000330012121",
            "12121003333012121",
            "12121034443012121",
            "12121333333312121",
            "12121334443312121",
            "12121033033012121",
            "12121000000012121",
            "12121111111112121",
            "12122222222222121",
            "12111111111111121",
            "12222222222222221",
            "11111111111111111",
        ],
        "palette": [(0, 0, 0), (110, 200, 235), (25, 60, 140), (240, 242, 244), (15, 15, 18)],
    },
    "djba_hand": {
        "name": "LA MAIN GARDIENNE",
        "tile": 4,
        "matrix": [
            "001101111110110",
            "001101111110110",
            "001101111110110",
            "001101111110110",
            "001111111111100",
            "111111111111110",
            "111111111111110",
            "111112121211110",
            "011122222221110",
            "011121222121110",
            "001122222221100",
            "000111111111000",
            "000011111110000",
            "000000000000000",
        ],
        "palette": [(0, 0, 0), (80, 200, 215), (235, 240, 242)],
    },
}

_digit_cache: dict[tuple[str, int, tuple, bool], pygame.Surface] = {}
_pixel_cache: dict[tuple[str, int, tuple, bool], pygame.Surface] = {}


def make_pixel_surface(matrix: list[str], tile: int, palette: list[tuple[int, int, int]], outline: bool = True) -> pygame.Surface:
    """Like make_mosaic_surface, but each digit is an explicit index into
    `palette` (0 = transparent) instead of a color picked by a position hash --
    used for faithful reproductions where the exact color-per-cell matters."""
    key = ("/".join(matrix), tile, tuple(palette), outline)
    if key in _pixel_cache:
        return _pixel_cache[key].copy()
    w = max(len(row) for row in matrix) * tile
    h = len(matrix) * tile
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    for y, row in enumerate(matrix):
        for x, ch in enumerate(row):
            idx = int(ch)
            if idx == 0:
                continue
            col = palette[idx]
            rect = pygame.Rect(x * tile, y * tile, tile, tile)
            if outline:
                pygame.draw.rect(surf, C.MORTAR, rect)
                inner = rect.inflate(-1, -1)
                if inner.width > 0 and inner.height > 0:
                    pygame.draw.rect(surf, col, inner)
            else:
                pygame.draw.rect(surf, col, rect)
    _pixel_cache[key] = surf.copy()
    return surf


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
