from __future__ import annotations
import math
import random
import sys
import pygame
from .vec2 import Vector2
from . import settings as S
from . import palette as C
from .entities import Player, Enemy, Bullet, Particle, PowerUp
from .waves import spawn_wave, WAVE_BOOK
from .sprites import draw_text, draw_bar
from .autopilot import Autopilot


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        fallback_size = (S.LOGICAL_WIDTH * S.SCALE, S.LOGICAL_HEIGHT * S.SCALE)
        try:
            self.screen = pygame.display.set_mode(self._initial_window_size(), pygame.RESIZABLE)
        except Exception:
            self.screen = pygame.display.set_mode(fallback_size)
        pygame.display.set_caption(f"{S.TITLE} {S.VERSION}")
        self.canvas = pygame.Surface((S.LOGICAL_WIDTH, S.LOGICAL_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 12)
        self.font_med = pygame.font.Font(None, 18)
        self.font_big = pygame.font.Font(None, 30)
        self.viewport = pygame.Rect(0, 0, *self.screen.get_size())
        self._update_viewport()
        self.demo_mode = False
        self.idle_timer = 0.0
        self.demo_restart_delay = 0.0
        self.autopilot = Autopilot()
        self.time_scale = 1.0
        self._step_accumulator = 0.0
        self.reset(full=True)

    def _initial_window_size(self) -> tuple[int, int]:
        # Fit the widest/tallest window that keeps the 16:9 logical aspect
        # ratio. On the browser build, main.py has already resized the
        # canvas to the full page before Game() is constructed, so
        # pygame.display.Info() reports that real canvas size here and no
        # extra chrome margin is needed (there's no OS title bar/taskbar).
        is_web = sys.platform == "emscripten"
        try:
            info = pygame.display.Info()
            avail_w, avail_h = info.current_w, info.current_h
            if avail_w <= 0 or avail_h <= 0:
                raise ValueError("invalid desktop size")
        except Exception:
            avail_w, avail_h = S.LOGICAL_WIDTH * S.SCALE, S.LOGICAL_HEIGHT * S.SCALE
        chrome_margin = 0 if is_web else 90
        scale = min(avail_w / S.LOGICAL_WIDTH, max(1, avail_h - chrome_margin) / S.LOGICAL_HEIGHT)
        scale = max(scale, 1.0)
        return (round(S.LOGICAL_WIDTH * scale), round(S.LOGICAL_HEIGHT * scale))

    def _update_viewport(self):
        # Largest 16:9 rect that fits the current window, centered,
        # so resizing to an off-ratio size letterboxes instead of distorting.
        win_w, win_h = self.screen.get_size()
        scale = min(win_w / S.LOGICAL_WIDTH, win_h / S.LOGICAL_HEIGHT)
        w = max(1, round(S.LOGICAL_WIDTH * scale))
        h = max(1, round(S.LOGICAL_HEIGHT * scale))
        self.viewport = pygame.Rect((win_w - w) // 2, (win_h - h) // 2, w, h)

    def reset(self, full=False):
        self.state = "title" if full else "playing"
        self.player = Player()
        self.player_bullets: list[Bullet] = []
        self.enemy_bullets: list[Bullet] = []
        self.enemies: list[Enemy] = []
        self.powerups: list[PowerUp] = []
        self.particles: list[Particle] = []
        self.boss = None
        self.score = 0
        self.combo = 0
        self.combo_t = 0.0
        self.wave_index = 0
        self.rank = 1
        self.wave_title = ""
        self.wave_banner = 0.0
        self.next_wave_delay = 0.5
        self.t = 0.0
        self.shake = 0.0
        self.flash = 0.0
        self.kills = 0
        self.bosses_killed = 0
        self.stars = [
            [random.randrange(S.LOGICAL_WIDTH), random.randrange(S.LOGICAL_HEIGHT), random.choice([12, 20, 34, 48]), random.choice([1, 1, 1, 2])]
            for _ in range(S.STAR_COUNT)
        ]
        if not full:
            self.spawn_next_wave()

    def start(self):
        self.reset(full=False)
        self.state = "playing"

    def start_demo(self):
        self.reset(full=False)
        self.state = "demo"
        self.demo_mode = True
        self.autopilot = Autopilot()
        self.idle_timer = 0.0

    def exit_demo(self):
        self.demo_mode = False
        self.reset(full=True)
        self.idle_timer = 0.0
        self.time_scale = 1.0
        self._step_accumulator = 0.0

    def _adjust_time_scale(self, key):
        lo, hi = (S.TIME_SCALE_DEMO_MIN, S.TIME_SCALE_DEMO_MAX) if self.state == "demo" else (S.TIME_SCALE_PLAY_MIN, S.TIME_SCALE_PLAY_MAX)
        if key == pygame.K_HOME:
            self.time_scale = 1.0
        else:
            step = S.TIME_SCALE_STEP if key == pygame.K_PAGEUP else -S.TIME_SCALE_STEP
            self.time_scale = round(max(lo, min(hi, self.time_scale + step)), 2)

    def _enter_end_state(self, name: str):
        self.state = name
        if self.demo_mode:
            self.demo_restart_delay = 3.0

    def use_bomb(self):
        self.player.bombs -= 1
        self.enemy_bullets.clear()
        for e in list(self.enemies):
            e.hit(3)
            self.add_particles(e.pos.x, e.pos.y, C.ORANGE, 6, 70)
        if self.boss:
            self.boss.hit(18)
        self.explode_big(self.player.pos.x, self.player.pos.y - 30, [C.ORANGE, C.YELLOW, C.WHITE])

    def spawn_next_wave(self):
        self.enemy_bullets.clear()
        self.enemies, self.boss, self.wave_title = spawn_wave(self.wave_index, self.rank)
        self.wave_banner = 2.0
        self.wave_index += 1
        if self.wave_index % len(WAVE_BOOK) == 1 and self.wave_index > 1:
            self.rank += 1

    def add_particles(self, x, y, color, amount=10, speed=70, size=2):
        for _ in range(amount):
            a = random.random() * math.tau
            v = Vector2(math.cos(a), math.sin(a)) * random.uniform(18, speed)
            self.particles.append(Particle(Vector2(x, y), v, color, random.uniform(.35, .95), size=random.choice([1, size])))

    def explode_big(self, x, y, colors):
        for _ in range(65):
            a = random.random() * math.tau
            v = Vector2(math.cos(a), math.sin(a)) * random.uniform(25, 145)
            self.particles.append(Particle(Vector2(x, y), v, random.choice(colors), random.uniform(.45, 1.25), random.choice([1, 2, 3])))
        self.shake = max(self.shake, 0.35)
        self.flash = max(self.flash, 0.35)

    def maybe_drop_powerup(self, pos: Vector2, boss=False):
        if boss or random.random() < 0.13:
            if boss:
                choices = ["spread", "laser", "drone", "shield", "bomb", "repair"]
                count = 3
            else:
                choices = ["spread", "laser", "drone", "shield", "bomb", "repair", "repair"]
                count = 1
            for i in range(count):
                kind = random.choice(choices)
                self.powerups.append(PowerUp(pos.x + (i - count // 2) * 14, pos.y, kind))

    def handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.state = "quit"
            elif event.type == pygame.VIDEORESIZE:
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self._update_viewport()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN, pygame.K_HOME) and self.state in ("playing", "paused", "demo"):
                    self._adjust_time_scale(event.key)
                elif self.state == "demo":
                    self.exit_demo()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.state in ("title", "gameover", "victory"):
                    self.start()
                elif event.key == pygame.K_i and self.state == "title":
                    self.start_demo()
                elif event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "paused"
                    elif self.state == "paused":
                        self.state = "playing"
                elif event.key == pygame.K_r and self.state in ("playing", "paused"):
                    self.start()
                elif event.key == pygame.K_b and self.state == "playing" and self.player.bombs > 0:
                    self.use_bomb()
                if self.state == "title":
                    self.idle_timer = 0.0
        return events

    def update_background(self, dt):
        for s in self.stars:
            s[1] += s[2] * dt
            if s[1] > S.LOGICAL_HEIGHT:
                s[0] = random.randrange(S.LOGICAL_WIDTH)
                s[1] = -2
                s[2] = random.choice([12, 20, 34, 48])

    def draw_background(self):
        self.canvas.fill(C.BLACK)
        # Nebula blocks, deliberately square/pixel-like.
        for i in range(5):
            x = int((self.t * (3 + i) + i * 73) % (S.LOGICAL_WIDTH + 60)) - 60
            y = int((i * 47 + self.t * (7 + i)) % S.LOGICAL_HEIGHT)
            col = [C.DEEP, C.INK, (16, 10, 34), (8, 18, 32), (18, 12, 24)][i]
            pygame.draw.rect(self.canvas, col, (x, y, 46 + i * 8, 12 + i * 5))
        for x, y, speed, size in self.stars:
            color = C.WHITE if speed > 30 else C.GREY
            pygame.draw.rect(self.canvas, color, (int(x), int(y), size, size))

    def update_playing(self, dt):
        if self.state == "demo":
            keys, want_shoot, want_bomb = self.autopilot.decide(self, dt)
            if want_bomb and self.player.bombs > 0:
                self.use_bomb()
        else:
            keys = pygame.key.get_pressed()
            want_shoot = keys[pygame.K_SPACE] or keys[pygame.K_x] or keys[pygame.K_j]
        self.player.update(dt, keys)
        if want_shoot:
            if len(self.player_bullets) < S.MAX_PLAYER_BULLETS:
                self.player_bullets.extend(self.player.shoot())

        self.combo_t = max(0.0, self.combo_t - dt)
        if self.combo_t <= 0:
            self.combo = 0
        self.wave_banner = max(0.0, self.wave_banner - dt)
        self.next_wave_delay = max(0.0, self.next_wave_delay - dt)

        for b in self.player_bullets:
            b.update(dt)
        for b in self.enemy_bullets:
            b.update(dt)
        self.player_bullets = [b for b in self.player_bullets if b.alive]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive]

        # Enemy updates and support behavior.
        for e in list(self.enemies):
            self.enemy_bullets.extend(e.update(dt, self.t, self.player.pos))
            if e.kind == "builder" and e.heal_pulse <= 0 and random.random() < dt * 0.55:
                candidates = [x for x in self.enemies if x is not e and x.hp < x.max_hp and e.pos.distance_to(x.pos) < 55]
                if candidates:
                    target = random.choice(candidates)
                    target.hp += 1
                    e.heal_pulse = 1.5
                    self.add_particles(target.pos.x, target.pos.y, C.GREEN, 5, 34, 1)
        self.enemies = [e for e in self.enemies if e.alive]
        if len(self.enemy_bullets) > S.MAX_ENEMY_BULLETS:
            self.enemy_bullets = self.enemy_bullets[-S.MAX_ENEMY_BULLETS:]

        if self.boss:
            self.enemy_bullets.extend(self.boss.update(dt, self.player.pos))
            if not self.boss.alive:
                self.score += self.boss.score
                self.bosses_killed += 1
                self.explode_big(self.boss.pos.x, self.boss.pos.y, [C.MAGENTA, C.CYAN, C.YELLOW, C.WHITE])
                self.maybe_drop_powerup(self.boss.pos, boss=True)
                self.boss = None
                self.next_wave_delay = 2.2
                if self.bosses_killed >= 3:
                    self._enter_end_state("victory")

        self.handle_collisions()

        for p in self.powerups:
            p.update(dt, self.player.pos, self.player.magnet > 0)
        self.powerups = [p for p in self.powerups if p.alive]
        for p in list(self.powerups):
            if p.rect().colliderect(self.player.rect()):
                self.player.apply_powerup(p.kind)
                self.add_particles(p.pos.x, p.pos.y, p.color, 12, 80, 2)
                self.powerups.remove(p)

        for pt in self.particles:
            pt.update(dt)
        self.particles = [p for p in self.particles if p.alive]
        self.shake = max(0.0, self.shake - dt)
        self.flash = max(0.0, self.flash - dt)

        if not self.enemies and self.boss is None and self.state in ("playing", "demo") and self.next_wave_delay <= 0:
            self.next_wave_delay = 0.7
            self.spawn_next_wave()

        if self.player.lives <= 0:
            self._enter_end_state("gameover")

    def handle_collisions(self):
        for b in list(self.player_bullets):
            hit_any = False
            for e in list(self.enemies):
                if b.rect().colliderect(e.rect()):
                    killed = e.hit(b.damage)
                    hit_any = True
                    self.add_particles(b.pos.x, b.pos.y, b.color, 4, 45, 1)
                    if killed:
                        self.kills += 1
                        self.combo += 1
                        self.combo_t = 2.0
                        gain = e.score + max(0, self.combo - 1) * 3
                        self.score += gain
                        self.add_particles(e.pos.x, e.pos.y, C.ENEMY_PALETTES.get(e.kind, [C.WHITE])[0], 16, 95, 2)
                        self.maybe_drop_powerup(e.pos)
                        if e.kind == "splitter":
                            for dx in (-9, 9):
                                shard = Enemy("tile", e.pos.x + dx, e.pos.y, hp=1, rank=max(1, e.rank - 1))
                                shard.spawn = shard.pos.copy()
                                self.enemies.append(shard)
                        self.shake = max(self.shake, 0.08)
                    if b.pierce > 0:
                        b.pierce -= 1
                    else:
                        if b in self.player_bullets:
                            self.player_bullets.remove(b)
                    break
            if not hit_any and self.boss and b.rect().colliderect(self.boss.rect()):
                killed = self.boss.hit(b.damage)
                self.add_particles(b.pos.x, b.pos.y, b.color, 5, 60, 1)
                if b.pierce > 0:
                    b.pierce -= 1
                elif b in self.player_bullets:
                    self.player_bullets.remove(b)
                if killed:
                    return

        prect = self.player.rect()
        for b in list(self.enemy_bullets):
            if b.rect().colliderect(prect):
                self.add_particles(b.pos.x, b.pos.y, b.color, 10, 70, 2)
                if b in self.enemy_bullets:
                    self.enemy_bullets.remove(b)
                self.player.hurt()
                self.shake = max(self.shake, 0.22)
        for e in list(self.enemies):
            if e.rect().colliderect(prect):
                e.dead = True
                self.add_particles(e.pos.x, e.pos.y, C.RED, 14, 100, 2)
                self.player.hurt()
                self.shake = max(self.shake, 0.28)

    def draw_playing(self):
        for p in self.powerups:
            p.draw(self.canvas, self.font)
        for b in self.player_bullets:
            b.draw(self.canvas)
        for e in self.enemies:
            e.draw(self.canvas)
        if self.boss:
            self.boss.draw(self.canvas, self.font)
        for b in self.enemy_bullets:
            b.draw(self.canvas)
        self.player.draw(self.canvas)
        for pt in self.particles:
            pt.draw(self.canvas)
        self.draw_hud()
        if self.wave_banner > 0:
            y = 54
            pygame.draw.rect(self.canvas, C.BLACK, (0, y - 12, S.LOGICAL_WIDTH, 24))
            pygame.draw.rect(self.canvas, C.CYAN, (0, y - 12, S.LOGICAL_WIDTH, 1))
            pygame.draw.rect(self.canvas, C.MAGENTA, (0, y + 11, S.LOGICAL_WIDTH, 1))
            draw_text(self.canvas, self.font_med, self.wave_title, S.LOGICAL_WIDTH // 2, y - 6, C.WHITE, center=True)

    def draw_hud(self):
        w = S.LOGICAL_WIDTH
        pygame.draw.rect(self.canvas, (2, 3, 9), (0, 0, w, 13))
        draw_text(self.canvas, self.font, f"SCORE {self.score:06d}", 4, 3, C.WHITE)
        draw_text(self.canvas, self.font, f"VIES {self.player.lives}", round(w * 0.35), 3, C.GREEN if self.player.lives > 1 else C.RED)
        draw_text(self.canvas, self.font, f"BOMBES {self.player.bombs}", round(w * 0.5125), 3, C.ORANGE)
        weapon = self.player.weapon.upper()
        if self.player.weapon != "basic":
            weapon += f" L{self.player.weapon_level} {int(self.player.weapon_timer)}s"
        draw_text(self.canvas, self.font, weapon, round(w * 0.725), 3, C.CYAN if self.player.weapon == "laser" else C.MAGENTA if self.player.weapon == "spread" else C.WHITE)
        if self.combo > 2:
            draw_text(self.canvas, self.font, f"COMBO x{self.combo}", 4, 16, C.YELLOW)
        if self.player.shield > 0:
            draw_bar(self.canvas, pygame.Rect(round(w * 0.35), 16, 54, 4), self.player.shield / 12, C.GREEN)
        if self.player.magnet > 0:
            draw_text(self.canvas, self.font, "MAGNET", round(w * 0.5438), 15, C.CYAN)
        if self.time_scale != 1.0:
            draw_text(self.canvas, self.font, f"x{self.time_scale:.1f}", w - 34, 3, C.YELLOW)

    def draw_demo_overlay(self):
        if int(self.t * 2) % 2 == 0:
            draw_text(self.canvas, self.font, "MODE DEMO (IA) - Appuyez sur une touche", S.LOGICAL_WIDTH // 2, S.LOGICAL_HEIGHT - 10, C.YELLOW, center=True)
        draw_text(self.canvas, self.font, f"Vitesse x{self.time_scale:.1f}  (PageUp/PageDown, Home=x1)", S.LOGICAL_WIDTH // 2, S.LOGICAL_HEIGHT - 20, C.CYAN, center=True)

    def draw_title(self):
        self.draw_background()
        draw_text(self.canvas, self.font_big, "MOSAIC", S.LOGICAL_WIDTH // 2, 48, C.CYAN, center=True)
        draw_text(self.canvas, self.font_big, "STAR RAIDERS", S.LOGICAL_WIDTH // 2, 72, C.MAGENTA, center=True)
        draw_text(self.canvas, self.font_med, "shoot'em up retro-moderne", S.LOGICAL_WIDTH // 2, 104, C.WHITE, center=True)
        lines = [
            "Fleches/WASD/ZQSD : bouger",
            "ESPACE / X / J : tirer",
            "B : bombe   ESC : pause   R : restart",
            "I : mode demo (IA aux commandes)",
            "PageUp/PageDown : vitesse (x2 en jeu, x5 en demo)",
            "Entree ou Espace pour lancer",
        ]
        for i, line in enumerate(lines):
            draw_text(self.canvas, self.font, line, S.LOGICAL_WIDTH // 2, 132 + i * 14, C.GREY if i < len(lines) - 1 else C.YELLOW, center=True)
        self.draw_mini_mosaic_logo()

    def draw_mini_mosaic_logo(self):
        cx, cy = S.LOGICAL_WIDTH // 2, 24
        colors = [C.CYAN, C.MAGENTA, C.YELLOW, C.WHITE]
        pattern = ["01111110", "11011011", "11111111", "00100100"]
        tile = 3
        start_x = cx - len(pattern[0]) * tile // 2
        for y, row in enumerate(pattern):
            for x, ch in enumerate(row):
                if ch == "1":
                    pygame.draw.rect(self.canvas, colors[(x + y) % len(colors)], (start_x + x * tile, cy + y * tile, tile - 1, tile - 1))

    def draw_end_screen(self, title, subtitle, color):
        self.draw_background()
        for pt in self.particles:
            pt.draw(self.canvas)
        draw_text(self.canvas, self.font_big, title, S.LOGICAL_WIDTH // 2, 64, color, center=True)
        draw_text(self.canvas, self.font_med, subtitle, S.LOGICAL_WIDTH // 2, 98, C.WHITE, center=True)
        draw_text(self.canvas, self.font_med, f"SCORE {self.score}", S.LOGICAL_WIDTH // 2, 124, C.YELLOW, center=True)
        draw_text(self.canvas, self.font, "Entree / Espace : rejouer", S.LOGICAL_WIDTH // 2, 158, C.GREY, center=True)

    def draw_pause(self):
        self.draw_playing()
        overlay = pygame.Surface((S.LOGICAL_WIDTH, S.LOGICAL_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.canvas.blit(overlay, (0, 0))
        draw_text(self.canvas, self.font_big, "PAUSE", S.LOGICAL_WIDTH // 2, 94, C.WHITE, center=True)
        draw_text(self.canvas, self.font, "ESC pour reprendre", S.LOGICAL_WIDTH // 2, 122, C.GREY, center=True)

    def render(self):
        if self.state == "title":
            self.draw_title()
        elif self.state == "playing":
            self.draw_background()
            self.draw_playing()
        elif self.state == "demo":
            self.draw_background()
            self.draw_playing()
            self.draw_demo_overlay()
        elif self.state == "paused":
            self.draw_background()
            self.draw_pause()
        elif self.state == "gameover":
            self.draw_end_screen("GAME OVER", "la mosaique t'a submerge", C.RED)
            if self.demo_mode:
                self.draw_demo_overlay()
        elif self.state == "victory":
            self.draw_end_screen("VICTOIRE", "les 100 points sont neutralises", C.GREEN)
            if self.demo_mode:
                self.draw_demo_overlay()

        if self.flash > 0:
            f = pygame.Surface((S.LOGICAL_WIDTH, S.LOGICAL_HEIGHT), pygame.SRCALPHA)
            f.fill((255, 255, 255, int(120 * self.flash)))
            self.canvas.blit(f, (0, 0))

        target = self.screen
        dest = self.canvas
        if self.shake > 0:
            ox = random.randint(-2, 2)
            oy = random.randint(-2, 2)
            temp = pygame.Surface((S.LOGICAL_WIDTH, S.LOGICAL_HEIGHT))
            temp.fill(C.BLACK)
            temp.blit(self.canvas, (ox, oy))
            dest = temp
        target.fill(C.BLACK)
        scaled = pygame.transform.scale(dest, self.viewport.size)
        target.blit(scaled, self.viewport.topleft)
        pygame.display.flip()

    def tick(self) -> float:
        dt = min(0.033, self.clock.tick(S.FPS) / 1000.0)
        self.handle_events()
        if self.state in ("playing", "demo"):
            # Sub-step at a fixed dt so speeding up (time_scale > 1) runs more
            # whole physics steps per rendered frame instead of one step with
            # a huge dt (which would let fast bullets tunnel through the
            # player). Slowing down (time_scale < 1) simply runs a step less
            # often via the fractional accumulator.
            self._step_accumulator += max(0.0, self.time_scale)
            steps = int(self._step_accumulator)
            self._step_accumulator -= steps
            for _ in range(steps):
                self.t += dt
                self.update_background(dt)
                self.update_playing(dt)
                if self.state not in ("playing", "demo"):
                    break
        else:
            self.t += dt
            self.update_background(dt)
            if self.state in ("title", "gameover", "victory"):
                for pt in self.particles:
                    pt.update(dt)
                self.particles = [p for p in self.particles if p.alive]
                if self.state == "title" and not self.demo_mode:
                    self.idle_timer += dt
                    if self.idle_timer >= S.DEMO_IDLE_TIMEOUT:
                        self.start_demo()
                elif self.demo_mode:
                    self.demo_restart_delay -= dt
                    if self.demo_restart_delay <= 0:
                        self.start_demo()
        self.render()
        return dt
