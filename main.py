import json
import random
import arcade
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE,
    STAR_COUNT, SPRITE_SIZE, SPRITESHEET_PATH, PLAYER_SPEED,
)
from sprites import SpriteSheet, Player, Enemy, Shot, Missile, Explosion, Planet, Powerup, Star

with open("levels.json") as f:
    LEVELS = json.load(f)["levels"]


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.BLACK)
        self.stars = [Star(randomize_y=True) for _ in range(STAR_COUNT)]
        self.spritesheet = SpriteSheet(SPRITESHEET_PATH, SPRITE_SIZE * 2, SPRITE_SIZE * 2, cols=16, rows=16)
        self.shot_spritesheet = SpriteSheet("images/shot.png", SPRITE_SIZE, SPRITE_SIZE, cols=2, rows=1)
        self.missile_spritesheet = SpriteSheet("images/missile.png", 48, 48, cols=2, rows=1)
        self.explosion_spritesheet = SpriteSheet("images/Space Ships Explosion.png", 48, 48, cols=7, rows=1)
        self.player_list = arcade.SpriteList()
        self.player = Player()
        self.player_list.append(self.player)
        self.enemy_list = arcade.SpriteList()
        self.shot_list = arcade.SpriteList()
        self.missile_list = arcade.SpriteList()
        self.explosion_list = arcade.SpriteList()
        self.powerup_list = arcade.SpriteList()
        self.planet_list = arcade.SpriteList()
        self.score = 0
        self.lives = 10
        self.missiles_remaining = 3
        self.game_over = False
        self.you_win = False
        self.level_index = 0
        self.kills_this_level = 0
        self._apply_level()

    def _level(self) -> dict:
        return LEVELS[self.level_index]

    def _max_enemies(self) -> int:
        return int(self._level()["max_enemies"])

    def _kills_to_advance(self) -> int:
        return self._max_enemies() * 3

    def _planet_max_speed(self) -> float:
        return float(self._level()["planet_max_speed"])

    def _maybe_spawn_powerup(self, x: float, y: float):
        if random.random() < 0.25:
            kind = random.choice(["missile", "health"])
            self.powerup_list.append(Powerup(kind, x, y))

    def _new_planet(self) -> Planet:
        return Planet(max_speed=self._planet_max_speed())

    def _apply_level(self):
        self.planet_list.clear()
        for _ in range(int(self._level()["num_planets"])):
            self.planet_list.append(self._new_planet())
        self.enemy_list.clear()
        self.enemy_list.append(Enemy(self.spritesheet))

    def _advance_level(self):
        self.level_index += 1
        if self.level_index >= len(LEVELS):
            self.game_over = True
            self.you_win = True
            self.level_index = 0
            return
        self.kills_this_level = 0
        self.shot_list.clear()
        self.missile_list.clear()
        self.explosion_list.clear()
        self.powerup_list.clear()
        self._apply_level()

    def _restart(self):
        self.score = 0
        self.lives = 10
        self.game_over = False
        self.you_win = False
        self.level_index = 0
        self.kills_this_level = 0
        self.missiles_remaining = 3
        self.player.center_x = SCREEN_WIDTH / 2
        self.player.change_x = 0
        self.shot_list.clear()
        self.missile_list.clear()
        self.explosion_list.clear()
        self.powerup_list.clear()
        self._apply_level()

    def on_draw(self):
        self.clear()
        for star in self.stars:
            star.draw()
        self.planet_list.draw()
        self.powerup_list.draw()
        self.enemy_list.draw()
        self.shot_list.draw()
        self.missile_list.draw()
        self.explosion_list.draw()
        self.player_list.draw()
        arcade.draw_text(f"Score: {self.score}", 10, SCREEN_HEIGHT - 30,
                         arcade.color.YELLOW, 20, bold=True)
        arcade.draw_text(f"Lives: {self.lives}", 200, SCREEN_HEIGHT - 30,
                         arcade.color.CYAN, 20, bold=True)
        arcade.draw_text(f"Missiles: {self.missiles_remaining}", 380, SCREEN_HEIGHT - 30,
                         arcade.color.LIGHT_GREEN, 20, bold=True)
        arcade.draw_text(self._level()["name"], 560, SCREEN_HEIGHT - 30,
                         arcade.color.WHITE, 20, bold=True)
        kills_left = self._kills_to_advance() - self.kills_this_level
        arcade.draw_text(f"Kills: {kills_left}", SCREEN_WIDTH - 10, SCREEN_HEIGHT - 30,
                         arcade.color.ORANGE, 20, bold=True, anchor_x="right")
        if self.game_over:
            if self.you_win:
                arcade.draw_text("YOU WIN!", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30,
                                 arcade.color.GOLD, 60, bold=True, anchor_x="center")
            else:
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
        elif key == arcade.key.LSHIFT:
            if self.missiles_remaining > 0:
                missile = Missile(self.missile_spritesheet, self.player.center_x, self.player.top)
                self.missile_list.append(missile)
                self.missiles_remaining -= 1

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
                self.planet_list.append(self._new_planet())
        if self.game_over:
            return
        for explosion in list(self.explosion_list):
            explosion.update(delta_time)
        for powerup in list(self.powerup_list):
            powerup.update(delta_time)
            if powerup.center_y < -powerup.height:
                powerup.remove_from_sprite_lists()
            elif arcade.check_for_collision(powerup, self.player):
                powerup.remove_from_sprite_lists()
                if powerup.kind == "missile":
                    self.missiles_remaining += 1
                elif powerup.kind == "health":
                    self.lives += 1
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
            count = random.randint(2, self._max_enemies())
            for _ in range(count):
                self.enemy_list.append(Enemy(self.spritesheet))
        for missile in list(self.missile_list):
            missile.update(delta_time)
            if missile.center_y > SCREEN_HEIGHT + SPRITE_SIZE:
                missile.remove_from_sprite_lists()
                continue
            hit_planets = arcade.check_for_collision_with_list(missile, self.planet_list)
            if hit_planets:
                missile.remove_from_sprite_lists()
                for planet in hit_planets:
                    self.explosion_list.append(Explosion(self.explosion_spritesheet, planet.center_x, planet.center_y))
                    planet.remove_from_sprite_lists()
                continue
            hit_list = arcade.check_for_collision_with_list(missile, self.enemy_list)
            if hit_list:
                missile.remove_from_sprite_lists()
                for enemy in hit_list:
                    self.explosion_list.append(Explosion(self.explosion_spritesheet, enemy.center_x, enemy.center_y))
                    self._maybe_spawn_powerup(enemy.center_x, enemy.center_y)
                    enemy.remove_from_sprite_lists()
                    self.score += 1
                    self.kills_this_level += 1
                    if self.kills_this_level >= self._kills_to_advance():
                        self._advance_level()
                        return
        for shot in list(self.shot_list):
            shot.update(delta_time)
            if shot.center_y > SCREEN_HEIGHT + SPRITE_SIZE:
                shot.remove_from_sprite_lists()
                continue
            if arcade.check_for_collision_with_list(shot, self.planet_list):
                shot.remove_from_sprite_lists()
                continue
            hit_list = arcade.check_for_collision_with_list(shot, self.enemy_list)
            if hit_list:
                shot.remove_from_sprite_lists()
                for enemy in hit_list:
                    self.explosion_list.append(Explosion(self.explosion_spritesheet, enemy.center_x, enemy.center_y))
                    self._maybe_spawn_powerup(enemy.center_x, enemy.center_y)
                    enemy.remove_from_sprite_lists()
                    self.score += 1
                    self.kills_this_level += 1
                    if self.kills_this_level >= self._kills_to_advance():
                        self._advance_level()
                        return


def main():
    GameWindow()
    arcade.run()


if __name__ == "__main__":
    main()
