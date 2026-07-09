from __future__ import annotations
import random
from .entities import Enemy, Boss
from . import settings as S


def make_grid(kind: str, rows: int, cols: int, y: int, hp: int = 1, rank: int = 1, x_margin: int = 36, y_step: int = 18, skin: str | None = None):
    enemies = []
    if cols <= 1:
        xs = [S.LOGICAL_WIDTH / 2]
    else:
        xs = [x_margin + i * ((S.LOGICAL_WIDTH - x_margin * 2) / (cols - 1)) for i in range(cols)]
    for r in range(rows):
        for c, x in enumerate(xs):
            enemies.append(Enemy(kind, x, y + r * y_step, hp=hp, rank=rank, skin=skin))
    return enemies


def make_v_wave(kind: str, count: int, y: int, hp: int = 1, rank: int = 1, skin: str | None = None):
    enemies = []
    for i in range(count):
        x = S.LOGICAL_WIDTH / 2 + (i - count / 2) * 18
        yy = y + abs(i - count / 2) * 8
        enemies.append(Enemy(kind, x, yy, hp=hp, rank=rank, skin=skin))
    return enemies


def make_random_swarm(kinds: list[str], count: int, y_min: int, rank: int, skins: list[str] | None = None):
    enemies = []
    for i in range(count):
        kind = random.choice(kinds)
        hp = 1 + (kind in ("mirror", "builder")) + (kind == "elite") * 2
        skin = random.choice(skins) if skins else None
        enemies.append(Enemy(kind, random.randint(28, S.LOGICAL_WIDTH - 28), y_min - random.randint(0, 90), hp=hp, rank=rank, skin=skin))
    return enemies


WAVE_BOOK = [
    {"title": "ORBITE BASSE", "factory": lambda rank: make_grid("tile", 3, 8, -55, 1, rank)},
    {"title": "PLONGEURS", "factory": lambda rank: make_grid("tile", 2, 7, -60, 1, rank) + make_v_wave("diver", 7, -105, 1, rank)},
    {"title": "FRAGMENTS", "factory": lambda rank: make_grid("splitter", 2, 6, -75, 1 + rank // 3, rank) + make_grid("tile", 1, 8, -30, 1, rank)},
    {"title": "MIROIRS", "factory": lambda rank: make_grid("mirror", 2, 6, -70, 2, rank) + make_grid("builder", 1, 5, -115, 2, rank)},
    {"boss": "medic", "title": "BOSS 100 PTS: MEDECIN COSMIQUE"},
    {"title": "ESSAIM LIBRE", "factory": lambda rank: make_random_swarm(["tile", "diver", "splitter"], 24, -25, rank)},
    {"title": "ATELIER ORBITAL", "factory": lambda rank: make_grid("builder", 2, 5, -80, 2, rank) + make_grid("splitter", 2, 7, -38, 1 + rank // 4, rank)},
    {"title": "ELITES", "factory": lambda rank: make_grid("elite", 1, 5, -80, 4, rank) + make_grid("mirror", 1, 6, -35, 2, rank)},
    {"boss": "duo", "title": "BOSS 100 PTS: DUO STELLAIRE"},
    {"title": "TEMPETE DE TUILES", "factory": lambda rank: make_random_swarm(["tile", "diver", "mirror", "splitter"], 32, -20, rank)},
    {"title": "DERNIER REMPART", "factory": lambda rank: make_grid("elite", 2, 4, -100, 5, rank) + make_grid("builder", 2, 5, -50, 3, rank)},
    {"boss": "wall", "title": "BOSS FINAL: GRAND MUR"},

    # Act 2: faithful reproductions of real "Invader" street-art mosaics,
    # reusing the same behavioral kinds/bosses above (only the skin changes).
    {"title": "COTE D AZUR", "factory": lambda rank: make_grid("tile", 3, 8, -55, 1, rank, skin="pa_classic")},
    {"title": "FANTOMES DE POCHE", "factory": lambda rank: make_grid("tile", 2, 7, -60, 1, rank, skin="la_mono") + make_v_wave("diver", 7, -105, 1, rank, skin="mars_ghost")},
    {"title": "ECLATS RETRO", "factory": lambda rank: make_grid("splitter", 2, 6, -75, 1 + rank // 3, rank, skin="tk_wide") + make_grid("tile", 1, 8, -30, 1, rank, skin="rom_classic")},
    {"title": "GARDIENS D ARGILE", "factory": lambda rank: make_grid("mirror", 2, 6, -70, 2, rank, skin="hk_spider") + make_grid("builder", 1, 5, -115, 2, rank, skin="bab_flag")},
    {"boss": "medic", "skin": "mia_shades", "title": "BOSS 100 PTS: SURFEUR A LUNETTES"},
    {"title": "ESSAIM RETRO", "factory": lambda rank: make_random_swarm(["tile", "diver", "splitter"], 24, -25, rank, skins=["pa_classic", "rom_classic", "mars_ghost", "tk_wide"])},
    {"title": "ATELIER MOSAIQUE", "factory": lambda rank: make_grid("builder", 2, 5, -80, 2, rank, skin="bab_flag") + make_grid("splitter", 2, 7, -38, 1 + rank // 4, rank, skin="tk_face")},
    {"title": "ELITES DE RUE", "factory": lambda rank: make_grid("elite", 1, 5, -80, 4, rank, skin="la_green") + make_grid("mirror", 1, 6, -35, 2, rank, skin="hk_spider")},
    {"boss": "duo", "skin": "djba_target", "title": "BOSS 100 PTS: CIBLE BLEUE"},
    {"title": "TEMPETE URBAINE", "factory": lambda rank: make_random_swarm(
        ["tile", "diver", "mirror", "splitter"], 32, -20, rank,
        skins=["pa_classic", "rom_classic", "hk_spider", "tk_wide", "mars_ghost", "la_mono", "bab_flag", "tk_face", "la_green"],
    )},
    {"title": "DERNIER QUARTIER", "factory": lambda rank: make_grid("elite", 2, 4, -100, 5, rank, skin="rom_classic") + make_grid("builder", 2, 5, -50, 3, rank, skin="la_green")},
    {"boss": "wall", "skin": "djba_hand", "title": "BOSS FINAL: MAIN GARDIENNE"},
]


def spawn_wave(index: int, rank: int):
    entry = WAVE_BOOK[index % len(WAVE_BOOK)]
    if "boss" in entry:
        return [], Boss(entry["boss"], rank, skin=entry.get("skin")), entry["title"]
    return entry["factory"](rank), None, entry["title"]
