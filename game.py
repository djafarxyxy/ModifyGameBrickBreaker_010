"""Inti permainan: mengatur state, input, tabrakan, dan render."""

import pygame

import ui
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

        self.font_title = get_font(64)
        self.font_big = get_font(48)
        self.font_medium = get_font(26)
        self.font_small = get_font(18)
        self.font_tiny = get_font(15)

        self.state = "menu"
        self.score = 0
        self.best_score = 0
        self.lives = 3
        self.level_index = 0
        self.running = True

        self.paddle = Paddle()
        self.balls = []
        self.bricks = []
        self.top_boundary = HUD_HEIGHT
        self.load_level(0)

        self.build_buttons()

    def build_buttons(self):
        center = WIDTH // 2
        self.menu_buttons = [
            ui.Button(center, 320, 260, 52, "MULAI", "start", "ENTER"),
            ui.Button(center, 392, 260, 52, "CARA BERMAIN", "howto", ""),
            ui.Button(center, 464, 260, 52, "KELUAR", "quit", ""),
        ]
        self.howto_buttons = [ui.Button(center, 520, 220, 46, "KEMBALI", "menu", "ESC")]
        self.pause_buttons = [
            ui.Button(center, 300, 240, 48, "LANJUT", "resume", "ESC"),
            ui.Button(center, 364, 240, 48, "ULANG LEVEL", "restart_level", "R"),
            ui.Button(center, 428, 240, 48, "MENU", "menu", "M"),
        ]
        self.game_over_buttons = [
            ui.Button(center, 400, 240, 48, "MAIN LAGI", "start", "ENTER"),
            ui.Button(center, 464, 240, 48, "MENU", "menu", "M"),
        ]
        self.level_clear_buttons = [
            ui.Button(center, 400, 240, 48, "LANJUT", "next_level", "ENTER"),
            ui.Button(center, 464, 240, 48, "MENU", "menu", "M"),
        ]
        self.win_buttons = [
            ui.Button(center, 400, 240, 48, "MAIN LAGI", "start", "ENTER"),
            ui.Button(center, 464, 240, 48, "MENU", "menu", "M"),
        ]

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
            if not self.running:
                break
            self.update(dt)
            self.draw()
        pygame.quit()

    def current_buttons(self):
        if self.state == "menu":
            return self.menu_buttons
        if self.state == "howto":
            return self.howto_buttons
        if self.state == "paused":
            return self.pause_buttons
        if self.state == "game_over":
            return self.game_over_buttons
        if self.state == "level_clear":
            return self.level_clear_buttons
        if self.state == "win":
            return self.win_buttons
        return []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in self.current_buttons():
                    if button.is_hovered(event.pos):
                        self.do_action(button.action)
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)
            elif event.type == pygame.KEYUP:
                self.paddle.handle_key(event.key, False)
            elif event.type == pygame.MOUSEMOTION and self.state == "playing":
                self.paddle.move_to_mouse(event.pos[0])

    def handle_keydown(self, event):
        key = event.key

        if self.state == "playing":
            if key == pygame.K_SPACE:
                for ball in self.balls:
                    if ball.stuck:
                        ball.launch()
            elif key in (pygame.K_ESCAPE, pygame.K_p):
                self.state = "paused"
            elif key == pygame.K_r:
                self.start_level(self.level_index)
            elif key == pygame.K_m:
                self.state = "menu"
            else:
                self.paddle.handle_key(key, True)

        elif self.state == "menu":
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                self.do_action("start")
            elif key == pygame.K_ESCAPE:
                self.running = False

        elif self.state == "howto":
            if key == pygame.K_ESCAPE:
                self.do_action("menu")

        elif self.state == "paused":
            if key in (pygame.K_ESCAPE, pygame.K_p):
                self.do_action("resume")
            elif key == pygame.K_r:
                self.do_action("restart_level")
            elif key == pygame.K_m:
                self.do_action("menu")

        elif self.state in ("game_over", "level_clear", "win"):
            if key in (pygame.K_RETURN, pygame.K_SPACE):
                action = "next_level" if self.state == "level_clear" else "start"
                self.do_action(action)
            elif key == pygame.K_m:
                self.do_action("menu")

    def do_action(self, action):
        if action == "start":
            self.start_game()
        elif action == "howto":
            self.state = "howto"
        elif action == "menu":
            self.state = "menu"
        elif action == "quit":
            self.running = False
        elif action == "resume":
            self.state = "playing"
        elif action == "restart_level":
            self.start_level(self.level_index)
        elif action == "next_level":
            self.next_level()

    def start_game(self):
        self.score = 0
        self.lives = 3
        self.start_level(0)

    def start_level(self, index):
        self.load_level(index)
        self.paddle.rect.width = 110
        self.paddle.target_width = 110
        self.paddle.rect.centerx = WIDTH // 2
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
            self.finish_level()

    def lose_life(self):
        self.lives -= 1
        if self.lives <= 0:
            self.lives = 0
            self.state = "game_over"
        else:
            self.reset_after_life_lost()

    def finish_level(self):
        self.state = "level_clear"

    def next_level(self):
        if self.level_index + 1 >= len(LEVELS):
            self.state = "win"
            return
        self.start_level(self.level_index + 1)

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

        if self.state in ("menu", "howto"):
            ui.draw_menu(
                screen,
                (self.font_title, self.font_small),
                self.menu_buttons,
                pygame.mouse.get_pos(),
                self.best_score,
            )
            if self.state == "howto":
                ui.draw_how_to(screen, (self.font_big, self.font_small), self.howto_buttons[0], pygame.mouse.get_pos())
        elif self.state == "win":
            self.draw_playfield()
            ui.draw_win(screen, (self.font_big, self.font_small), self.win_buttons, pygame.mouse.get_pos(), self.score)
        else:
            self.draw_playfield()
            if self.state == "paused":
                ui.draw_pause(screen, (self.font_big, self.font_small), self.pause_buttons, pygame.mouse.get_pos())
            elif self.state == "game_over":
                ui.draw_game_over(
                    screen,
                    (self.font_big, self.font_small),
                    self.game_over_buttons,
                    pygame.mouse.get_pos(),
                    self.score,
                    self.best_score,
                )
            elif self.state == "level_clear":
                ui.draw_level_clear(
                    screen,
                    (self.font_big, self.font_small),
                    self.level_clear_buttons,
                    pygame.mouse.get_pos(),
                    LEVELS[self.level_index].name,
                    0,
                )

        pygame.display.flip()

    def draw_playfield(self):
        for brick in self.bricks:
            if brick.alive:
                brick.draw(self.screen)
        self.paddle.draw(self.screen)
        for ball in self.balls:
            ball.draw(self.screen)
        self.draw_hud()

    def draw_hud(self):
        bar = pygame.Surface((WIDTH, HUD_HEIGHT), pygame.SRCALPHA)
        bar.fill((10, 14, 30, 200))
        self.screen.blit(bar, (0, 0))
        pygame.draw.line(self.screen, (40, 48, 76), (0, HUD_HEIGHT - 1), (WIDTH, HUD_HEIGHT - 1))

        score = self.font_tiny.render("SKOR", True, MUTED)
        score_value = self.font_medium.render(str(self.score), True, WHITE)
        self.screen.blit(score, (24, 5))
        self.screen.blit(score_value, (24, 20))

        level = LEVELS[self.level_index]
        name = self.font_small.render(f"LEVEL {self.level_index + 1} - {level.name.upper()}", True, NEON)
        self.screen.blit(name, (WIDTH // 2 - name.get_width() // 2, 15))

        lives_label = self.font_tiny.render("NYAWA", True, MUTED)
        self.screen.blit(lives_label, (WIDTH - 110, 5))
        for i in range(3):
            color = PINK if i < self.lives else (60, 66, 90)
            pygame.draw.circle(self.screen, color, (WIDTH - 34 - i * 22, 33), 6)
