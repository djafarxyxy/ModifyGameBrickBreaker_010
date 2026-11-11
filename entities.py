"""Objek-objek yang bergerak di dalam game."""

import math
import random

import pygame

from settings import (
    BALL_COLOR,
    HEIGHT,
    NEON,
    PADDLE_COLOR,
    WHITE,
    WIDTH,
)


class GameObject:
    """Kelas dasar buat semua objek yang punya posisi dan ukuran."""

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = (x, y)
        self.alive = True

    def update(self, dt, game):
        pass

    def draw(self, surface):
        pass


class Paddle(GameObject):
    """Pemukul di bagian bawah layar."""

    def __init__(self):
        super().__init__(WIDTH // 2, HEIGHT - 58, 110, 16)
        self.speed = 660
        self.target_width = 110
        self.keyboard_dir = 0

    def handle_key(self, key, pressed):
        if key in (pygame.K_LEFT, pygame.K_a):
            self.keyboard_dir = -1 if pressed else 0
        elif key in (pygame.K_RIGHT, pygame.K_d):
            self.keyboard_dir = 1 if pressed else 0

    def move_to_mouse(self, mouse_x):
        self.rect.centerx = mouse_x
        self.clamp()

    def clamp(self):
        if self.rect.left < 8:
            self.rect.left = 8
        if self.rect.right > WIDTH - 8:
            self.rect.right = WIDTH - 8

    def update(self, dt, game):
        self.rect.x += self.keyboard_dir * self.speed * dt
        self.clamp()

        # lebar paddle diubah perlahan biar tidak lompat saat kena power up
        if self.rect.width != self.target_width:
            center = self.rect.centerx
            diff = self.target_width - self.rect.width
            step = max(1, int(abs(diff) * 8 * dt))
            if abs(diff) <= step:
                self.rect.width = self.target_width
            else:
                self.rect.width += step if diff > 0 else -step
            self.rect.centerx = center
            self.clamp()

    def draw(self, surface):
        glow = pygame.Surface((self.rect.width + 24, self.rect.height + 24), pygame.SRCALPHA)
        pygame.draw.rect(
            glow,
            (*NEON, 40),
            glow.get_rect(),
            border_radius=18,
        )
        surface.blit(glow, (self.rect.x - 12, self.rect.y - 12))
        pygame.draw.rect(surface, PADDLE_COLOR, self.rect, border_radius=8)
        pygame.draw.rect(
            surface,
            (200, 250, 255),
            self.rect.inflate(-10, -8),
            width=1,
            border_radius=4,
        )


class Ball(GameObject):
    """Bola yang memantul dan menghancurkan bata."""

    def __init__(self, x, y, speed=430):
        super().__init__(x, y, 16, 16)
        self.radius = 8
        self.speed = speed
        self.pos_x = float(x)
        self.pos_y = float(y)
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.stuck = True
        self.lost = False

    def launch(self):
        angle = random.uniform(-0.9, 0.9)
        self.vel_x = math.sin(angle) * self.speed
        self.vel_y = -abs(math.cos(angle) * self.speed)
        self.stuck = False

    def sync_rect(self):
        self.rect.center = (round(self.pos_x), round(self.pos_y))

    def update(self, dt, game):
        if self.stuck:
            self.pos_x = game.paddle.rect.centerx
            self.pos_y = game.paddle.rect.top - self.radius - 2
            self.sync_rect()
            return

        self.pos_x += self.vel_x * dt
        self.pos_y += self.vel_y * dt

        # pantulan di dinding kiri dan kanan
        if self.pos_x - self.radius <= 0:
            self.pos_x = self.radius
            self.vel_x = abs(self.vel_x)
        elif self.pos_x + self.radius >= WIDTH:
            self.pos_x = WIDTH - self.radius
            self.vel_x = -abs(self.vel_x)

        # pantulan di langit-langit
        if self.pos_y - self.radius <= game.top_boundary:
            self.pos_y = game.top_boundary + self.radius
            self.vel_y = abs(self.vel_y)

        if self.pos_y - self.radius > HEIGHT:
            self.lost = True

        self.sync_rect()

    def draw(self, surface):
        # bayangan tipis biar bola kelihatan menyala
        glow = pygame.Surface((self.radius * 5, self.radius * 5), pygame.SRCALPHA)
        pygame.draw.circle(
            glow,
            (0, 229, 255, 55),
            (self.radius * 2, self.radius * 2),
            self.radius * 2,
        )
        surface.blit(glow, (self.rect.centerx - self.radius * 2, self.rect.centery - self.radius * 2))
        pygame.draw.circle(surface, BALL_COLOR, self.rect.center, self.radius)
        pygame.draw.circle(surface, (255, 255, 255), self.rect.center, self.radius, 1)


class Brick(GameObject):
    """Bata yang bisa dihancurkan dengan beberapa kali pukulan."""

    def __init__(self, x, y, width, height, color, hp=1, points=10):
        super().__init__(x, y, width, height)
        self.color = color
        self.max_hp = hp
        self.hp = hp
        self.points = points

    def hit(self, damage=1):
        self.hp -= damage
        if self.hp <= 0:
            self.alive = False
        return not self.alive

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=5)
        # sisi atas lebih terang, sisi bawah lebih gelap -> kesan 3D
        top = self.rect.inflate(-4, -4)
        top.height = max(3, self.rect.height // 3)
        lighter = tuple(min(255, c + 60) for c in self.color)
        darker = tuple(max(0, c - 70) for c in self.color)
        pygame.draw.rect(surface, lighter, top, border_radius=3)
        pygame.draw.line(
            surface,
            darker,
            (self.rect.left + 4, self.rect.bottom - 3),
            (self.rect.right - 4, self.rect.bottom - 3),
            2,
        )
        if self.max_hp > 1:
            pygame.draw.circle(surface, (255, 255, 255), self.rect.center, 4)
            pygame.draw.circle(surface, self.color, self.rect.center, 2)


def circle_rect_collision(ball, rect):
    """Cek tabrakan bola dengan persegi, sekaligus hitung arah pantulnya."""
    closest_x = max(rect.left, min(ball.pos_x, rect.right))
    closest_y = max(rect.top, min(ball.pos_y, rect.bottom))
    dx = ball.pos_x - closest_x
    dy = ball.pos_y - closest_y
    distance = math.hypot(dx, dy)

    if distance > ball.radius:
        return None

    if distance == 0:
        # bola masuk ke dalam persegi, pakai sisi yang paling dekat
        overlap_left = abs(ball.pos_x - rect.left)
        overlap_right = abs(rect.right - ball.pos_x)
        overlap_top = abs(ball.pos_y - rect.top)
        overlap_bottom = abs(rect.bottom - ball.pos_y)
        smallest = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
        if smallest == overlap_left:
            return -1.0, 0.0
        if smallest == overlap_right:
            return 1.0, 0.0
        if smallest == overlap_top:
            return 0.0, -1.0
        return 0.0, 1.0

    return dx / distance, dy / distance


def reflect(ball, normal):
    """Pantulkan kecepatan bola terhadap garis normal tabrakan."""
    dot = ball.vel_x * normal[0] + ball.vel_y * normal[1]
    if dot < 0:
        ball.vel_x -= 2 * dot * normal[0]
        ball.vel_y -= 2 * dot * normal[1]
