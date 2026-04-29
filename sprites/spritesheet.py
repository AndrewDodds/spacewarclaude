import arcade


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
