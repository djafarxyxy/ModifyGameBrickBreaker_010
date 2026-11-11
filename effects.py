"""Efek visual dan suara, semuanya dibuat dari kode tanpa file aset."""

import array
import io
import math
import random
import wave

import pygame

from settings import HEIGHT, WIDTH


class Particle:
    def __init__(self, x, y, color, speed_scale=1.0):
        self.x = float(x)
        self.y = float(y)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(40, 190) * speed_scale
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed - random.uniform(20, 90)
        self.color = color
        self.life = random.uniform(0.45, 0.95)
        self.max_life = self.life
        self.size = random.uniform(1.6, 3.6)

    def update(self, dt):
        self.life -= dt
        self.vel_y += 620 * dt
        self.vel_x *= 1 - 1.8 * dt
        self.x += self.vel_x * dt
        self.y += self.vel_y * dt
        return self.life > 0

    def draw(self, surface):
        ratio = max(0.0, self.life / self.max_life)
        color = tuple(int(c * (0.35 + 0.65 * ratio)) for c in self.color)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), max(1, int(self.size * ratio + 0.5)))


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def burst(self, x, y, color, count=12, power=1.0):
        for _ in range(count):
            self.particles.append(Particle(x, y, color, power))

    def update(self, dt):
        self.particles = [particle for particle in self.particles if particle.update(dt)]

    def draw(self, surface):
        for particle in self.particles:
            particle.draw(surface)


class Starfield:
    """Latar bintang yang bergerak pelan ke bawah."""

    def __init__(self, count=90):
        self.stars = []
        for _ in range(count):
            self.stars.append(
                {
                    "x": random.uniform(0, WIDTH),
                    "y": random.uniform(0, HEIGHT),
                    "speed": random.uniform(4, 22),
                    "size": random.choice([1, 1, 1, 2, 2, 3]),
                    "phase": random.uniform(0, math.tau),
                }
            )
        self.time = 0.0

    def update(self, dt):
        self.time += dt
        for star in self.stars:
            star["y"] += star["speed"] * dt
            if star["y"] > HEIGHT:
                star["y"] = -2
                star["x"] = random.uniform(0, WIDTH)

    def draw(self, surface):
        for star in self.stars:
            glow = 0.55 + 0.45 * math.sin(self.time * 1.6 + star["phase"])
            value = int(110 + 120 * glow)
            color = (value, value, min(255, value + 30))
            pygame.draw.circle(surface, color, (int(star["x"]), int(star["y"])), star["size"])


def make_tone(freq_start, freq_end, duration, volume=0.22, wave_type="sine", sample_rate=44100):
    """Bikin nada pendek langsung di memori, lalu jadi pygame Sound."""
    frames = int(sample_rate * duration)
    samples = array.array("h")
    for i in range(frames):
        progress = i / frames
        freq = freq_start + (freq_end - freq_start) * progress
        value = math.sin(2 * math.pi * freq * (i / sample_rate))
        if wave_type == "square":
            value = 1.0 if value >= 0 else -1.0
        elif wave_type == "triangle":
            value = 2 / math.pi * math.asin(value)
        envelope = min(1.0, i / (sample_rate * 0.008)) * (1.0 - progress) ** 1.5
        samples.append(int(max(-1.0, min(1.0, value)) * volume * 32767 * envelope))

    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(sample_rate)
        file.writeframes(samples.tobytes())
    buffer.seek(0)
    return pygame.mixer.Sound(file=buffer)


class SoundBank:
    """Kumpulan efek suara, dibikin sendiri pakai gelombang sinus."""

    def __init__(self):
        self.enabled = True
        self.sounds = {}
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 1, 512)
            self.sounds = {
                "paddle": make_tone(300, 220, 0.07, 0.28),
                "brick": make_tone(680, 900, 0.06, 0.22),
                "steel": make_tone(160, 130, 0.06, 0.20, "square"),
                "bomb": make_tone(180, 45, 0.32, 0.35, "square"),
                "powerup": make_tone(620, 1020, 0.16, 0.25, "triangle"),
                "life": make_tone(520, 880, 0.22, 0.25),
                "laser": make_tone(1000, 620, 0.05, 0.16, "square"),
                "lose": make_tone(400, 140, 0.3, 0.28),
                "level": make_tone(440, 880, 0.35, 0.25, "triangle"),
                "gameover": make_tone(330, 80, 0.6, 0.3),
                "win": make_tone(520, 1040, 0.5, 0.28, "triangle"),
            }
        except Exception:
            self.enabled = False
            self.sounds = {}

    def play(self, name):
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()
