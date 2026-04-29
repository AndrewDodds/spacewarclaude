import random
import arcade
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE,
    STAR_COUNT, SPRITE_SIZE, SPRITESHEET_PATH, PLAYER_SPEED,
)
from sprites import SpriteSheet, Player, Enemy, Shot, Explosion, Planet, Star


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.stars = [Star(randomize_y=True) for _ in range(STAR_COUNT)]
        self.spritesheet = SpriteSheet(SPRITESHEET_PATH, SPRITE_SIZE*2, SPRITE_SIZE*2, cols=16, rows=16)
        self.shot_spritesheet = SpriteSheet("images/shot.png", SPRITE_SIZE, SPRITE_SIZE, cols=2, rows=1)
        self.explosion_spritesheet = SpriteSheet("images/Space Ships Explosion.png", 48, 48, cols=7, rows=1)
        self.player_list = arcade.SpriteList()
        self.player = Player()
        self.player_list.append(self.player)
        self.enemy_list = arcade.SpriteList()
        self.enemy_list.append(Enemy(self.spritesheet))
        self.shot_list = arcade.SpriteList()
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
