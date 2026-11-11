"""Susunan bata untuk setiap level."""

from settings import ROW_COLORS, WIDTH


class Level:
    """Satu level berisi layout bata, warna, dan kecepatan bola."""

    def __init__(self, name, layout, palette=None, speed=430):
        self.name = name
        self.layout = layout
        self.palette = palette or ROW_COLORS
        self.speed = speed

    def build_bricks(self, brick_class):
        rows = len(self.layout)
        cols = max(len(row) for row in self.layout)
        margin = 70
        gap = 6
        top = 100
        brick_h = 26
        brick_w = (WIDTH - margin * 2 - gap * (cols - 1)) / cols

        bricks = []
        for row_index, row in enumerate(self.layout):
            for col_index, symbol in enumerate(row):
                if symbol == ".":
                    continue
                x = margin + col_index * (brick_w + gap)
                y = top + row_index * (brick_h + gap)
                color = self.palette[row_index % len(self.palette)]
                bricks.append(brick_class(x, y, brick_w, brick_h, color, 1, 10))
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
    ),
]
