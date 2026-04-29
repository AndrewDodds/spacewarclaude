import arcade
from constants import SPRITE_SCALE, EXPLOSION_FPS
from .spritesheet import SpriteSheet


class Explosion(arcade.Sprite):
    def __init__(self, spritesheet: SpriteSheet, x: float, y: float):
        super().__init__(spritesheet.get(0, 0), scale=SPRITE_SCALE)
        self.textures = spritesheet.textures[0]
        self.center_x = x
        self.center_y = y
        self._frame_timer = 0.0
        self._frame_index = 0

    def update(self, delta_time: float = 1 / 60):
        self._frame_timer += delta_time
        if self._frame_timer >= 1 / EXPLOSION_FPS:
            self._frame_timer = 0.0
            self._frame_index += 1
            if self._frame_index >= len(self.textures):
                self.remove_from_sprite_lists()
                return
            self.texture = self.textures[self._frame_index]
