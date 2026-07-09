from __future__ import annotations
from dataclasses import dataclass
import math
import random
import pygame
from .vec2 import Vector2
from . import palette as C
from . import settings as S
from .sprites import PLAYER_SHIP, DRONE, ENEMY_MATRICES, INVADER_SKINS, BOSS_SKINS, make_mosaic_surface, make_pixel_surface


@dataclass
class Bullet:
    pos: Vector2
    vel: Vector2
    owner: str
    damage: int
    color: tuple[int, int, int]
    radius: int = 2
    ttl: float = 4.0
    pierce: int = 0
    kind: str = "bolt"

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.pos.x - self.radius), int(self.pos.y - self.radius), self.radius * 2, self.radius * 2)

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.ttl -= dt

    @property
    def alive(self) -> bool:
        return self.ttl > 0 and -20 < self.pos.x < S.LOGICAL_WIDTH + 20 and -30 < self.pos.y < S.LOGICAL_HEIGHT + 30

    def draw(self, surf: pygame.Surface):
        if self.kind == "laser":
            pygame.draw.rect(surf, self.color, (int(self.pos.x - 1), int(self.pos.y - 7), 3, 12))
            pygame.draw.rect(surf, C.WHITE, (int(self.pos.x), int(self.pos.y - 6), 1, 10))
        else:
            pygame.draw.circle(surf, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
            pygame.draw.circle(surf, C.WHITE, (int(self.pos.x), int(self.pos.y)), max(1, self.radius - 2))


@dataclass
class Particle:
    pos: Vector2
    vel: Vector2
    color: tuple[int, int, int]
    ttl: float
    size: int = 2

    def update(self, dt: float):
        self.pos += self.vel * dt
        self.vel *= 0.985
        self.ttl -= dt

    @property
    def alive(self) -> bool:
        return self.ttl > 0

    def draw(self, surf: pygame.Surface):
        alpha = max(0, min(255, int(255 * self.ttl)))
        rect = pygame.Rect(int(self.pos.x), int(self.pos.y), self.size, self.size)
        col = tuple(max(0, min(255, c)) for c in self.color)
        pygame.draw.rect(surf, col, rect)
        if alpha > 120 and self.size > 1:
            pygame.draw.rect(surf, C.WHITE, rect, 1)


class PowerUp:
    def __init__(self, x: float, y: float, kind: str):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 34)
        self.kind = kind
        self.t = random.random() * 10
        self.color = C.POWER_COLORS[kind]
        self.radius = 6

    def update(self, dt: float, player_pos: Vector2, magnet: bool = False):
        self.t += dt
        if magnet and self.pos.distance_to(player_pos) < 85:
            direction = player_pos - self.pos
            if direction.length_squared() > 1:
                self.vel += direction.normalize() * 260 * dt
        self.pos += self.vel * dt
        self.vel *= 0.995

    @property
    def alive(self) -> bool:
        return self.pos.y < S.LOGICAL_HEIGHT + 20

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.pos.x - self.radius), int(self.pos.y - self.radius), self.radius * 2, self.radius * 2)

    def draw(self, surf: pygame.Surface, font: pygame.font.Font):
        x, y = int(self.pos.x), int(self.pos.y)
        pulse = 1 + int(math.sin(self.t * 7) > 0)
        pygame.draw.rect(surf, C.MORTAR, (x - 7, y - 7, 14, 14))
        pygame.draw.rect(surf, self.color, (x - 6, y - 6, 12, 12))
        pygame.draw.rect(surf, C.WHITE, (x - 4, y - 4, 8, 8), 1)
        letter = {
            "spread": "S",
            "laser": "L",
            "drone": "D",
            "shield": "O",
            "bomb": "B",
            "repair": "+",
        }[self.kind]
        img = font.render(letter, False, C.BLACK)
        surf.blit(img, img.get_rect(center=(x, y + pulse)))


class Player:
    def __init__(self):
        self.pos = Vector2(S.LOGICAL_WIDTH / 2, S.PLAYER_Y)
        self.speed = S.PLAYER_SPEED
        self.lives = 3
        self.max_lives = 5
        self.invuln = 0.0
        self.fire_cd = 0.0
        self.weapon = "basic"
        self.weapon_timer = 0.0
        self.weapon_level = 1
        self.shield = 0.0
        self.drones = 0
        self.bombs = 1
        self.magnet = 0.0
        self.ship_surface = make_mosaic_surface(PLAYER_SHIP, 2, [C.CYAN, C.BLUE, C.WHITE])
        self.drone_surface = make_mosaic_surface(DRONE, 2, [C.YELLOW, C.WHITE, C.ORANGE])
        self.engine_t = 0.0

    def rect(self) -> pygame.Rect:
        r = self.ship_surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        return r.inflate(-4, -3)

    def update(self, dt: float, keys):
        move = Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_q]:
            move.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_z]:
            move.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move.y += 1
        if move.length_squared() > 0:
            move = move.normalize()
        self.pos += move * self.speed * dt
        self.pos.x = max(14, min(S.LOGICAL_WIDTH - 14, self.pos.x))
        self.pos.y = max(148, min(S.LOGICAL_HEIGHT - 17, self.pos.y))
        self.fire_cd = max(0.0, self.fire_cd - dt)
        self.invuln = max(0.0, self.invuln - dt)
        self.weapon_timer = max(0.0, self.weapon_timer - dt)
        self.shield = max(0.0, self.shield - dt)
        self.magnet = max(0.0, self.magnet - dt)
        self.engine_t += dt
        if self.weapon_timer <= 0 and self.weapon != "basic":
            self.weapon = "basic"
            self.weapon_level = 1

    def apply_powerup(self, kind: str):
        if kind in ("spread", "laser"):
            if self.weapon == kind:
                self.weapon_level = min(3, self.weapon_level + 1)
            else:
                self.weapon = kind
                self.weapon_level = 1
            self.weapon_timer = 16.0
        elif kind == "drone":
            self.drones = min(2, self.drones + 1)
        elif kind == "shield":
            self.shield = max(self.shield, 12.0)
        elif kind == "bomb":
            self.bombs = min(3, self.bombs + 1)
        elif kind == "repair":
            self.lives = min(self.max_lives, self.lives + 1)
        self.magnet = max(self.magnet, 6.0)

    def shoot(self) -> list[Bullet]:
        if self.fire_cd > 0:
            return []
        bullets: list[Bullet] = []
        base = Vector2(self.pos.x, self.pos.y - 10)
        if self.weapon == "spread":
            self.fire_cd = 0.16
            angles = [-24, 0, 24] if self.weapon_level == 1 else [-32, -13, 0, 13, 32]
            if self.weapon_level >= 3:
                angles = [-42, -25, -10, 0, 10, 25, 42]
            for deg in angles:
                rad = math.radians(deg)
                vel = Vector2(math.sin(rad) * 210, -math.cos(rad) * 210)
                bullets.append(Bullet(base.copy(), vel, "player", 1, C.MAGENTA, 2, 2.1))
        elif self.weapon == "laser":
            self.fire_cd = 0.11
            xs = [0] if self.weapon_level == 1 else [-4, 4]
            if self.weapon_level >= 3:
                xs = [-8, 0, 8]
            for ox in xs:
                bullets.append(Bullet(Vector2(base.x + ox, base.y), Vector2(0, -285), "player", 2, C.CYAN, 2, 1.6, pierce=2, kind="laser"))
        else:
            self.fire_cd = S.PLAYER_FIRE_RATE
            bullets.append(Bullet(base.copy(), Vector2(0, -240), "player", 1, C.CYAN, 2, 1.9))
        if self.drones:
            for i in range(self.drones):
                side = -1 if i == 0 else 1
                bullets.append(Bullet(Vector2(self.pos.x + side * 18, self.pos.y - 2), Vector2(side * 18, -220), "player", 1, C.YELLOW, 2, 1.8))
        return bullets

    def hurt(self) -> bool:
        if self.invuln > 0:
            return False
        if self.shield > 0:
            self.shield = max(0.0, self.shield - 4.0)
            self.invuln = 0.6
            return False
        self.lives -= 1
        self.invuln = 1.8
        self.weapon = "basic"
        self.weapon_level = 1
        self.weapon_timer = 0
        self.drones = max(0, self.drones - 1)
        return True

    def draw(self, surf: pygame.Surface):
        blink = self.invuln > 0 and int(self.invuln * 16) % 2 == 0
        if not blink:
            r = self.ship_surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))
            surf.blit(self.ship_surface, r)
        flame_h = 3 + int((math.sin(self.engine_t * 20) + 1) * 2)
        pygame.draw.rect(surf, C.ORANGE, (int(self.pos.x - 3), int(self.pos.y + 9), 6, flame_h))
        pygame.draw.rect(surf, C.YELLOW, (int(self.pos.x - 1), int(self.pos.y + 9), 2, max(2, flame_h - 1)))
        if self.shield > 0:
            radius = 17 + int(math.sin(self.engine_t * 8) * 2)
            pygame.draw.circle(surf, C.GREEN, (int(self.pos.x), int(self.pos.y)), radius, 1)
            pygame.draw.circle(surf, C.CYAN, (int(self.pos.x), int(self.pos.y)), radius + 3, 1)
        for i in range(self.drones):
            side = -1 if i == 0 else 1
            y = self.pos.y + math.sin(self.engine_t * 4 + i) * 3
            r = self.drone_surface.get_rect(center=(int(self.pos.x + side * 22), int(y)))
            surf.blit(self.drone_surface, r)


class Enemy:
    def __init__(self, kind: str, x: float, y: float, hp: int = 1, rank: int = 1, skin: str | None = None):
        self.kind = kind
        self.skin = skin
        self.pos = Vector2(x, y)
        self.spawn = Vector2(x, y)
        self.hp = hp
        self.max_hp = hp
        self.rank = rank
        self.t = random.random() * 10
        self.fire_cd = random.uniform(0.8, 3.0)
        self.dead = False
        self.score = {"tile": 10, "diver": 25, "splitter": 30, "mirror": 40, "builder": 45, "elite": 80}.get(kind, 10) * rank
        if skin:
            spec = INVADER_SKINS[skin]
            self.surface = make_pixel_surface(spec["matrix"], spec["tile"], spec["palette"])
        else:
            colors = C.ENEMY_PALETTES.get(kind, C.ENEMY_PALETTES["tile"])
            tile = 2 if kind != "elite" else 3
            self.surface = make_mosaic_surface(ENEMY_MATRICES[kind], tile, colors)
        self.dive_target = Vector2(x, S.LOGICAL_HEIGHT + 20)
        self.diving = kind == "diver" and random.random() < 0.35
        self.armored = kind == "mirror"
        self.heal_pulse = 0.0

    def rect(self) -> pygame.Rect:
        return self.surface.get_rect(center=(int(self.pos.x), int(self.pos.y))).inflate(-2, -2)

    def update(self, dt: float, game_t: float, player_pos: Vector2) -> list[Bullet]:
        self.t += dt
        wave_speed = 1 + self.rank * 0.15
        if self.kind == "tile":
            self.pos.x = self.spawn.x + math.sin(game_t * 1.3 + self.spawn.y * .07) * 12
            self.pos.y += (8 + self.rank * 1.2) * dt
        elif self.kind == "diver":
            if not self.diving and self.pos.y > 42 and random.random() < dt * 0.35:
                self.diving = True
            if self.diving:
                direction = (Vector2(player_pos.x, S.LOGICAL_HEIGHT + 20) - self.pos)
                if direction.length_squared() > 0:
                    self.pos += direction.normalize() * (48 + 20 * self.rank) * dt
            else:
                self.pos.x = self.spawn.x + math.sin(game_t * 2.2 + self.spawn.x) * 20
                self.pos.y += 10 * dt
        elif self.kind == "splitter":
            self.pos.x = self.spawn.x + math.sin(game_t * 1.7 + self.spawn.x) * 8
            self.pos.y += (13 + self.rank * 2) * dt
        elif self.kind == "mirror":
            self.pos.x = self.spawn.x + math.sin(game_t * 2.8 + self.spawn.x * .1) * 22
            self.pos.y += (7 + self.rank) * dt
        elif self.kind == "builder":
            self.pos.x = self.spawn.x + math.sin(game_t * 1.0 + self.spawn.x) * 10
            self.pos.y += (6 + self.rank) * dt
            self.heal_pulse = max(0, self.heal_pulse - dt)
        elif self.kind == "elite":
            self.pos.x = self.spawn.x + math.sin(game_t * 1.7) * 25
            self.pos.y += (5 + self.rank) * dt
        bullets = []
        self.fire_cd -= dt
        fire_chance_scale = {"tile": 1.0, "diver": 1.15, "splitter": .8, "mirror": 1.1, "builder": .6, "elite": 1.8}.get(self.kind, 1)
        if self.fire_cd <= 0 and self.pos.y > 10:
            self.fire_cd = random.uniform(1.2, 3.2) / fire_chance_scale
            color = C.ENEMY_PALETTES.get(self.kind, [C.RED])[0]
            if self.kind == "elite":
                for vx in (-36, 0, 36):
                    bullets.append(Bullet(Vector2(self.pos.x, self.pos.y + 6), Vector2(vx, 88), "enemy", 1, color, 2, 4))
            else:
                bullets.append(Bullet(Vector2(self.pos.x, self.pos.y + 6), Vector2(0, 70 + self.rank * 5), "enemy", 1, color, 2, 4))
        return bullets

    @property
    def alive(self) -> bool:
        return not self.dead and self.hp > 0 and self.pos.y < S.LOGICAL_HEIGHT + 35

    def hit(self, damage: int) -> bool:
        self.hp -= damage
        if self.hp <= 0:
            self.dead = True
            return True
        return False

    def draw(self, surf: pygame.Surface):
        r = self.surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        surf.blit(self.surface, r)
        if self.hp > 1:
            w = r.width
            hpw = int(w * self.hp / self.max_hp)
            pygame.draw.rect(surf, C.DARK_GREY, (r.left, r.top - 4, w, 2))
            pygame.draw.rect(surf, C.RED if self.kind == "elite" else C.WHITE, (r.left, r.top - 4, hpw, 2))
        if self.kind == "mirror":
            pygame.draw.rect(surf, C.CYAN, r.inflate(3, 3), 1)


class Boss:
    def __init__(self, key: str, level: int, skin: str | None = None):
        from .sprites import BOSS_MATRICES
        self.key = key
        self.level = level
        self.skin = skin
        self.names = {
            "medic": "LE MEDECIN COSMIQUE",
            "duo": "LE DUO STELLAIRE",
            "wall": "LE GRAND MUR",
        }
        if skin:
            spec = BOSS_SKINS[skin]
            self.name = spec["name"]
            self.matrix = spec["matrix"]
            self.tile = spec["tile"]
            self.surface = make_pixel_surface(self.matrix, self.tile, spec["palette"])
        else:
            self.name = self.names.get(key, key.upper())
            self.matrix = BOSS_MATRICES[key]
            self.tile = 3 if key != "wall" else 2
            palette = {
                "medic": [C.WHITE, C.CYAN, C.BLUE, C.RED],
                "duo": [C.BROWN, C.GOLD, C.WHITE, C.ORANGE],
                "wall": [C.PURPLE, C.MAGENTA, C.CYAN, C.WHITE],
            }[key]
            self.surface = make_mosaic_surface(self.matrix, self.tile, palette)
        self.pos = Vector2(S.LOGICAL_WIDTH / 2, -40)
        self.target_y = 52 if key != "wall" else 44
        base_hp = {"medic": 70, "duo": 105, "wall": 145}[key]
        self.hp = base_hp + level * 12
        self.max_hp = self.hp
        self.t = 0.0
        self.attack_cd = 1.0
        self.dead = False
        self.score = {"medic": 500, "duo": 800, "wall": 1200}[key]

    def rect(self) -> pygame.Rect:
        return self.surface.get_rect(center=(int(self.pos.x), int(self.pos.y))).inflate(-4, -4)

    @property
    def phase(self) -> int:
        f = self.hp / self.max_hp
        if f < 0.34:
            return 3
        if f < 0.67:
            return 2
        return 1

    def update(self, dt: float, player_pos: Vector2) -> list[Bullet]:
        self.t += dt
        if self.pos.y < self.target_y:
            self.pos.y += 32 * dt
        else:
            span = 36 if self.key != "wall" else 20
            self.pos.x = S.LOGICAL_WIDTH / 2 + math.sin(self.t * (0.7 + self.phase * .18)) * span
        self.attack_cd -= dt
        bullets: list[Bullet] = []
        if self.attack_cd <= 0 and self.pos.y >= self.target_y - 2:
            if self.key == "medic":
                self.attack_cd = max(0.34, 1.05 - self.phase * 0.18)
                # ECG wave plus aimed shot
                for i, vx in enumerate([-70, -35, 0, 35, 70]):
                    vy = 68 + abs(vx) * .18
                    bullets.append(Bullet(Vector2(self.pos.x - 30 + i * 15, self.pos.y + 18), Vector2(vx * .45, vy), "enemy", 1, C.RED, 2, 5))
                aim = player_pos - self.pos
                if aim.length_squared() > 0:
                    bullets.append(Bullet(Vector2(self.pos.x, self.pos.y + 25), aim.normalize() * 92, "enemy", 1, C.CYAN, 3, 4))
            elif self.key == "duo":
                self.attack_cd = max(0.42, 0.95 - self.phase * .14)
                for side in [-1, 1]:
                    origin = Vector2(self.pos.x + side * 24, self.pos.y + 10)
                    for a in [-20, 0, 20]:
                        rad = math.radians(a + side * 8)
                        bullets.append(Bullet(origin.copy(), Vector2(math.sin(rad) * 75, math.cos(rad) * 75 + 32), "enemy", 1, C.GOLD if side > 0 else C.BROWN, 2, 4))
            else:
                self.attack_cd = max(0.38, 0.78 - self.phase * .1)
                count = 6 + self.phase * 2
                for i in range(count):
                    x = 34 + i * (S.LOGICAL_WIDTH - 68) / max(1, count - 1)
                    vy = 62 + (i % 3) * 12
                    bullets.append(Bullet(Vector2(x, self.pos.y + 34), Vector2(math.sin(self.t * 2 + i) * 22, vy), "enemy", 1, C.PURPLE if i % 2 else C.MAGENTA, 2, 5))
        return bullets

    @property
    def alive(self) -> bool:
        return not self.dead and self.hp > 0

    def hit(self, damage: int) -> bool:
        self.hp -= damage
        if self.hp <= 0:
            self.dead = True
            return True
        return False

    def draw(self, surf: pygame.Surface, font: pygame.font.Font):
        r = self.surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))
        surf.blit(self.surface, r)
        # weak-point glints
        if int(self.t * 8) % 2 == 0:
            pygame.draw.rect(surf, C.WHITE, (r.centerx - 3, r.centery - 3, 6, 6), 1)
        bar_w = S.LOGICAL_WIDTH - 76
        pygame.draw.rect(surf, C.DARK_GREY, (38, 15, bar_w, 5))
        pygame.draw.rect(surf, C.WHITE, (38, 15, bar_w, 5), 1)
        hpw = int((bar_w - 4) * max(0, self.hp) / self.max_hp)
        pygame.draw.rect(surf, C.RED if self.phase >= 3 else C.MAGENTA, (40, 17, hpw, 1))
        img = font.render(self.name, False, C.WHITE)
        surf.blit(img, img.get_rect(center=(S.LOGICAL_WIDTH // 2, 9)))
