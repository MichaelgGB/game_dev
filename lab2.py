
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

        self.collision_count = 0
        self.previous_collisions = set() # to track collisions that we have already counted

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
        
        # Draw collision counter
        arcade.draw_text(
            f"Count: {self.collision_count}",
            WINDOW_WIDTH - 150, WINDOW_HEIGHT - 40,
            arcade.color.WHITE,
            24,
            bold=True
        )
        
        # TASK 2: Draw bounding boxes for colliding crates
        selected_crate = self.crate_list[self.selected_crate_index]
        
        # Check crate-to-crate collisions for selected crate
        for other_crate in self.crate_list:
            if other_crate != selected_crate:
                if arcade.check_for_collision(selected_crate, other_crate):
                    # Calculate overlap rectangle
                    overlap = self.get_overlap_rect(selected_crate, other_crate)
                    if overlap:
                        x, y, width, height = overlap
                        # Draw filled rectangle with border using arcade.draw_lrbt_rectangle_filled
                        left = x - width / 2
                        right = x + width / 2
                        bottom = y - height / 2
                        top = y + height / 2
                        
                        # Draw the outline using lines
                        arcade.draw_line(left, bottom, right, bottom, arcade.color.RED, 3)
                        arcade.draw_line(right, bottom, right, top, arcade.color.RED, 3)
                        arcade.draw_line(right, top, left, top, arcade.color.RED, 3)
                        arcade.draw_line(left, top, left, bottom, arcade.color.RED, 3)
        
        # Check selected crate to wall collisions
        wall_collisions = arcade.check_for_collision_with_list(
            selected_crate, self.wall_list
        )
        for wall in wall_collisions:
            overlap = self.get_overlap_rect(selected_crate, wall)
            if overlap:
                x, y, width, height = overlap
                left = x - width / 2
                right = x + width / 2
                bottom = y - height / 2
                top = y + height / 2
                
                # Draw the outline using lines
                arcade.draw_line(left, bottom, right, bottom, arcade.color.RED, 3)
                arcade.draw_line(right, bottom, right, top, arcade.color.RED, 3)
                arcade.draw_line(right, top, left, top, arcade.color.RED, 3)
                arcade.draw_line(left, top, left, bottom, arcade.color.RED, 3)
        
        # Draw yellow border around selected crate
        selected_crate.draw_hit_box(arcade.color.YELLOW, 4)
        
        # Draw player hitbox
        self.player_sprite.draw_hit_box(arcade.color.YELLOW, 2)

    def get_overlap_rect(self, sprite1, sprite2):
        """Calculate the overlapping rectangle between two sprites."""
        # Get boundaries of each sprite
        left1 = sprite1.left
        right1 = sprite1.right
        bottom1 = sprite1.bottom
        top1 = sprite1.top
        
        left2 = sprite2.left
        right2 = sprite2.right
        bottom2 = sprite2.bottom
        top2 = sprite2.top
        
        # Calculate overlap
        overlap_left = max(left1, left2)
        overlap_right = min(right1, right2)
        overlap_bottom = max(bottom1, bottom2)
        overlap_top = min(top1, top2)
        
        # Check if there is actual overlap
        if overlap_left < overlap_right and overlap_bottom < overlap_top:
            overlap_width = overlap_right - overlap_left
            overlap_height = overlap_top - overlap_bottom
            overlap_center_x = overlap_left + overlap_width / 2
            overlap_center_y = overlap_bottom + overlap_height / 2
            
            return (overlap_center_x, overlap_center_y, overlap_width, overlap_height)
        
        return None

    def on_update(self, delta_time):
        """Movement and Game Logic"""
        
        # Check for NEW collisions
        current_collisions = set()
        
        # Check crate-to-crate collisions
        for i, crate1 in enumerate(self.crate_list):
            for j, crate2 in enumerate(self.crate_list):
                if i < j:  # Only check each pair once
                    if arcade.check_for_collision(crate1, crate2):
                        collision_key = (i, j, 'crate')
                        current_collisions.add(collision_key)
                        if collision_key not in self.previous_collisions:
                            self.collision_count += 1
                            print(f"Count: {self.collision_count}")
        
        # Check crate-to-wall collisions
        for i, crate in enumerate(self.crate_list):
            wall_collisions = arcade.check_for_collision_with_list(crate, self.wall_list)
            for wall in wall_collisions:
                wall_index = self.wall_list.index(wall)
                collision_key = (i, wall_index, 'wall')
                current_collisions.add(collision_key)
                if collision_key not in self.previous_collisions:
                    self.collision_count += 1
                    print(f"Count: {self.collision_count}")
        
        # Update previous collisions for next frame
        self.previous_collisions = current_collisions
        
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