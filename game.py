"""Inti permainan: mengatur state, input, tabrakan, dan render."""

import pygame

from entities import Ball, Brick, Paddle, circle_rect_collision, reflect
from levels import LEVELS
from settings import (
    BG_BOTTOM,
    BG_TOP,
    FPS,
    HEIGHT,
    HUD_HEIGHT,
    MUTED,
    NEON,
    PINK,
    TITLE,
    WHITE,
    WIDTH,
    YELLOW,
    get_font,
)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.background = self.make_background()

        self.font_big = get_font(56)
        self.font_medium = get_font(26)
        self.font_small = get_font(18)
        self.font_tiny = get_font(15)

        self.state = "playing"
        self.score = 0
        self.lives = 3
        self.level_index = 0
        self.running = True

        self.paddle = Paddle()
        self.balls = []
        self.bricks = []
        self.top_boundary = HUD_HEIGHT
        self.load_level(0)

    # ------------------------------------------------------------------ setup
    def make_background(self):
        surface = pygame.Surface((WIDTH, HEIGHT))
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            color = (
                int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * ratio),
                int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * ratio),
                int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * ratio),
            )
            pygame.draw.line(surface, color, (0, y), (WIDTH, y))
        return surface

    def load_level(self, index):
        self.level_index = index
        level = LEVELS[index]
        self.bricks = level.build_bricks(Brick)
        self.spawn_ball(level.speed)

    def spawn_ball(self, speed):
        ball = Ball(self.paddle.rect.centerx, self.paddle.rect.top - 30, speed)
        self.balls = [ball]

    def reset_after_life_lost(self):
        self.paddle.rect.width = 110
        self.paddle.target_width = 110
        self.paddle.rect.centerx = WIDTH // 2
        self.spawn_ball(LEVELS[self.level_index].speed)

    # ------------------------------------------------------------------ loop
    def run(self):
        while self.running:
            dt = min(self.clock.tick(FPS) / 1000.0, 0.033)
            self.handle_events()
            if self.running:
                self.update(dt)
                self.draw()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    if self.state == "playing":
                        for ball in self.balls:
                            if ball.stuck:
                                ball.launch()
                    elif self.state == "game_over":
                        self.restart()
                elif self.state == "playing":
                    self.paddle.handle_key(event.key, True)
            elif event.type == pygame.KEYUP:
                self.paddle.handle_key(event.key, False)
            elif event.type == pygame.MOUSEMOTION and self.state == "playing":
                self.paddle.move_to_mouse(event.pos[0])

    def restart(self):
        self.score = 0
        self.lives = 3
        self.load_level(0)
        self.state = "playing"

    # ------------------------------------------------------------------ update
    def update(self, dt):
        if self.state != "playing":
            return

        self.paddle.update(dt, self)
        for ball in self.balls:
            ball.update(dt, self)

        for ball in self.balls:
            self.handle_paddle_collision(ball)
            self.handle_brick_collision(ball)

        alive_balls = [ball for ball in self.balls if not ball.lost]
        if len(alive_balls) != len(self.balls):
            self.balls = alive_balls
            if not self.balls:
                self.lose_life()

        if not any(brick.alive for brick in self.bricks):
            self.next_level()

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.state = "game_over"
            self.lives = 0
        else:
            self.reset_after_life_lost()

    def next_level(self):
        self.load_level((self.level_index + 1) % len(LEVELS))

    def handle_paddle_collision(self, ball):
        if ball.stuck or not ball.rect.colliderect(self.paddle.rect):
            return
        if ball.vel_y <= 0:
            return

        ball.pos_y = self.paddle.rect.top - ball.radius
        offset = (ball.pos_x - self.paddle.rect.centerx) / (self.paddle.rect.width / 2)
        offset = max(-1.0, min(1.0, offset))
        speed = max(300, (ball.vel_x ** 2 + ball.vel_y ** 2) ** 0.5)
        angle = offset * 1.05
        ball.vel_x = speed * angle
        ball.vel_y = -abs(speed * (1 - abs(angle) * 0.35))
        ball.sync_rect()

    def handle_brick_collision(self, ball):
        if ball.stuck:
            return
        for brick in self.bricks:
            if not brick.alive or not brick.rect.colliderect(ball.rect):
                continue
            normal = circle_rect_collision(ball, brick.rect)
            if normal is None:
                continue
            reflect(ball, normal)
            # dorong bola keluar dari bata biar tidak nyangkut
            ball.pos_x += normal[0] * 2
            ball.pos_y += normal[1] * 2
            ball.sync_rect()
            if brick.hit():
                self.score += brick.points
                self.bricks.remove(brick)
            break

    # ------------------------------------------------------------------ render
    def draw(self):
        screen = self.screen
        screen.blit(self.background, (0, 0))

        for brick in self.bricks:
            if brick.alive:
                brick.draw(screen)
        self.paddle.draw(screen)
        for ball in self.balls:
            ball.draw(screen)

        self.draw_hud()

        if self.state == "game_over":
            self.draw_game_over()

        pygame.display.flip()

    def draw_hud(self):
        bar = pygame.Surface((WIDTH, HUD_HEIGHT), pygame.SRCALPHA)
        bar.fill((10, 14, 30, 200))
        self.screen.blit(bar, (0, 0))
        pygame.draw.line(self.screen, (40, 48, 76), (0, HUD_HEIGHT - 1), (WIDTH, HUD_HEIGHT - 1))

        score = self.font_small.render("SKOR", True, MUTED)
        score_value = self.font_medium.render(str(self.score), True, WHITE)
        self.screen.blit(score, (24, 6))
        self.screen.blit(score_value, (24, 22))

        level = LEVELS[self.level_index]
        name = self.font_small.render(f"LEVEL {self.level_index + 1} - {level.name.upper()}", True, NEON)
        self.screen.blit(name, (WIDTH // 2 - name.get_width() // 2, 15))

        for i in range(max(3, self.lives)):
            color = PINK if i < self.lives else (60, 66, 90)
            pygame.draw.circle(self.screen, color, (WIDTH - 34 - i * 24, 24), 7)

    def draw_game_over(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((6, 8, 18, 210))
        self.screen.blit(overlay, (0, 0))

        title = self.font_big.render("GAME OVER", True, PINK)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 2 - 90))

        score = self.font_medium.render(f"Skor akhir: {self.score}", True, WHITE)
        self.screen.blit(score, (WIDTH // 2 - score.get_width() // 2, HEIGHT // 2 - 10))

        hint = self.font_small.render("Tekan SPACE untuk main lagi, ESC untuk keluar", True, YELLOW)
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT // 2 + 50))
