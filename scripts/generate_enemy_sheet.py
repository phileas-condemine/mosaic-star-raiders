"""Renders a reference sheet of every enemy and boss in the game, grouped by
act, and saves it to docs/enemies_sheet.png for the README.

Run from the project root:
    python scripts/generate_enemy_sheet.py
"""
from __future__ import annotations
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame
from src import palette as C
from src.sprites import ENEMY_MATRICES, INVADER_SKINS, BOSS_MATRICES, BOSS_SKINS, make_mosaic_surface, make_pixel_surface, draw_text

pygame.init()
pygame.font.init()
pygame.display.set_mode((1, 1))

FONT = pygame.font.Font(None, 16)
FONT_SMALL = pygame.font.Font(None, 13)
FONT_HEADER = pygame.font.Font(None, 24)
FONT_TITLE = pygame.font.Font(None, 34)

ENEMY_TILE = 6
BOSS_TILE = 8

ENEMY_LABELS = {
    "tile": "Tuile",
    "diver": "Plongeur",
    "splitter": "Fragment",
    "mirror": "Miroir",
    "builder": "Batisseur",
    "elite": "Elite",
}
INVADER_LABELS = {
    "pa_classic": "Classique (Paris)",
    "rom_classic": "Classique (Rome)",
    "hk_spider": "Araignee (Hong Kong)",
    "tk_wide": "Grand sourire (Tokyo)",
    "mars_ghost": "Fantome (Marseille)",
    "la_mono": "Mono (Los Angeles)",
    "bab_flag": "Porte-drapeau (Bab)",
    "tk_face": "Visage (Tokyo)",
    "la_green": "Vert (Los Angeles)",
}
BOSS_LABELS = {
    "medic": "Medecin cosmique",
    "duo": "Duo stellaire",
    "wall": "Grand Mur",
}


def enemy_surface(kind: str) -> pygame.Surface:
    colors = C.ENEMY_PALETTES.get(kind, C.ENEMY_PALETTES["tile"])
    return make_mosaic_surface(ENEMY_MATRICES[kind], ENEMY_TILE, colors)


def invader_surface(skin: str) -> pygame.Surface:
    spec = INVADER_SKINS[skin]
    return make_pixel_surface(spec["matrix"], ENEMY_TILE, spec["palette"])


def boss_surface(key: str) -> pygame.Surface:
    palette = {
        "medic": [C.WHITE, C.CYAN, C.BLUE, C.RED],
        "duo": [C.BROWN, C.GOLD, C.WHITE, C.ORANGE],
        "wall": [C.PURPLE, C.MAGENTA, C.CYAN, C.WHITE],
    }[key]
    return make_mosaic_surface(BOSS_MATRICES[key], BOSS_TILE, palette)


def boss_skin_surface(skin: str) -> pygame.Surface:
    spec = BOSS_SKINS[skin]
    return make_pixel_surface(spec["matrix"], BOSS_TILE, spec["palette"])


def layout_row(items: list[tuple[pygame.Surface, str]], cell_w: int, cell_h: int, cols: int, label_gap: int = 40) -> pygame.Surface:
    rows = (len(items) + cols - 1) // cols
    surf = pygame.Surface((cell_w * cols, cell_h * rows), pygame.SRCALPHA)
    baseline = cell_h - label_gap  # every sprite's bottom sits on this line, regardless of its own size
    for i, (sprite, label) in enumerate(items):
        col, row = i % cols, i // cols
        cx = col * cell_w + cell_w // 2
        bottom_y = row * cell_h + baseline
        rect = sprite.get_rect(midbottom=(cx, bottom_y))
        surf.blit(sprite, rect)
        draw_text(surf, FONT_SMALL, label, cx, bottom_y + 10, C.GREY, center=True)
    return surf


def section(title: str, subtitle: str, items: list[tuple[pygame.Surface, str]], cell_w: int, cell_h: int, cols: int, width: int) -> pygame.Surface:
    grid = layout_row(items, cell_w, cell_h, cols)
    header_h = 46
    surf = pygame.Surface((width, header_h + grid.get_height() + 16), pygame.SRCALPHA)
    draw_text(surf, FONT_HEADER, title, 18, 8, C.CYAN)
    draw_text(surf, FONT_SMALL, subtitle, 18, 30, C.GREY)
    surf.blit(grid, ((width - grid.get_width()) // 2, header_h))
    return surf


def main():
    enemy_items = [(enemy_surface(k), ENEMY_LABELS[k]) for k in ENEMY_MATRICES]
    invader_items = [(invader_surface(k), INVADER_LABELS[k]) for k in INVADER_SKINS]
    boss_items = [(boss_surface(k), BOSS_LABELS[k]) for k in BOSS_MATRICES]
    boss_skin_items = [(boss_skin_surface(k), BOSS_SKINS[k]["name"].title()) for k in BOSS_SKINS]

    width = 980
    sec1 = section("ACTE 1 - ENNEMIS", "src/sprites.py : ENEMY_MATRICES (6 familles de comportement)", enemy_items, 150, 110, 6, width)
    sec2 = section("ACTE 2 - ENNEMIS INVADERS", "reproductions fideles de mosaiques «Invader» reelles, en street art dans le monde", invader_items, 150, 110, 6, width)
    sec3 = section("ACTE 1 - BOSS", "src/sprites.py : BOSS_MATRICES", boss_items, 300, 210, 3, width)
    sec4 = section("ACTE 2 - BOSS INVADERS", "memes patterns d'attaque (medic/duo/wall), nouvelle identite visuelle", boss_skin_items, 300, 210, 3, width)

    title_h = 56
    pad = 24
    total_h = title_h + sec1.get_height() + sec2.get_height() + sec3.get_height() + sec4.get_height() + pad * 5
    sheet = pygame.Surface((width, total_h))
    sheet.fill(C.BLACK)
    for i in range(0, total_h, 4):
        pygame.draw.line(sheet, C.INK, (0, i), (width, i), 1)

    draw_text(sheet, FONT_TITLE, "MOSAIC STAR RAIDERS - GALERIE DES ENNEMIS", width // 2, 16, C.WHITE, center=True)

    y = title_h + pad
    for sec in (sec1, sec2, sec3, sec4):
        sheet.blit(sec, (0, y))
        y += sec.get_height() + pad

    out_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "enemies_sheet.png")
    pygame.image.save(sheet, out_path)
    print(f"saved {out_path} ({sheet.get_width()}x{sheet.get_height()})")


if __name__ == "__main__":
    main()
