import arcade
import random

SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 640
SCREEN_TITLE = "Space War"

STAR_COUNT = 200

SPRITE_SIZE = 16
SPRITESHEET_PATH = "images/spritesheet.png"


class SpriteSheet:
    """Wraps arcade.SpriteSheet into a 2D grid of textures indexed by (row, col)."""

    def __init__(self, path: str, sprite_width: int, sprite_height: int, cols: int, rows: int):
        self.cols = cols
        self.rows = rows
        sheet = arcade.load_spritesheet(path)
        flat = sheet.get_texture_grid(
            size=(sprite_width, sprite_height),
            columns=cols,
            count=cols * rows,
        )
        self.textures = [flat[row * cols:(row + 1) * cols] for row in range(rows)]

    def get(self, row: int, col: int) -> arcade.Texture:
        return self.textures[row][col]


PLAYER_SPEED = 250
SPRITE_SCALE = 2


class Player(arcade.Sprite):
    def __init__(self):
        super().__init__("images/purple.png", scale=SPRITE_SCALE)
        self.center_x = SCREEN_WIDTH / 2
        self.center_y = 48

    def draw(self, **kwargs):
        super().draw(**kwargs)

    def update(self, delta_time: float = 1/60):
        self.center_x += self.change_x * delta_time
        self.center_x = max(self.width / 2, min(SCREEN_WIDTH - self.width / 2, self.center_x))


class Enemy(arcade.Sprite):
    def __init__(self, spritesheet: SpriteSheet):
        row = random.randrange(spritesheet.rows)
        col = random.randrange(spritesheet.cols)
        texture = spritesheet.get(row, col)
        super().__init__(texture, scale=SPRITE_SCALE)
        self.center_x = random.randrange(SPRITE_SIZE, SCREEN_WIDTH - SPRITE_SIZE)
        self.center_y = SCREEN_HEIGHT + SPRITE_SIZE
        self.speed = random.randint(20, 100)

    def draw(self, **kwargs):
        super().draw(**kwargs)

    def update(self, delta_time: float = 1/60):
        self.center_y -= self.speed * delta_time


SHOT_SPEED = 400
SHOT_ANIM_FPS = 8


class Shot(arcade.Sprite):
    def __init__(self, spritesheet: SpriteSheet, x: float, y: float):
        super().__init__(spritesheet.get(0, 0), scale=SPRITE_SCALE)
        self.textures = [spritesheet.get(0, 0), spritesheet.get(0, 1)]
        self.center_x = x
        self.center_y = y
        self._frame_timer = 0.0
        self._frame_index = 0

    def update(self, delta_time: float = 1/60):
        self.center_y += SHOT_SPEED * delta_time
        self._frame_timer += delta_time
        if self._frame_timer >= 1 / SHOT_ANIM_FPS:
            self._frame_timer = 0.0
            self._frame_index = 1 - self._frame_index
            self.texture = self.textures[self._frame_index]


EXPLOSION_FPS = 12


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


PLANET_IMAGES = [f"images/planet_{i}.png" for i in range(1, 7)]


class Planet(arcade.Sprite):
    def __init__(self):
        super().__init__(random.choice(PLANET_IMAGES))
        self.center_x = int(random.randrange(int(self.width), SCREEN_WIDTH - int(self.width)))
        self.center_y = SCREEN_HEIGHT + self.height
        self.speed = random.uniform(10, 30)

    def update(self, delta_time: float = 1/60):
        self.center_y -= self.speed * delta_time


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


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.stars = [Star(randomize_y=True) for _ in range(STAR_COUNT)]
        self.spritesheet = SpriteSheet(SPRITESHEET_PATH, SPRITE_SIZE, SPRITE_SIZE, cols=32, rows=32)
        self.shot_spritesheet = SpriteSheet("images/shot.png", SPRITE_SIZE, SPRITE_SIZE, cols=2, rows=1)
        self.player_list = arcade.SpriteList()
        self.player = Player()
        self.player_list.append(self.player)
        self.enemy_list = arcade.SpriteList()
        self.enemy_list.append(Enemy(self.spritesheet))
        self.shot_list = arcade.SpriteList()
        self.explosion_spritesheet = SpriteSheet("images/Space Ships Explosion.png", 48, 48, cols=7, rows=1)
        self.explosion_list = arcade.SpriteList()
        self.planet_list = arcade.SpriteList()
        for _ in range(3):
            self.planet_list.append(Planet())
        self.score = 0
        self.lives = 10
        self.game_over = False

    def _restart(self):
        self.score = 0
        self.lives = 10
        self.game_over = False
        self.player.center_x = SCREEN_WIDTH / 2
        self.player.change_x = 0
        self.enemy_list.clear()
        self.enemy_list.append(Enemy(self.spritesheet))
        self.shot_list.clear()
        self.explosion_list.clear()

    def on_draw(self):
        self.clear()
        for star in self.stars:
            star.draw()
        self.planet_list.draw()
        self.enemy_list.draw()
        self.shot_list.draw()
        self.explosion_list.draw()
        self.player_list.draw()
        arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 30,
                         arcade.color.YELLOW, 20, bold=True)
        arcade.draw_text(f"Lives: {self.lives}", 200, SCREEN_HEIGHT - 30,
                         arcade.color.CYAN, 20, bold=True)
        if self.game_over:
            arcade.draw_text("GAME OVER", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30,
                             arcade.color.RED, 60, bold=True, anchor_x="center")
            arcade.draw_text("Press SPACE to play again", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 30,
                             arcade.color.WHITE, 24, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if self.game_over:
            if key == arcade.key.SPACE:
                self._restart()
            return
        if key == arcade.key.LEFT:
            self.player.change_x = -PLAYER_SPEED
        elif key == arcade.key.RIGHT:
            self.player.change_x = PLAYER_SPEED
        elif key == arcade.key.SPACE:
            shot = Shot(self.shot_spritesheet, self.player.center_x, self.player.top)
            self.shot_list.append(shot)

    def on_key_release(self, key, modifiers):
        if key in (arcade.key.LEFT, arcade.key.RIGHT):
            self.player.change_x = 0

    def on_update(self, delta_time):
        for star in self.stars:
            star.update(delta_time)
        for planet in list(self.planet_list):
            planet.update(delta_time)
            if planet.center_y < -planet.height:
                planet.remove_from_sprite_lists()
                self.planet_list.append(Planet())
        if self.game_over:
            return
        for explosion in list(self.explosion_list):
            explosion.update(delta_time)
        self.player.update(delta_time)
        if arcade.check_for_collision_with_list(self.player, self.planet_list):
            self.game_over = True
            return
        for enemy in list(self.enemy_list):
            enemy.update(delta_time)
            if enemy.center_y < -SPRITE_SIZE or arcade.check_for_collision(enemy, self.player):
                self.explosion_list.append(Explosion(self.explosion_spritesheet, enemy.center_x, enemy.center_y))
                enemy.remove_from_sprite_lists()
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                    return
        if len(self.enemy_list) == 0:
            for _ in range(random.randint(2, 5)):
                self.enemy_list.append(Enemy(self.spritesheet))
        for shot in list(self.shot_list):
            shot.update(delta_time)
            if shot.center_y > SCREEN_HEIGHT + SPRITE_SIZE:
                shot.remove_from_sprite_lists()
                continue
            hit_list = arcade.check_for_collision_with_list(shot, self.enemy_list)
            if hit_list:
                shot.remove_from_sprite_lists()
                for enemy in hit_list:
                    self.explosion_list.append(Explosion(self.explosion_spritesheet, enemy.center_x, enemy.center_y))
                    enemy.remove_from_sprite_lists()
                    self.score += 1


def main():
    GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()
