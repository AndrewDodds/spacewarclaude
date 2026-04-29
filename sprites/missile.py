import arcade
from constants import SPRITE_SCALE
from .spritesheet import SpriteSheet

MISSILE_SPEED = 350
MISSILE_ANIM_FPS = 10


class Missile(arcade.Sprite):
    def __init__(self, spritesheet: SpriteSheet, x: float, y: float):
        super().__init__(spritesheet.get(0, 0), scale=SPRITE_SCALE)
        self.textures = spritesheet.textures[0]
        self.center_x = x
        self.center_y = y
        self._frame_timer = 0.0
        self._frame_index = 0

    def update(self, delta_time: float = 1 / 60):
        self.center_y += MISSILE_SPEED * delta_time
        self._frame_timer += delta_time
        if self._frame_timer >= 1 / MISSILE_ANIM_FPS:
            self._frame_timer = 0.0
            self._frame_index = 1 - self._frame_index
            self.texture = self.textures[self._frame_index]
