import arcade
from constants import SCREEN_HEIGHT, SPRITE_SCALE

POWERUP_IMAGES = {
    "missile": "images/Item_1.png",
    "health": "images/item_2.png",
}
POWERUP_SPEED = 80


class Powerup(arcade.Sprite):
    def __init__(self, kind: str, x: float, y: float):
        super().__init__(POWERUP_IMAGES[kind], scale=SPRITE_SCALE)
        self.kind = kind
        self.center_x = x
        self.center_y = y

    def update(self, delta_time: float = 1 / 60):
        self.center_y -= POWERUP_SPEED * delta_time
