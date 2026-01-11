import arcade

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Moving Sprite Example"

PLAYER_SPEED = 300.0

class MovingSpriteGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.ASH_GREY)

        self.player_sprite = arcade.Sprite(
            ":resources:images/space_shooter/playerShip1_green.png",
            scale=0.5
        )
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        self.player_sprite.center_x = SCREEN_WIDTH // 2
        self.player_sprite.center_y = SCREEN_HEIGHT // 2

        # set the Velocity vector components
        self.vx = 0.0
        self.vy = 0.0
    
    def on_draw(self):
        self.clear()

        self.player_list.draw()

        # skip the drawing of the demo line

        # debug text, velocity and position
        arcade.draw_text(
            f"Velocity: ({self.vx}, {self.vy}); Pos: ({self.player_sprite.center_x:.1f}, {self.player_sprite.center_y:.1f})",
            10, 10,
            arcade.color.BLUE,
            14
        )
    
    def on_update(self, delta_time):
        self.player_sprite.center_x += self.vx * delta_time
        self.player_sprite.center_y += self.vy * delta_time

        # we need to prevent the player from getting out
        # of our "world coordinate"
        self.player_sprite.center_x = arcade.math.clamp(
            self.player_sprite.center_x, 0, SCREEN_WIDTH
        )
        self.player_sprite.center_y = arcade.math.clamp(
            self.player_sprite.center_y, 0, SCREEN_HEIGHT
        )
    
    def on_key_press(self, sym, modifiers):
        if sym == arcade.key.LEFT:
            self.vx = -PLAYER_SPEED
        elif sym == arcade.key.RIGHT:
            self.vx = PLAYER_SPEED
        elif sym == arcade.key.UP:
            self.vy = PLAYER_SPEED
        elif sym == arcade.key.DOWN:
            self.vy = -PLAYER_SPEED
    
    def on_key_release(self, symbol, modifiers):
        if symbol == arcade.key.LEFT or symbol == arcade.key.RIGHT:
            self.vx = 0.0
        if symbol == arcade.key.UP or symbol == arcade.key.DOWN:
            self.vy = 0.0


if __name__ == "__main__":
    game = MovingSpriteGame()
    arcade.run()
