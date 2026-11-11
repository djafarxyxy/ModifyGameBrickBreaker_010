"""Power up yang jatuh dari bata dan bisa ditangkap paddle."""

import random

import pygame

from settings import GREEN, NEON, ORANGE, PINK, PURPLE, get_font

_font = None


def get_powerup_font():
    global _font
    if _font is None:
        _font = get_font(16)
    return _font


class PowerUp:
    """Kapsul yang jatuh ke bawah, efeknya diatur di subclass."""

    letter = "?"
    color = NEON
    weight = 10

    def __init__(self, x, y):
        self.rect = pygame.Rect(0, 0, 26, 26)
        self.rect.center = (x, y)
        self.speed = 160
        self.alive = True
        self.phase = random.uniform(0, 6.28)

    def update(self, dt, game):
        self.rect.y += self.speed * dt
        self.phase += dt * 4
        if self.rect.top > game.screen.get_height():
            self.alive = False

    def draw(self, surface):
        glow = pygame.Surface((54, 54), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*self.color, 45), (27, 27), 22)
        surface.blit(glow, (self.rect.centerx - 27, self.rect.centery - 27))

        pygame.draw.rect(surface, (18, 22, 38), self.rect, border_radius=8)
        pygame.draw.rect(surface, self.color, self.rect, width=2, border_radius=8)

        font = get_powerup_font()
        text = font.render(self.letter, True, self.color)
        surface.blit(text, (self.rect.centerx - text.get_width() // 2, self.rect.centery - text.get_height() // 2))

    def apply(self, game):
        raise NotImplementedError


class ExpandPower(PowerUp):
    letter = "E"
    color = GREEN
    weight = 30

    def apply(self, game):
        game.activate_expand()


class MultiBallPower(PowerUp):
    letter = "M"
    color = PURPLE
    weight = 20

    def apply(self, game):
        game.spawn_extra_balls()


class SlowPower(PowerUp):
    letter = "S"
    color = NEON
    weight = 20

    def apply(self, game):
        game.activate_slow()


class LifePower(PowerUp):
    letter = "+"
    color = PINK
    weight = 10

    def apply(self, game):
        game.lives = min(5, game.lives + 1)


class LaserPower(PowerUp):
    letter = "L"
    color = ORANGE
    weight = 20

    def apply(self, game):
        game.activate_laser()


POWERUP_TYPES = [ExpandPower, MultiBallPower, SlowPower, LifePower, LaserPower]


def random_powerup(x, y):
    weights = [powerup.weight for powerup in POWERUP_TYPES]
    chosen = random.choices(POWERUP_TYPES, weights=weights, k=1)[0]
    return chosen(x, y)
