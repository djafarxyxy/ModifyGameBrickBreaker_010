"""Komponen tampilan: tombol, panel, dan teks bantuan."""

import pygame

from settings import (
    DARK,
    HEIGHT,
    MUTED,
    NEON,
    PINK,
    WHITE,
    WIDTH,
    YELLOW,
)


class Button:
    """Tombol sederhana yang bisa diklik pakai mouse."""

    def __init__(self, center_x, y, width, height, label, action, hint=""):
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.centerx = center_x
        self.rect.y = y
        self.label = label
        self.action = action
        self.hint = hint

    def is_hovered(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def draw(self, surface, font, mouse_pos):
        hovered = self.is_hovered(mouse_pos)
        fill = (36, 46, 82) if hovered else (24, 30, 54)
        border = NEON if hovered else (58, 70, 108)

        pygame.draw.rect(surface, fill, self.rect, border_radius=10)
        pygame.draw.rect(surface, border, self.rect, width=2, border_radius=10)

        color = WHITE if hovered else (206, 214, 236)
        text = font.render(self.label, True, color)
        surface.blit(text, (self.rect.centerx - text.get_width() // 2, self.rect.centery - text.get_height() // 2))


def draw_panel(surface, rect, alpha=220, border=(54, 64, 98)):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, (14, 18, 34, alpha), panel.get_rect(), border_radius=16)
    surface.blit(panel, rect.topleft)
    pygame.draw.rect(surface, border, rect, width=2, border_radius=16)


def draw_overlay(surface, alpha=200):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((5, 7, 16, alpha))
    surface.blit(overlay, (0, 0))


def draw_title(surface, text, font, y, color=WHITE, glow=NEON):
    """Judul dengan efek glow tipis di belakangnya."""
    glow_text = font.render(text, True, glow)
    for offset in ((0, 0), (2, 2), (-2, 2), (2, -2), (-2, -2)):
        glow_text.set_alpha(90)
        surface.blit(glow_text, (WIDTH // 2 - glow_text.get_width() // 2 + offset[0], y + offset[1]))
    main = font.render(text, True, color)
    surface.blit(main, (WIDTH // 2 - main.get_width() // 2, y))
    return main


def draw_menu(surface, fonts, buttons, mouse_pos, best_score=0):
    draw_decor(surface)

    title_font, subtitle_font = fonts
    draw_title(surface, "BRICK BREAKER", title_font, 120)

    subtitle = subtitle_font.render("Tugas Multipatform - Implementasi OOP di GUI", True, MUTED)
    surface.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 205))

    if best_score:
        best = subtitle_font.render(f"Skor tertinggi: {best_score}", True, YELLOW)
        surface.blit(best, (WIDTH // 2 - best.get_width() // 2, 240))

    for button in buttons:
        button.draw(surface, subtitle_font, mouse_pos)


def draw_decor(surface):
    """Hiasan bata transparan di belakang menu."""
    layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    colors = [(255, 74, 138, 26), (255, 138, 76, 22), (0, 229, 255, 20)]
    size, gap = 62, 8
    for row in range(4):
        for col in range(12):
            x = 30 + col * (size + gap)
            y = HEIGHT - 150 + row * 24
            color = colors[(row + col) % len(colors)]
            pygame.draw.rect(layer, color, (x, y, size, 16), border_radius=4)
    for row in range(3):
        for col in range(12):
            x = 60 + col * (size + gap)
            y = 40 + row * 24
            color = colors[(row + col) % len(colors)]
            pygame.draw.rect(layer, color, (x, y, size, 16), border_radius=4)
    surface.blit(layer, (0, 0))


HOW_TO_PLAY = [
    ("Panah kiri / kanan atau A / D", "geser paddle"),
    ("Mouse", "geser paddle langsung"),
    ("SPACE", "luncurkan bola"),
    ("ESC / P", "pause game"),
    ("R", "ulang level"),
    ("M", "kembali ke menu"),
    ("", ""),
    ("Hancurkan semua bata", "buat naik level"),
    ("Bata putih", "butuh dua kali pukulan"),
    ("Bata abu-abu", "tidak bisa dihancurkan"),
]


def draw_how_to(surface, fonts, back_button, mouse_pos):
    draw_overlay(surface, 220)
    title_font, body_font = fonts
    draw_title(surface, "CARA BERMAIN", title_font, 90, glow=PINK)

    panel = pygame.Rect(180, 180, WIDTH - 360, 300)
    draw_panel(surface, panel, 235)

    y = panel.y + 26
    for label, description in HOW_TO_PLAY:
        if not label:
            y += 12
            continue
        key_text = body_font.render(label, True, NEON)
        desc_text = body_font.render(description, True, WHITE if label in ("Hancurkan semua bata", "Bata putih", "Bata abu-abu") else MUTED)
        surface.blit(key_text, (panel.x + 28, y))
        surface.blit(desc_text, (panel.x + 330, y))
        y += 27

    back_button.draw(surface, body_font, mouse_pos)


def draw_pause(surface, fonts, buttons, mouse_pos):
    draw_overlay(surface, 190)
    title_font, body_font = fonts
    draw_title(surface, "PAUSE", title_font, HEIGHT // 2 - 140, glow=NEON)
    for button in buttons:
        button.draw(surface, body_font, mouse_pos)


def draw_game_over(surface, fonts, buttons, mouse_pos, score, best_score):
    draw_overlay(surface, 215)
    title_font, body_font = fonts
    draw_title(surface, "GAME OVER", title_font, HEIGHT // 2 - 190, glow=PINK)

    score_text = body_font.render(f"Skor kamu: {score}", True, WHITE)
    surface.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2 - 90))

    if score >= best_score and score > 0:
        record = body_font.render("Rekor baru!", True, YELLOW)
        surface.blit(record, (WIDTH // 2 - record.get_width() // 2, HEIGHT // 2 - 52))
    else:
        best = body_font.render(f"Skor tertinggi: {best_score}", True, MUTED)
        surface.blit(best, (WIDTH // 2 - best.get_width() // 2, HEIGHT // 2 - 52))

    for button in buttons:
        button.draw(surface, body_font, mouse_pos)


def draw_level_clear(surface, fonts, buttons, mouse_pos, level_name, bonus):
    draw_overlay(surface, 200)
    title_font, body_font = fonts
    draw_title(surface, "LEVEL SELESAI", title_font, HEIGHT // 2 - 170, glow=(86, 227, 159))

    name = body_font.render(level_name, True, WHITE)
    surface.blit(name, (WIDTH // 2 - name.get_width() // 2, HEIGHT // 2 - 70))

    bonus_text = body_font.render(f"Bonus level +{bonus}", True, YELLOW)
    surface.blit(bonus_text, (WIDTH // 2 - bonus_text.get_width() // 2, HEIGHT // 2 - 34))

    for button in buttons:
        button.draw(surface, body_font, mouse_pos)


def draw_win(surface, fonts, buttons, mouse_pos, score):
    draw_overlay(surface, 205)
    title_font, body_font = fonts
    draw_title(surface, "GANJARAN BUAT KAMU", title_font, HEIGHT // 2 - 190, glow=YELLOW)
    text = body_font.render(f"Semua level selesai dengan skor {score}", True, WHITE)
    surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 80))
    for button in buttons:
        button.draw(surface, body_font, mouse_pos)
