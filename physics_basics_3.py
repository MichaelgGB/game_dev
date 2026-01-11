
"""
Platformer Game

In-class lab for Dec 9, 2025.
"""
import arcade

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Platformer"

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5
GRAVITY = 1
PLAYER_JUMP_SPEED = 20
CRATE_MOVEMENT_SPEED = 5

# Constants used to scale our sprites from their original size
TILE_SCALING = 0.5


class GameView(arcade.Window):
    """
    Main application class.
    """

    # helper function
    def add_crate(self, position):
        crate = arcade.Sprite(
                ":resources:images/tiles/boxCrate_double.png", scale=TILE_SCALING
            )
        crate.position = position
        self.crate_list.append(crate)
    
    def __init__(self):

        # Call the parent class and set up the window
        super().__init__(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)

        # Variable to hold our texture for our player
        self.player_texture = arcade.load_texture(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png"
        )

        # Separate variable that holds the player sprite
        self.player_sprite = arcade.Sprite(self.player_texture)
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 128

        # SpriteList for our player
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player_sprite)

        # SpriteList for our boxes and ground
        # Putting our ground and box Sprites in the same SpriteList
        # will make it easier to perform collision detection against
        # them later on. Setting the spatial hash to True will make
        # collision detection much faster if the objects in this
        # SpriteList do not move.
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)

        ## Explore platforms vs. walls
        self.crate_list = arcade.SpriteList()

        # Create the ground
        # This shows using a loop to place multiple sprites horizontally
        for x in range(0, 1250, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            if x < 512 or x > 640:
                self.wall_list.append(wall)

        # Put some crates on the ground
        # This shows using a coordinate list to place sprites
        coordinate_list = [
            [256, 96], # work with one crate for now
            # [512, 96], [768, 96]
        ]

        for coordinate in coordinate_list:
            # Add a crate on the ground
            self.add_crate(coordinate)

        
        self.background_color = arcade.csscolor.CORNFLOWER_BLUE

        # Use Platformer Physics Engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.wall_list,
            platforms=self.crate_list,
            gravity_constant=GRAVITY
        )

    def setup(self):
        """Set up the game here. Call this function to restart the game."""
        pass

    def on_draw(self):
        """Render the screen."""

        # Clear the screen to the background color
        self.clear()

        # Draw our sprites
        self.wall_list.draw()
        self.crate_list.draw()
        self.player_list.draw()

    def on_update(self, delta_time):
        """Movement and Game Logic"""

        # Move the player using our physics engine
        self.physics_engine.update()

   

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        # player movement
        if key == arcade.key.UP or key == arcade.key.W:
            speed = PLAYER_MOVEMENT_SPEED
            if self.physics_engine.can_jump():
                speed = PLAYER_JUMP_SPEED
            self.player_sprite.change_y = speed
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        
        # move the crates
        # M --> right, N --> left
        selected_crate = self.crate_list[0]
        if key == arcade.key.M:
            selected_crate.change_x = CRATE_MOVEMENT_SPEED
        elif key == arcade.key.N:
            selected_crate.change_x = -CRATE_MOVEMENT_SPEED
        elif key == arcade.key.SPACE:
            position = self.crate_list[-1].position # tuple
            position = list(position) # (3, 5) -> [3, 5] # x, y
            position[1] += self.crate_list[-1].height
            # TODO: cap the number of crates to be added to 8
            self.add_crate(position)


    def on_key_release(self, key, modifiers):
        """Called whenever a key is released."""

        if key == arcade.key.UP or key == arcade.key.W:
            self.player_sprite.change_y = 0
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.player_sprite.change_y = 0
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.player_sprite.change_x = 0
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.player_sprite.change_x = 0

        # crate movement
        selected_crate = self.crate_list[0]
        if key == arcade.key.M or key == arcade.key.N:
            selected_crate.change_x = 0


def main():
    """Main function"""
    window = GameView()
    window.setup()
    arcade.run() # game loop // infinite

if __name__ == "__main__":
    main()


'''
TODO's:

(1) Limit the crates to be added during game play to 8 max
(2) Add logic to move the selected crate up (press "J") and down (press "K")
(3) Add logic that selects the crate to move
    currently, selected_crate = crate_list[0]
    pay attention to out-of-bound errors e.g.
        - if we have 3 crates, pressing 3 is not valid
            since there's no crate_list[3] 
(4) Bounds:
    i. the player should not get out of the screen boundary
    ii. when moving down, the crate shouldn't go past the grass
        hint: selected_crate.center_y >= 96
(5) Bonus: make the crate movement while on the ground (grass)
    to be a little slower, mimicking friction.
(6) Bonus: when selecting a crate, you can add "glowing" yellow border
    around the crate.
'''