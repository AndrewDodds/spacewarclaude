import random
import arcade
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, PLANET_IMAGES


class Planet(arcade.Sprite):
    def __init__(self, max_speed: float = 30):
        super().__init__(random.choice(PLANET_IMAGES))
        self.center_x = int(random.randrange(int(self.width), SCREEN_WIDTH - int(self.width)))
        self.center_y = SCREEN_HEIGHT + self.height
        self.speed = random.uniform(10, max_speed)

    def update(self, delta_time: float = 1 / 60):
        self.center_y -= self.speed * delta_time
