"""Konstanta dan pengaturan yang dipakai semua bagian game."""

import pygame

# ukuran layar
WIDTH, HEIGHT = 900, 640
FPS = 60
TITLE = "Brick Breaker"

# batas area bermain
HUD_HEIGHT = 48
PLAY_TOP = HUD_HEIGHT
PLAY_BOTTOM = HEIGHT

# warna dasar
BG_TOP = (8, 12, 28)
BG_BOTTOM = (28, 18, 52)
WHITE = (240, 244, 255)
MUTED = (138, 148, 180)
DARK = (18, 22, 40)

NEON = (0, 229, 255)
PINK = (255, 74, 138)
YELLOW = (255, 206, 84)
GREEN = (86, 227, 159)
ORANGE = (255, 138, 76)
PURPLE = (167, 108, 255)
RED = (255, 74, 74)

PADDLE_COLOR = NEON
BALL_COLOR = WHITE

# warna tiap baris bata, dipakai bergantian
ROW_COLORS = [PINK, ORANGE, YELLOW, GREEN, NEON, PURPLE]

FONT_NAME = "segoeui"


def get_font(size, bold=True):
    """Bikin font dengan ukuran tertentu, fallback ke font bawaan pygame."""
    try:
        font = pygame.font.SysFont(FONT_NAME, size, bold=bold)
    except Exception:
        font = pygame.font.Font(None, size)
    return font
