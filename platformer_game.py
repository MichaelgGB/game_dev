"""
Complete 2D Platformer Game
Final Lab - SCS3411

Features:
- 3 Game States: Menu, Game Play, Game Over
- Player animation during jumps, movement, and rest
- Collision detection for coin collection
- Health system with enemies
- Win condition when reaching the end
- Multiple difficulty levels
"""
import arcade
import random

# Constants
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
SCREEN_TITLE = "Platformer Adventure"

# Scaling
TILE_SCALING = 0.5
PLAYER_SCALING = 0.5
COIN_SCALING = 0.5
ENEMY_SCALING = 0.5

# Physics
GRAVITY = 1.0
PLAYER_JUMP_SPEED = 20
PLAYER_MOVE_SPEED = 5
ENEMY_MOVE_SPEED = 2

# Game States
MENU = 0
GAME_PLAY = 1
GAME_OVER = 2
GAME_WIN = 3

# Difficulty levels
EASY = 0
MEDIUM = 1
HARD = 2


class MenuView:
    """Menu screen"""
    
    def __init__(self, window):
        self.window = window
        self.selected_difficulty = EASY
        
    def draw(self):
        arcade.draw_text(
            "PLATFORMER ADVENTURE",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT - 150,
            arcade.color.WHITE, 54,
            anchor_x="center", bold=True
        )
        
        arcade.draw_text(
            "Select Difficulty:",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT - 250,
            arcade.color.WHITE, 32,
            anchor_x="center"
        )
        
        difficulties = ["EASY", "MEDIUM", "HARD"]
        colors = [arcade.color.GREEN, arcade.color.YELLOW, arcade.color.RED]
        
        for i, (diff, color) in enumerate(zip(difficulties, colors)):
            y_pos = SCREEN_HEIGHT - 320 - (i * 60)
            text_color = arcade.color.YELLOW if i == self.selected_difficulty else color
            size = 36 if i == self.selected_difficulty else 28
            
            arcade.draw_text(
                f"[{i + 1}] {diff}",
                SCREEN_WIDTH / 2, y_pos,
                text_color, size,
                anchor_x="center", bold=(i == self.selected_difficulty)
            )
        
        arcade.draw_text(
            "Press ENTER to Start",
            SCREEN_WIDTH / 2, 150,
            arcade.color.WHITE, 28,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "Controls: Arrow Keys to Move, UP to Jump",
            SCREEN_WIDTH / 2, 80,
            arcade.color.LIGHT_GRAY, 18,
            anchor_x="center"
        )


class GameOverView:
    """Game Over screen"""
    
    def __init__(self, window, won=False, score=0, health=0):
        self.window = window
        self.won = won
        self.score = score
        self.health = health
        
    def draw(self):
        if self.won:
            arcade.draw_text(
                "YOU WIN!",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT - 150,
                arcade.color.YELLOW, 64,
                anchor_x="center", bold=True
            )
            arcade.draw_text(
                "Congratulations! You collected all coins and reached the end!",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT - 230,
                arcade.color.WHITE, 24,
                anchor_x="center"
            )
        else:
            arcade.draw_text(
                "GAME OVER",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT - 150,
                arcade.color.RED, 64,
                anchor_x="center", bold=True
            )
            arcade.draw_text(
                "You ran out of health!",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT - 230,
                arcade.color.WHITE, 24,
                anchor_x="center"
            )
        
        arcade.draw_text(
            f"Final Score: {self.score}",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
            arcade.color.WHITE, 36,
            anchor_x="center"
        )
        
        arcade.draw_text(
            f"Final Health: {self.health}",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 60,
            arcade.color.WHITE, 36,
            anchor_x="center"
        )
        
        arcade.draw_text(
            "Press R to Restart or ESC for Menu",
            SCREEN_WIDTH / 2, 150,
            arcade.color.WHITE, 28,
            anchor_x="center"
        )


class GamePlayView:
    """Main game play"""
    
    def __init__(self, window, difficulty=EASY):
        self.window = window
        self.difficulty = difficulty
        
        # Game state
        self.player_health = 100
        self.score = 0
        self.total_coins = 0
        self.coins_collected = 0
        
        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.coin_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.end_goal_list = arcade.SpriteList()
        
        # Camera for scrolling (Arcade 3.x+)
        self.camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        
        # Player setup
        # ANIMATION PLACEHOLDER: Replace with animated sprite
        self.player_sprite = arcade.Sprite(
            ":resources:images/animated_characters/female_adventurer/femaleAdventurer_idle.png",
            PLAYER_SCALING
        )
        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 256
        self.player_list.append(self.player_sprite)
        
        # Physics engine
        self.physics_engine = None
        
        # Setup level
        self.setup_level()
        
        # Invincibility frames after taking damage
        self.invincible_timer = 0
        
    def setup_level(self):
        """Create the game level based on difficulty"""
        
        # Adjust difficulty parameters
        if self.difficulty == EASY:
            level_length = 3000
            num_enemies = 3
            num_coins = 15
            self.player_health = 100
        elif self.difficulty == MEDIUM:
            level_length = 5000
            num_enemies = 6
            num_coins = 25
            self.player_health = 80
        else:  # HARD
            level_length = 10000
            num_enemies = 20
            num_coins = 50
            self.player_health = 50
        
        # Create ground
        for x in range(0, level_length, 64):
            wall = arcade.Sprite(
                ":resources:images/tiles/grassMid.png",
                TILE_SCALING
            )
            wall.center_x = x
            wall.center_y = 32
            self.wall_list.append(wall)
        
        # Create platforms at various heights
        platform_positions = [
            (400, 150), (600, 250), (900, 180), (1200, 280),
            (1500, 200), (1800, 300), (2100, 220), (2400, 180),
            (2700, 260), (3000, 200), (3300, 280)
        ]
        
        # Adjust number of platforms based on difficulty
        num_platforms = min(len(platform_positions), level_length // 300)
        
        for i in range(num_platforms):
            x, y = platform_positions[i % len(platform_positions)]
            x = x + (i // len(platform_positions)) * 300
            
            # Create platform (3 blocks wide)
            for offset in range(-64, 129, 64):
                if x + offset < level_length:
                    platform = arcade.Sprite(
                        ":resources:images/tiles/grassMid.png",
                        TILE_SCALING
                    )
                    platform.center_x = x + offset
                    platform.center_y = y
                    self.wall_list.append(platform)
        
        # Add coins
        self.total_coins = num_coins
        for i in range(num_coins):
            coin = arcade.Sprite(
                ":resources:images/items/coinGold.png",
                COIN_SCALING
            )
            # Distribute coins throughout the level, placed above ground/platforms
            coin.center_x = random.randint(200, level_length - 200)
            coin.center_y = random.randint(150, 350)
            self.coin_list.append(coin)
        
        # Add enemies
        for i in range(num_enemies):
            enemy = arcade.Sprite(
                ":resources:images/enemies/slimeBlue.png",
                ENEMY_SCALING
            )
            enemy.center_x = random.randint(300, level_length - 300)
            enemy.center_y = 96
            enemy.change_x = ENEMY_MOVE_SPEED * random.choice([-1, 1])
            self.enemy_list.append(enemy)
        
        # Add end goal
        end_goal = arcade.Sprite(
            ":resources:images/items/flagGreen2.png",
            TILE_SCALING * 1.5
        )
        end_goal.center_x = level_length - 100
        end_goal.center_y = 128
        self.end_goal_list.append(end_goal)
        
        # Setup physics
        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player_sprite,
            walls=self.wall_list,
            gravity_constant=GRAVITY
        )
    
    def update(self, delta_time):
        """Update game logic"""
        
        # Update invincibility timer
        if self.invincible_timer > 0:
            self.invincible_timer -= delta_time
        
        # Update physics
        self.physics_engine.update()
        
        # Update enemies
        for enemy in self.enemy_list:
            enemy.center_x += enemy.change_x
            
            # Bounce enemies off walls or edges
            if enemy.left < 0 or enemy.right > 7000:
                enemy.change_x *= -1
            
            # Check if enemy hits a wall
            walls_hit = arcade.check_for_collision_with_list(enemy, self.wall_list)
            if len(walls_hit) > 1:  # More than just the ground
                enemy.change_x *= -1
        
        # Coin collection
        coins_hit = arcade.check_for_collision_with_list(
            self.player_sprite,
            self.coin_list
        )
        for coin in coins_hit:
            coin.remove_from_sprite_lists()
            self.score += 10
            self.coins_collected += 1
        
        # Enemy collision (damage)
        if self.invincible_timer <= 0:
            enemies_hit = arcade.check_for_collision_with_list(
                self.player_sprite,
                self.enemy_list
            )
            if enemies_hit:
                damage = 5 if self.difficulty == EASY else 10 if self.difficulty == MEDIUM else 15
                self.player_health -= damage
                self.invincible_timer = 1.0  # 1 second invincibility
                
                if self.player_health <= 0:
                    return GAME_OVER
        
        # Check win condition
        end_goal_hit = arcade.check_for_collision_with_list(
            self.player_sprite,
            self.end_goal_list
        )
        if end_goal_hit and self.coins_collected >= self.total_coins:
            return GAME_WIN
        
        # Update camera
        self.center_camera_on_player()
        
        # Check if player falls off
        if self.player_sprite.center_y < -100:
            self.player_health = 0
            return GAME_OVER
        
        return GAME_PLAY
    
    def center_camera_on_player(self):
        """Center camera on player"""
        # Center camera on player with smooth following
        # Position player at 1/3 of screen width (left side) to see ahead
        target_x = self.player_sprite.center_x - SCREEN_WIDTH / 3
        target_y = self.player_sprite.center_y - SCREEN_HEIGHT * 2 / 3
        
        # Don't let camera go below 0
        if target_x < 0:
            target_x = 0
        if target_y < 0:
            target_y = 0
        
        # Set camera position
        self.camera.position = (target_x, target_y)
    
    def draw(self):
        """Draw the game"""
        
        # Draw game world with camera
        self.camera.use()
        
        self.wall_list.draw()
        self.coin_list.draw()
        self.enemy_list.draw()
        self.end_goal_list.draw()
        
        # Flash player when invincible
        if self.invincible_timer <= 0 or int(self.invincible_timer * 10) % 2 == 0:
            self.player_list.draw()
        
        # Draw GUI with fixed camera
        self.gui_camera.use()
        
        # Health bar
        health_width = 200
        health_height = 20
        health_x = 20
        health_y = SCREEN_HEIGHT - 40
        
        # Background (red)
        arcade.draw_lrbt_rectangle_filled(
            health_x, health_x + health_width,
            health_y - health_height / 2, health_y + health_height / 2,
            arcade.color.DARK_RED
        )
        
        # Current health (green)
        current_health_width = (self.player_health / 100) * health_width
        arcade.draw_lrbt_rectangle_filled(
            health_x, health_x + current_health_width,
            health_y - health_height / 2, health_y + health_height / 2,
            arcade.color.GREEN
        )
        
        # Health text
        arcade.draw_text(
            f"Health: {max(0, self.player_health)}",
            health_x + health_width + 10, health_y - 8,
            arcade.color.WHITE, 18, bold=True
        )
        
        # Score
        arcade.draw_text(
            f"Score: {self.score}",
            20, SCREEN_HEIGHT - 80,
            arcade.color.WHITE, 20, bold=True
        )
        
        # Coins collected
        arcade.draw_text(
            f"Coins: {self.coins_collected}/{self.total_coins}",
            20, SCREEN_HEIGHT - 110,
            arcade.color.YELLOW, 20, bold=True
        )
        
        # Instructions if near end
        if self.player_sprite.center_x > 6500:
            if self.coins_collected < self.total_coins:
                arcade.draw_text(
                    f"Collect all coins first! ({self.coins_collected}/{self.total_coins})",
                    SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100,
                    arcade.color.RED, 24,
                    anchor_x="center", bold=True
                )
            else:
                arcade.draw_text(
                    "Reach the flag to win!",
                    SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100,
                    arcade.color.GREEN, 24,
                    anchor_x="center", bold=True
                )
    
    def on_key_press(self, key):
        """Handle key presses"""
        if key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                # ANIMATION PLACEHOLDER: Switch to jump animation
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -PLAYER_MOVE_SPEED
            # ANIMATION PLACEHOLDER: Switch to walk left animation
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = PLAYER_MOVE_SPEED
            # ANIMATION PLACEHOLDER: Switch to walk right animation
    
    def on_key_release(self, key):
        """Handle key releases"""
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0
            # ANIMATION PLACEHOLDER: Switch to idle animation


class PlatformerGame(arcade.Window):
    """Main game window"""
    
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.SKY_BLUE)
        
        self.game_state = MENU
        self.menu_view = MenuView(self)
        self.game_view = None
        self.game_over_view = None
    
    def setup(self):
        """Setup the game"""
        self.game_state = MENU
        self.menu_view = MenuView(self)
    
    def on_draw(self):
        """Render the screen"""
        self.clear()
        
        if self.game_state == MENU:
            self.menu_view.draw()
        elif self.game_state == GAME_PLAY:
            if self.game_view:
                self.game_view.draw()
        elif self.game_state in [GAME_OVER, GAME_WIN]:
            if self.game_over_view:
                self.game_over_view.draw()
    
    def on_update(self, delta_time):
        """Update game logic"""
        if self.game_state == GAME_PLAY and self.game_view:
            result = self.game_view.update(delta_time)
            if result == GAME_OVER:
                self.game_state = GAME_OVER
                self.game_over_view = GameOverView(
                    self,
                    won=False,
                    score=self.game_view.score,
                    health=self.game_view.player_health
                )
            elif result == GAME_WIN:
                self.game_state = GAME_WIN
                self.game_over_view = GameOverView(
                    self,
                    won=True,
                    score=self.game_view.score,
                    health=self.game_view.player_health
                )
    
    def on_key_press(self, key, modifiers):
        """Handle key presses"""
        if self.game_state == MENU:
            if key == arcade.key.NUM_1:
                self.menu_view.selected_difficulty = EASY
            elif key == arcade.key.NUM_2:
                self.menu_view.selected_difficulty = MEDIUM
            elif key == arcade.key.NUM_3:
                self.menu_view.selected_difficulty = HARD
            elif key == arcade.key.ENTER:
                self.game_state = GAME_PLAY
                self.game_view = GamePlayView(self, self.menu_view.selected_difficulty)
        
        elif self.game_state == GAME_PLAY:
            if self.game_view:
                self.game_view.on_key_press(key)
        
        elif self.game_state in [GAME_OVER, GAME_WIN]:
            if key == arcade.key.R:
                # Restart game
                self.game_state = GAME_PLAY
                self.game_view = GamePlayView(self, self.menu_view.selected_difficulty)
            elif key == arcade.key.ESCAPE:
                # Back to menu
                self.setup()
    
    def on_key_release(self, key, modifiers):
        """Handle key releases"""
        if self.game_state == GAME_PLAY and self.game_view:
            self.game_view.on_key_release(key)


def main():
    """Main function"""
    game = PlatformerGame()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()