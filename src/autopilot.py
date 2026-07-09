from __future__ import annotations
import math
from collections import defaultdict
import pygame
from .vec2 import Vector2
from . import settings as S

# Danger radii are a bit larger than the actual hitboxes to give the bot a
# safety margin and time to react instead of grazing every shot.
_BULLET_DANGER_RADIUS = 14.0
_ENEMY_RAM_RADIUS = 16.0
_BOSS_RAM_RADIUS = 26.0

_HORIZON_STEPS = 5
_STEP_DT = 0.045  # ~0.22s total lookahead, enough to see incoming bullets coming

_BOMB_COOLDOWN = 1.5
_BOMB_SCORE_THRESHOLD = -150.0  # even the safest candidate still looks this bad -> panic bomb

# 8 compass directions plus "hold position", used as the candidate moves for
# the lookahead search below.
_CANDIDATE_DIRECTIONS = []
for _dx in (-1, 0, 1):
    for _dy in (-1, 0, 1):
        _v = Vector2(_dx, _dy)
        _CANDIDATE_DIRECTIONS.append(_v.normalize() if _v.length_squared() else Vector2(0, 0))


class Autopilot:
    """Scripted lookahead pilot used by demo/attract mode.

    Each frame it simulates a handful of candidate headings a few steps into
    the future, scores them by predicted damage (enemy bullets extrapolate
    exactly, since Bullet.update is a straight line) versus opportunities to
    line up a kill or grab a powerup, and picks the best one. The result is
    emitted as a synthetic `keys` mapping so the rest of the game (Player.update,
    Game.handle_collisions, ...) runs completely unchanged.
    """

    def __init__(self):
        self._prev_enemy_pos: dict[int, Vector2] = {}
        self.bomb_cd = 0.0

    def decide(self, game, dt: float) -> tuple[dict, bool, bool]:
        """Returns (keys, want_shoot, want_bomb)."""
        self.bomb_cd = max(0.0, self.bomb_cd - dt)
        player = game.player
        enemy_vel = self._estimate_enemy_velocities(game, dt)
        target = self._pick_target(game)
        powerup = self._pick_powerup(game, player.pos)

        best_dir = Vector2(0, 0)
        best_score = -math.inf
        for d in _CANDIDATE_DIRECTIONS:
            score = self._score_direction(game, player.pos, d, enemy_vel, target, powerup)
            if score > best_score:
                best_score = score
                best_dir = d

        self._prev_enemy_pos = {id(e): e.pos.copy() for e in game.enemies}

        want_bomb = self.bomb_cd <= 0 and player.bombs > 0 and best_score < _BOMB_SCORE_THRESHOLD
        if want_bomb:
            self.bomb_cd = _BOMB_COOLDOWN

        return self._dir_to_keys(best_dir), True, want_bomb

    def _score_direction(self, game, pos: Vector2, direction: Vector2, enemy_vel, target, powerup) -> float:
        speed = game.player.speed
        p = pos.copy()
        score = 0.0
        for step in range(1, _HORIZON_STEPS + 1):
            p = p + direction * speed * _STEP_DT
            p.x = max(14, min(S.LOGICAL_WIDTH - 14, p.x))
            p.y = max(148, min(S.LOGICAL_HEIGHT - 17, p.y))
            t = step * _STEP_DT

            for b in game.enemy_bullets:
                future = b.pos + b.vel * t
                dist = p.distance_to(future)
                if dist < _BULLET_DANGER_RADIUS:
                    score -= (_BULLET_DANGER_RADIUS - dist) ** 2 * 6.0

            for e in game.enemies:
                future = e.pos + enemy_vel.get(id(e), Vector2(0, 15)) * t
                dist = p.distance_to(future)
                if dist < _ENEMY_RAM_RADIUS:
                    score -= (_ENEMY_RAM_RADIUS - dist) ** 2 * 5.0

            if game.boss is not None:
                dist = p.distance_to(game.boss.pos)
                if dist < _BOSS_RAM_RADIUS:
                    score -= (_BOSS_RAM_RADIUS - dist) ** 2 * 4.0

        # Soft shaping (much smaller weight than survival) to keep the bot
        # aggressive: line up under a target, drift toward loot, avoid walls.
        if target is not None:
            score -= abs(p.x - target.pos.x) * 0.06
        if powerup is not None:
            score -= p.distance_to(powerup.pos) * 0.01
        score -= abs(p.x - S.LOGICAL_WIDTH / 2) * 0.002
        return score

    def _estimate_enemy_velocities(self, game, dt: float) -> dict:
        vel = {}
        if dt <= 0:
            return vel
        for e in game.enemies:
            prev = self._prev_enemy_pos.get(id(e))
            vel[id(e)] = (e.pos - prev) * (1.0 / dt) if prev is not None else Vector2(0, 15)
        return vel

    def _pick_target(self, game):
        best = None
        best_d = math.inf
        for e in game.enemies:
            if not e.alive:
                continue
            urgency_bonus = 40.0 if (e.kind == "diver" and e.diving) else 0.0
            d = e.pos.distance_to(game.player.pos) - urgency_bonus
            if d < best_d:
                best_d = d
                best = e
        if game.boss is not None and game.boss.alive:
            d = game.boss.pos.distance_to(game.player.pos)
            if best is None or d < best_d:
                best = game.boss
        return best

    def _pick_powerup(self, game, player_pos: Vector2):
        best = None
        best_d = math.inf
        for p in game.powerups:
            d = p.pos.distance_to(player_pos)
            if d < best_d:
                best_d = d
                best = p
        return best

    def _dir_to_keys(self, d: Vector2) -> dict:
        keys = defaultdict(bool)
        if d.x < -0.25:
            keys[pygame.K_LEFT] = True
        elif d.x > 0.25:
            keys[pygame.K_RIGHT] = True
        if d.y < -0.25:
            keys[pygame.K_UP] = True
        elif d.y > 0.25:
            keys[pygame.K_DOWN] = True
        return keys
