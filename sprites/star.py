import random
import arcade
from constants import SCREEN_WIDTH, SCREEN_HEIGHT


class Star:
    def __init__(self, randomize_y=True):
        self.x = 0
        self.y = 0
        self.layer = 0
        self.speed = 0.0
        self.radius = 0.0
        self.brightness = 0
        self.reset(randomize_y)

    def reset(self, randomize_y=False):
        self.x = random.randrange(0, SCREEN_WIDTH)
        self.y = random.randrange(0, SCREEN_HEIGHT) if randomize_y else SCREEN_HEIGHT
        # Three layers: slow/dim, medium, fast/bright
        self.layer = random.choices([0, 1, 2], weights=[50, 35, 15])[0]
        self.speed = [0.5, 1.5, 3.5][self.layer]
        self.radius = [1, 1.5, 2.5][self.layer]
        self.brightness = [120, 180, 255][self.layer]

    def update(self, delta_time):
        self.y -= self.speed * 60 * delta_time
        if self.y < 0:
            self.reset()

    def draw(self):
        color = (self.brightness, self.brightness, self.brightness)
        arcade.draw_circle_filled(self.x, self.y, self.radius, color)
