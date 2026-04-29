import random
import arcade
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, SPRITE_SIZE, SPRITE_SCALE
from .spritesheet import SpriteSheet


class Enemy(arcade.Sprite):
    def __init__(self, spritesheet: SpriteSheet):
        row = random.randrange(spritesheet.rows)
        col = random.randrange(spritesheet.cols)
        super().__init__(spritesheet.get(row, col), scale=SPRITE_SCALE)
        self.center_x = random.randrange(SPRITE_SIZE, SCREEN_WIDTH - SPRITE_SIZE)
        self.center_y = SCREEN_HEIGHT + SPRITE_SIZE
        self.speed = random.randint(20, 100)

    def update(self, delta_time: float = 1 / 60):
        self.center_y -= self.speed * delta_time
