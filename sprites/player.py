import arcade
from constants import SCREEN_WIDTH, SPRITE_SCALE, PLAYER_SPEED


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__("images/purple.png", scale=SPRITE_SCALE)
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = 48

    def update(self, delta_time: float = 1 / 60):
        self.center_x += self.change_x * delta_time
        self.center_x = max(self.width / 2, min(SCREEN_WIDTH - self.width / 2, self.center_x))
