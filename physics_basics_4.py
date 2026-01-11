
"""
Platformer Game

In-class lab -- Dec 9. 2025
"""
import arcade

# Constants
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Platformer"

GRAVITY = 1
PLAYER_JUMP_SPEED = 20

# Constants used to scale our sprites from their original size
TILE_SCALING = 0.5

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 5


class GameView(arcade.Window):
    """
    Main application class.
    """

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
        for x in range(0, 1600, 64):
            wall = arcade.Sprite(":resources:images/tiles/grassMid.png", scale=TILE_SCALING)
            wall.center_x = x
            wall.center_y = 32
            # leave a gap
            if x < 512 or x > 640:
              self.wall_list.append(wall)
        

        # Put some crates on the ground
        # This shows using a coordinate list to place sprites
        coordinate_list = [[256, 96], 
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

        self.selected_crate_index = 0

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

        # BONUS: draw border around the selected crate
        assert(len(self.crate_list) > self.selected_crate_index)
        crate = self.crate_list[self.selected_crate_index]
        crate.draw_hit_box(arcade.color.YELLOW, 4)

        # draw guides around the sprites
        self.player_sprite.draw_hit_box(arcade.color.YELLOW, 2)
        # or get points
        #points = self.player_sprite.hit_box.get_adjusted_points()
        #arcade.draw_polygon_outline(points, arcade.color.YELLOW, 2)

    def on_update(self, delta_time):
        """Movement and Game Logic"""
        
        # without collision-detection for now
        # prevent the "selected" crate from going past the ground
        
        # if self.crate_list[self.selected_crate_index].center_y < 96:
        #     self.crate_list[self.selected_crate_index].center_y = 96
        #     self.crate_list[self.selected_crate_index].change_y = 0
        
        # check for collision
        # crate_coll = arcade.check_for_collision_with_list(
        #     self.crate_list[self.selected_crate_index],
        #     self.wall_list
        # )
        # print(crate_coll)
        
        
    
        # Move the player using our physics engine
        self.physics_engine.update()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

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
        
        # move crates
        selected_crate = self.crate_list[self.selected_crate_index]
        if key == arcade.key.M:
            # will pick crate next to the player, for now pick first crate
            selected_crate.change_x = 5
        elif key == arcade.key.N:
            selected_crate.change_x = -5
        elif key == arcade.key.J:
            selected_crate.change_y = 5
        elif key == arcade.key.K:
            selected_crate.change_y = -5
        
        elif key == arcade.key.SPACE:
            # stack a new create on top of the last one
            position = self.crate_list[-1].position
            position = list(position) # tuple is returned after gameplay
            position[1] += self.crate_list[0].height
            # cap it at 8 crates
            if len(self.crate_list) < 8:
              self.add_crate(position)
        
        # crate selection
        if arcade.key.KEY_0 <= key <= arcade.key.KEY_9:
            index = key - arcade.key.KEY_0
            if index < len(self.crate_list):
                self.selected_crate_index = index
            # print("Debug key:", arcade.key.KEY_0, key, self.selected_crate_index)

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
        
        # crate move
        selected_crate = self.crate_list[self.selected_crate_index]
        if key == arcade.key.M or key == arcade.key.N:
            selected_crate.change_x = 0
        if key == arcade.key.J or key == arcade.key.K:
            selected_crate.change_y = 0

def main():
    """Main function"""
    window = GameView()
    window.setup()
    arcade.run() # game loop // infinite

if __name__ == "__main__":
    main()