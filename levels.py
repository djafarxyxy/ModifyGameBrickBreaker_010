"""Susunan bata untuk setiap level."""

from entities import BombBrick, NormalBrick, SteelBrick, StrongBrick
from settings import ROW_COLORS, WIDTH

BRICK_TYPES = {
    "1": NormalBrick,
    "2": StrongBrick,
    "3": SteelBrick,
    "4": BombBrick,
}


class Level:
    """Satu level berisi layout bata, warna, dan kecepatan bola."""

    def __init__(self, name, layout, palette=None, speed=430):
        self.name = name
        self.layout = layout
        self.palette = palette or ROW_COLORS
        self.speed = speed

    def build_bricks(self):
        cols = max(len(row) for row in self.layout)
        margin = 70
        gap = 6
        top = 100
        brick_h = 26
        brick_w = (WIDTH - margin * 2 - gap * (cols - 1)) / cols

        bricks = []
        for row_index, row in enumerate(self.layout):
            for col_index, symbol in enumerate(row):
                brick_class = BRICK_TYPES.get(symbol)
                if brick_class is None:
                    continue
                x = margin + col_index * (brick_w + gap)
                y = top + row_index * (brick_h + gap)
                color = self.palette[row_index % len(self.palette)]
                bricks.append(brick_class(x, y, brick_w, brick_h, color))
        return bricks


LEVELS = [
    Level(
        "Pemanasan",
        [
            "............",
            "111111111111",
            "111111111111",
            "111111111111",
            "............",
            "111111111111",
            "111111111111",
        ],
        speed=430,
    ),
    Level(
        "Benteng",
        [
            "..22222222..",
            "..21111112..",
            "..21133112..",
            "..21111112..",
            "..22222222..",
            "....1111....",
        ],
        speed=455,
    ),
    Level(
        "Zigzag",
        [
            "11..22..33..",
            ".11..22..33.",
            "..11..22..33",
            "33..22..11..",
            ".33..22..11.",
            "..33..22..11",
        ],
        speed=480,
    ),
    Level(
        "Kacau",
        [
            "4.2.3.2.4.2.",
            ".2.4.2.3.4.2",
            "3.2.4.2.2.4.",
            ".4.3.2.4.3.2",
            "2.4.2.3.2.4.",
            "4.2.3.2.4.2.",
        ],
        speed=510,
    ),
]
