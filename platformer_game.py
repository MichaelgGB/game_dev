#!/usr/bin/env python3
"""
Complete 2D Platformer Game
Features:
- 3 Game States: Menu, Playing, Game Over
- Animated player sprites (jumping, running, idle)
- Collision detection with coins
- Health system with enemies
- Multiple levels with increasing difficulty
- Smooth gameplay and particle effects
"""

import pygame
import random
import math
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 220, 50)
BLUE = (50, 150, 220)
YELLOW = (255, 215, 0)
ORANGE = (255, 140, 0)
PURPLE = (150, 50, 200)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (180, 180, 180)
SKY_BLUE = (135, 206, 235)
GOLD = (255, 215, 0)
DARK_GREEN = (34, 139, 34)
BROWN = (139, 69, 19)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    LEVEL_COMPLETE = 4
    PAUSED = 5


class Particle:
    """Particle effect for visual feedback"""
    def __init__(self, x, y, color, velocity):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.life = 30
        self.size = random.randint(2, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.3  # Gravity
        self.life -= 1
        self.size = max(1, self.size - 0.1)
    
    def draw(self, screen):
        if self.life > 0:
            alpha = int((self.life / 30) * 255)
            s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, alpha)
            pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
            screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class Player:
    """Player character with animations"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.jump_power = 15
        self.gravity = 0.8
        self.on_ground = False
        self.health = 100
        self.max_health = 100
        self.score = 0
        self.facing_right = True
        self.animation_frame = 0
        self.animation_timer = 0
        self.state = "idle"  # idle, run, jump
        self.invincible = 0  # Invincibility frames after hit
        
        # Improved jump mechanics
        self.coyote_time = 0  # Frames since leaving ground
        self.coyote_time_max = 6  # Allow jump for 6 frames after leaving platform
        self.jump_buffer = 0  # Frames since jump was pressed
        self.jump_buffer_max = 6  # Buffer jump input for 6 frames
        self.is_jumping = False  # Track if currently in a jump
        self.jump_cut_multiplier = 0.5  # Velocity multiplier when releasing jump early
        
        # Cache rect for performance
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
    def update(self, platforms):
        # Update animation
        self.animation_timer += 1
        if self.animation_timer > 8:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
        
        # Apply gravity
        self.vel_y += self.gravity
        
        # Limit fall speed
        if self.vel_y > 20:
            self.vel_y = 20
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Update cached rect
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Track if we were on ground before collision check
        was_on_ground = self.on_ground
        
        # Check platform collisions
        self.on_ground = False
        
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                # Collision from top
                if self.vel_y > 0 and self.rect.bottom <= platform.rect.top + 20:
                    self.y = platform.rect.top - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                # Collision from bottom
                elif self.vel_y < 0 and self.rect.top >= platform.rect.bottom - 20:
                    self.y = platform.rect.bottom
                    self.vel_y = 0
                # Collision from sides
                else:
                    if self.vel_x > 0:  # Moving right
                        self.x = platform.rect.left - self.width
                    elif self.vel_x < 0:  # Moving left
                        self.x = platform.rect.right
                    self.vel_x = 0
                # Update rect after collision resolution
                self.rect.x = self.x
                self.rect.y = self.y
        
        # Coyote time - allow jumping shortly after leaving platform
        if self.on_ground:
            self.coyote_time = self.coyote_time_max
        elif was_on_ground and not self.on_ground and not self.is_jumping:
            # Just left the ground without jumping
            pass  # coyote_time will decrement below
        
        if self.coyote_time > 0:
            self.coyote_time -= 1
        
        # Jump buffer countdown
        if self.jump_buffer > 0:
            self.jump_buffer -= 1
            # Try to execute buffered jump
            if self.can_jump():
                self._execute_jump()
        
        # Update state
        if not self.on_ground:
            self.state = "jump"
        elif abs(self.vel_x) > 0:
            self.state = "run"
        else:
            self.state = "idle"
        
        # Decrease invincibility
        if self.invincible > 0:
            self.invincible -= 1
        
        # Keep player in bounds
        if self.x < 0:
            self.x = 0
        if self.y > SCREEN_HEIGHT:
            self.health = 0
    
    def can_jump(self):
        """Check if player can jump (on ground or within coyote time)"""
        return self.on_ground or self.coyote_time > 0
    
    def _execute_jump(self):
        """Actually perform the jump"""
        self.vel_y = -self.jump_power
        self.is_jumping = True
        self.coyote_time = 0
        self.jump_buffer = 0
    
    def jump(self):
        """Request a jump - uses coyote time and jump buffering"""
        if self.can_jump():
            self._execute_jump()
        else:
            # Buffer the jump input
            self.jump_buffer = self.jump_buffer_max
    
    def release_jump(self):
        """Called when jump key is released - enables variable jump height"""
        if self.is_jumping and self.vel_y < 0:
            self.vel_y *= self.jump_cut_multiplier
    
    def move_left(self):
        self.vel_x = -self.speed
        self.facing_right = False
    
    def move_right(self):
        self.vel_x = self.speed
        self.facing_right = True
    
    def stop_horizontal(self):
        self.vel_x = 0
    
    def take_damage(self, amount):
        if self.invincible == 0:
            self.health -= amount
            self.invincible = 60  # 1 second of invincibility
            if self.health < 0:
                self.health = 0
    
    def draw(self, screen, camera_x):
        screen_x = self.x - camera_x
        
        # Draw player with animation
        color = BLUE
        if self.invincible > 0 and self.invincible % 10 < 5:
            color = LIGHT_GRAY  # Flashing effect when invincible
        
        # Body
        body_rect = pygame.Rect(screen_x + 5, self.y + 10, 20, 25)
        pygame.draw.rect(screen, color, body_rect, border_radius=5)
        
        # Head
        head_x = screen_x + 15
        head_y = self.y + 5
        pygame.draw.circle(screen, color, (int(head_x), int(head_y)), 8)
        
        # Eyes
        eye_offset = 2 if self.facing_right else -2
        pygame.draw.circle(screen, WHITE, (int(head_x + eye_offset), int(head_y)), 2)
        
        # Arms animation
        if self.state == "run":
            arm_swing = math.sin(self.animation_frame * math.pi / 2) * 5
            pygame.draw.line(screen, color, (screen_x + 10, self.y + 15), 
                           (screen_x + 5, self.y + 20 + arm_swing), 3)
            pygame.draw.line(screen, color, (screen_x + 20, self.y + 15), 
                           (screen_x + 25, self.y + 20 - arm_swing), 3)
        elif self.state == "jump":
            pygame.draw.line(screen, color, (screen_x + 10, self.y + 15), 
                           (screen_x + 5, self.y + 10), 3)
            pygame.draw.line(screen, color, (screen_x + 20, self.y + 15), 
                           (screen_x + 25, self.y + 10), 3)
        else:
            pygame.draw.line(screen, color, (screen_x + 10, self.y + 15), 
                           (screen_x + 7, self.y + 22), 3)
            pygame.draw.line(screen, color, (screen_x + 20, self.y + 15), 
                           (screen_x + 23, self.y + 22), 3)
        
        # Legs animation
        if self.state == "run":
            leg_swing = math.sin(self.animation_frame * math.pi / 2) * 6
            pygame.draw.line(screen, color, (screen_x + 12, self.y + 35), 
                           (screen_x + 10, self.y + 42 + leg_swing), 3)
            pygame.draw.line(screen, color, (screen_x + 18, self.y + 35), 
                           (screen_x + 20, self.y + 42 - leg_swing), 3)
        elif self.state == "jump":
            pygame.draw.line(screen, color, (screen_x + 12, self.y + 35), 
                           (screen_x + 8, self.y + 38), 3)
            pygame.draw.line(screen, color, (screen_x + 18, self.y + 35), 
                           (screen_x + 22, self.y + 38), 3)
        else:
            pygame.draw.line(screen, color, (screen_x + 12, self.y + 35), 
                           (screen_x + 12, self.y + 42), 3)
            pygame.draw.line(screen, color, (screen_x + 18, self.y + 35), 
                           (screen_x + 18, self.y + 42), 3)


class Platform:
    """Static platform"""
    def __init__(self, x, y, width, height, platform_type="grass"):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = platform_type
        
    def draw(self, screen, camera_x):
        screen_x = self.rect.x - camera_x
        
        # Skip if off screen (performance optimization)
        if screen_x + self.rect.width < 0 or screen_x > SCREEN_WIDTH:
            return
            
        rect = pygame.Rect(screen_x, self.rect.y, self.rect.width, self.rect.height)
        
        if self.type == "grass":
            pygame.draw.rect(screen, DARK_GREEN, rect)
            pygame.draw.rect(screen, GREEN, (rect.x, rect.y, rect.width, 5))
        elif self.type == "stone":
            pygame.draw.rect(screen, DARK_GRAY, rect)
            for i in range(0, self.rect.width, 20):
                pygame.draw.rect(screen, LIGHT_GRAY, (rect.x + i, rect.y, 18, self.rect.height), 1)
        else:
            pygame.draw.rect(screen, BROWN, rect)


class Coin:
    """Collectible coin"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.collected = False
        self.bob_offset = 0
        self.bob_speed = 0.1
        self.rotation = 0
        
    def update(self):
        self.bob_offset = math.sin(self.rotation) * 5
        self.rotation += self.bob_speed
        
    def check_collision(self, player):
        coin_rect = pygame.Rect(self.x, self.y + self.bob_offset, self.width, self.height)
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        
        if coin_rect.colliderect(player_rect) and not self.collected:
            self.collected = True
            player.score += 10
            return True
        return False
    
    def draw(self, screen, camera_x):
        if not self.collected:
            screen_x = self.x - camera_x
            
            # Skip if off screen (performance optimization)
            if screen_x < -30 or screen_x > SCREEN_WIDTH + 30:
                return
                
            y = self.y + self.bob_offset
            
            # Draw coin with rotation effect
            scale = abs(math.cos(self.rotation))
            width = int(self.width * scale)
            if width < 2:
                width = 2
            
            # Outer circle
            pygame.draw.ellipse(screen, GOLD, (screen_x + (self.width - width) // 2, 
                                                y, width, self.height))
            # Inner circle
            if width > 8:
                pygame.draw.ellipse(screen, YELLOW, (screen_x + (self.width - width) // 2 + 3, 
                                                     y + 3, width - 6, self.height - 6))


class Enemy:
    """Enemy that patrols and damages player"""
    def __init__(self, x, y, patrol_distance):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.speed = 2
        self.direction = 1
        self.damage = 20
        self.animation_frame = 0
        
        # Cache rect for performance
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
    def update(self, platforms):
        # Move back and forth
        self.x += self.speed * self.direction
        
        # Turn around at patrol limits
        if self.x > self.start_x + self.patrol_distance:
            self.direction = -1
        elif self.x < self.start_x:
            self.direction = 1
        
        # Animation
        self.animation_frame += 1
        
        # Apply gravity
        self.y += 5
        self.rect.x = self.x
        self.rect.y = self.y
        
        # Check platform collisions
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.y < platform.rect.top:
                    self.y = platform.rect.top - self.height
                    self.rect.y = self.y
                    break
    
    def check_collision(self, player):
        if self.rect.colliderect(player.rect):
            player.take_damage(self.damage)
            return True
        return False
    
    def draw(self, screen, camera_x):
        screen_x = self.x - camera_x
        
        # Skip if off screen (performance optimization)
        if screen_x < -50 or screen_x > SCREEN_WIDTH + 50:
            return
        
        # Body
        body_color = RED
        pygame.draw.rect(screen, body_color, (screen_x, self.y, self.width, self.height), 
                        border_radius=5)
        
        # Eyes
        eye_offset = math.sin(self.animation_frame * 0.1) * 2
        pygame.draw.circle(screen, YELLOW, (int(screen_x + 10), int(self.y + 10 + eye_offset)), 3)
        pygame.draw.circle(screen, YELLOW, (int(screen_x + 20), int(self.y + 10 - eye_offset)), 3)
        
        # Spikes
        for i in range(3):
            spike_x = screen_x + 5 + i * 10
            points = [(spike_x, self.y), (spike_x + 5, self.y - 5), (spike_x + 10, self.y)]
            pygame.draw.polygon(screen, ORANGE, points)


class Level:
    """Level class containing all level data"""
    def __init__(self, level_number):
        self.level_number = level_number
        self.platforms = []
        self.coins = []
        self.enemies = []
        self.width = 3000  # Level width
        self.goal_x = self.width - 100
        self.spawn_x = 100
        self.spawn_y = 300
        
        self.generate_level()
    
    def generate_level(self):
        """Generate level based on difficulty"""
        # Ground
        self.platforms.append(Platform(0, SCREEN_HEIGHT - 40, self.width, 40, "grass"))
        
        if self.level_number == 1:
            # Level 1 - Easy
            # Platforms
            self.platforms.append(Platform(200, 450, 150, 20, "grass"))
            self.platforms.append(Platform(400, 380, 150, 20, "grass"))
            self.platforms.append(Platform(600, 320, 150, 20, "grass"))
            self.platforms.append(Platform(850, 400, 200, 20, "grass"))
            self.platforms.append(Platform(1100, 350, 150, 20, "grass"))
            self.platforms.append(Platform(1350, 300, 150, 20, "grass"))
            self.platforms.append(Platform(1600, 400, 200, 20, "stone"))
            self.platforms.append(Platform(1900, 350, 150, 20, "grass"))
            self.platforms.append(Platform(2150, 400, 150, 20, "grass"))
            self.platforms.append(Platform(2400, 350, 200, 20, "grass"))
            
            # Coins - placed above platforms so they're reachable
            # Coins on ground level
            for i in range(3):
                self.coins.append(Coin(100 + i * 80, SCREEN_HEIGHT - 70))
            # Coins above platforms (30 pixels above platform surface)
            self.coins.append(Coin(250, 450 - 30))   # Above platform at y=450
            self.coins.append(Coin(450, 380 - 30))   # Above platform at y=380
            self.coins.append(Coin(650, 320 - 30))   # Above platform at y=320
            self.coins.append(Coin(900, 400 - 30))   # Above platform at y=400
            self.coins.append(Coin(1150, 350 - 30))  # Above platform at y=350
            self.coins.append(Coin(1400, 300 - 30))  # Above platform at y=300
            self.coins.append(Coin(1650, 400 - 30))  # Above platform at y=400
            self.coins.append(Coin(1950, 350 - 30))  # Above platform at y=350
            self.coins.append(Coin(2200, 400 - 30))  # Above platform at y=400
            self.coins.append(Coin(2450, 350 - 30))  # Above platform at y=350
            
            # Enemies
            self.enemies.append(Enemy(850, 350, 150))
            self.enemies.append(Enemy(1600, 350, 180))
            
        elif self.level_number == 2:
            # Level 2 - Medium
            # More complex platforms
            self.platforms.append(Platform(150, 480, 100, 20, "stone"))
            self.platforms.append(Platform(300, 420, 100, 20, "stone"))
            self.platforms.append(Platform(450, 360, 100, 20, "stone"))
            self.platforms.append(Platform(650, 400, 150, 20, "grass"))
            self.platforms.append(Platform(900, 320, 120, 20, "stone"))
            self.platforms.append(Platform(1100, 380, 150, 20, "grass"))
            self.platforms.append(Platform(1350, 300, 100, 20, "stone"))
            self.platforms.append(Platform(1550, 380, 150, 20, "grass"))
            self.platforms.append(Platform(1800, 320, 120, 20, "stone"))
            self.platforms.append(Platform(2000, 400, 100, 20, "grass"))
            self.platforms.append(Platform(2200, 350, 150, 20, "stone"))
            self.platforms.append(Platform(2450, 300, 120, 20, "grass"))
            self.platforms.append(Platform(2650, 380, 150, 20, "stone"))
            
            # Coins - placed above platforms so they're reachable
            # Coins on ground
            for i in range(2):
                self.coins.append(Coin(50 + i * 60, SCREEN_HEIGHT - 70))
            # Coins above platforms
            self.coins.append(Coin(180, 480 - 30))   # Above platform at y=480
            self.coins.append(Coin(330, 420 - 30))   # Above platform at y=420
            self.coins.append(Coin(480, 360 - 30))   # Above platform at y=360
            self.coins.append(Coin(700, 400 - 30))   # Above platform at y=400
            self.coins.append(Coin(940, 320 - 30))   # Above platform at y=320
            self.coins.append(Coin(1150, 380 - 30))  # Above platform at y=380
            self.coins.append(Coin(1380, 300 - 30))  # Above platform at y=300
            self.coins.append(Coin(1600, 380 - 30))  # Above platform at y=380
            self.coins.append(Coin(1840, 320 - 30))  # Above platform at y=320
            self.coins.append(Coin(2030, 400 - 30))  # Above platform at y=400
            self.coins.append(Coin(2250, 350 - 30))  # Above platform at y=350
            self.coins.append(Coin(2490, 300 - 30))  # Above platform at y=300
            self.coins.append(Coin(2700, 380 - 30))  # Above platform at y=380
            
            # More enemies
            self.enemies.append(Enemy(650, 350, 120))
            self.enemies.append(Enemy(1100, 330, 130))
            self.enemies.append(Enemy(1550, 330, 140))
            self.enemies.append(Enemy(2200, 300, 140))
            
        else:
            # Level 3 - Hard
            # Complex jumping required
            self.platforms.append(Platform(120, 500, 80, 20, "stone"))
            self.platforms.append(Platform(250, 450, 80, 20, "stone"))
            self.platforms.append(Platform(380, 400, 80, 20, "stone"))
            self.platforms.append(Platform(520, 350, 80, 20, "stone"))
            self.platforms.append(Platform(700, 300, 120, 20, "grass"))
            self.platforms.append(Platform(900, 380, 100, 20, "stone"))
            self.platforms.append(Platform(1080, 320, 100, 20, "stone"))
            self.platforms.append(Platform(1260, 380, 100, 20, "grass"))
            self.platforms.append(Platform(1450, 300, 80, 20, "stone"))
            self.platforms.append(Platform(1620, 350, 100, 20, "stone"))
            self.platforms.append(Platform(1800, 280, 120, 20, "grass"))
            self.platforms.append(Platform(2000, 350, 100, 20, "stone"))
            self.platforms.append(Platform(2180, 300, 100, 20, "stone"))
            self.platforms.append(Platform(2360, 380, 100, 20, "grass"))
            self.platforms.append(Platform(2550, 320, 120, 20, "stone"))
            self.platforms.append(Platform(2750, 380, 150, 20, "grass"))
            
            # Coins - placed above platforms so they're reachable
            # Coins on ground at start
            for i in range(2):
                self.coins.append(Coin(30 + i * 50, SCREEN_HEIGHT - 70))
            # Coins above platforms
            self.coins.append(Coin(140, 500 - 30))   # Above platform at y=500
            self.coins.append(Coin(270, 450 - 30))   # Above platform at y=450
            self.coins.append(Coin(400, 400 - 30))   # Above platform at y=400
            self.coins.append(Coin(540, 350 - 30))   # Above platform at y=350
            self.coins.append(Coin(740, 300 - 30))   # Above platform at y=300
            self.coins.append(Coin(930, 380 - 30))   # Above platform at y=380
            self.coins.append(Coin(1110, 320 - 30))  # Above platform at y=320
            self.coins.append(Coin(1290, 380 - 30))  # Above platform at y=380
            self.coins.append(Coin(1470, 300 - 30))  # Above platform at y=300
            self.coins.append(Coin(1650, 350 - 30))  # Above platform at y=350
            self.coins.append(Coin(1840, 280 - 30))  # Above platform at y=280
            self.coins.append(Coin(2030, 350 - 30))  # Above platform at y=350
            self.coins.append(Coin(2210, 300 - 30))  # Above platform at y=300
            self.coins.append(Coin(2390, 380 - 30))  # Above platform at y=380
            self.coins.append(Coin(2590, 320 - 30))  # Above platform at y=320
            self.coins.append(Coin(2800, 380 - 30))  # Above platform at y=380
            
            # Many enemies
            self.enemies.append(Enemy(700, 250, 110))
            self.enemies.append(Enemy(1080, 270, 90))
            self.enemies.append(Enemy(1450, 250, 70))
            self.enemies.append(Enemy(1800, 230, 110))
            self.enemies.append(Enemy(2180, 250, 90))
            self.enemies.append(Enemy(2550, 270, 110))


class Game:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ultimate Platformer Adventure")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        
        # Game objects
        self.player = None
        self.current_level = 1
        self.level = None
        self.camera_x = 0
        self.particles = []
        
        # Fonts
        self.title_font = pygame.font.Font(None, 80)
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Menu selection
        self.menu_selection = 0
        self.menu_options = ["Start Game", "Instructions", "Quit"]
        self.show_instructions = False
    
    def start_level(self, level_number):
        """Start a specific level"""
        self.current_level = level_number
        self.level = Level(level_number)
        self.player = Player(self.level.spawn_x, self.level.spawn_y)
        self.camera_x = 0
        self.particles = []
        self.state = GameState.PLAYING
    
    def update_camera(self):
        """Update camera to follow player"""
        # Keep player centered
        target_x = self.player.x - SCREEN_WIDTH // 3
        
        # Smooth camera movement
        self.camera_x += (target_x - self.camera_x) * 0.1
        
        # Keep camera in bounds
        if self.camera_x < 0:
            self.camera_x = 0
        if self.camera_x > self.level.width - SCREEN_WIDTH:
            self.camera_x = self.level.width - SCREEN_WIDTH
    
    def create_particles(self, x, y, color, count=10):
        """Create particle effects"""
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 6)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed - 3)
            self.particles.append(Particle(x, y, color, velocity))
    
    def handle_menu_input(self, event):
        """Handle menu input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.menu_selection = (self.menu_selection - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                if self.menu_selection == 0:  # Start Game
                    self.start_level(1)
                elif self.menu_selection == 1:  # Instructions
                    self.show_instructions = not self.show_instructions
                elif self.menu_selection == 2:  # Quit
                    self.running = False
            elif event.key == pygame.K_ESCAPE:
                if self.show_instructions:
                    self.show_instructions = False
    
    def handle_game_input(self):
        """Handle game input"""
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.player.move_left()
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.player.move_right()
        else:
            self.player.stop_horizontal()
        
        if keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]:
            self.player.jump()
    
    def update_game(self):
        """Update game state"""
        # Update player
        self.player.update(self.level.platforms)
        
        # Update camera
        self.update_camera()
        
        # Update coins
        for coin in self.level.coins:
            coin.update()
            if coin.check_collision(self.player):
                self.create_particles(coin.x + 10, coin.y + 10, GOLD, 15)
        
        # Update enemies
        for enemy in self.level.enemies:
            enemy.update(self.level.platforms)
            if enemy.check_collision(self.player):
                self.create_particles(self.player.x + 15, self.player.y + 20, RED, 10)
        
        # Update particles (optimized - use list comprehension instead of remove in loop)
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.life > 0]
        
        # Check win condition
        if self.player.x >= self.level.goal_x:
            all_coins_collected = all(coin.collected for coin in self.level.coins)
            if all_coins_collected:
                self.state = GameState.LEVEL_COMPLETE
        
        # Check game over
        if self.player.health <= 0:
            self.state = GameState.GAME_OVER
    
    def draw_menu(self):
        """Draw main menu"""
        self.screen.fill(SKY_BLUE)
        
        if self.show_instructions:
            # Draw instructions
            title = self.title_font.render("Instructions", True, BLACK)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 80))
            self.screen.blit(title, title_rect)
            
            instructions = [
                "Controls:",
                "  Arrow Keys / A,D - Move Left/Right",
                "  Space / W / Up - Jump",
                "",
                "Objective:",
                "  Collect ALL coins to complete the level",
                "  Avoid enemies - they damage you!",
                "  Reach the goal at the end",
                "",
                "Features:",
                "  3 Levels with increasing difficulty",
                "  Health system - don't let it reach 0!",
                "  Score points by collecting coins",
                "",
                "Press ESC to return to menu"
            ]
            
            y = 150
            for line in instructions:
                text = self.small_font.render(line, True, BLACK)
                self.screen.blit(text, (100, y))
                y += 30
        else:
            # Draw title with shadow
            title_shadow = self.title_font.render("PLATFORMER", True, DARK_GRAY)
            title = self.title_font.render("PLATFORMER", True, BLUE)
            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
            self.screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
            self.screen.blit(title, title_rect)
            
            subtitle = self.font.render("ADVENTURE", True, ORANGE)
            subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 160))
            self.screen.blit(subtitle, subtitle_rect)
            
            # Draw menu options
            for i, option in enumerate(self.menu_options):
                color = YELLOW if i == self.menu_selection else WHITE
                text = self.font.render(option, True, color)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, 300 + i * 60))
                
                if i == self.menu_selection:
                    # Draw selection indicator
                    pygame.draw.polygon(self.screen, YELLOW, [
                        (text_rect.left - 30, text_rect.centery - 10),
                        (text_rect.left - 30, text_rect.centery + 10),
                        (text_rect.left - 15, text_rect.centery)
                    ])
                
                self.screen.blit(text, text_rect)
            
            # Draw controls hint
            hint = self.small_font.render("Use Arrow Keys and Enter", True, LIGHT_GRAY)
            hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            self.screen.blit(hint, hint_rect)
    
    def draw_game(self):
        """Draw game screen"""
        # Sky background
        self.screen.fill(SKY_BLUE)
        
        # Draw platforms
        for platform in self.level.platforms:
            platform.draw(self.screen, self.camera_x)
        
        # Draw coins
        for coin in self.level.coins:
            coin.draw(self.screen, self.camera_x)
        
        # Draw enemies
        for enemy in self.level.enemies:
            enemy.draw(self.screen, self.camera_x)
        
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)
        
        # Draw player
        self.player.draw(self.screen, self.camera_x)
        
        # Draw goal
        goal_x = self.level.goal_x - self.camera_x
        if goal_x >= -100 and goal_x <= SCREEN_WIDTH + 100:
            pygame.draw.rect(self.screen, GOLD, (goal_x, SCREEN_HEIGHT - 140, 50, 100))
            pygame.draw.polygon(self.screen, YELLOW, [
                (goal_x + 50, SCREEN_HEIGHT - 140),
                (goal_x + 50, SCREEN_HEIGHT - 100),
                (goal_x + 80, SCREEN_HEIGHT - 120)
            ])
            flag_text = self.small_font.render("GOAL", True, BLACK)
            self.screen.blit(flag_text, (goal_x + 5, SCREEN_HEIGHT - 170))
        
        # Draw HUD
        self.draw_hud()
    
    def draw_hud(self):
        """Draw heads-up display"""
        # Health bar
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = 20
        
        # Background
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        pygame.draw.rect(self.screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
        
        # Health
        health_width = int((self.player.health / self.player.max_health) * bar_width)
        health_color = GREEN if self.player.health > 50 else (ORANGE if self.player.health > 25 else RED)
        pygame.draw.rect(self.screen, health_color, (bar_x, bar_y, health_width, bar_height))
        
        # Health text
        health_text = self.small_font.render(f"Health: {self.player.health}/{self.player.max_health}", 
                                             True, WHITE)
        self.screen.blit(health_text, (bar_x + 5, bar_y + 1))
        
        # Score
        score_text = self.font.render(f"Score: {self.player.score}", True, YELLOW)
        self.screen.blit(score_text, (20, 50))
        
        # Level
        level_text = self.font.render(f"Level: {self.current_level}", True, WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH - 150, 20))
        
        # Coins collected
        total_coins = len(self.level.coins)
        collected_coins = sum(1 for coin in self.level.coins if coin.collected)
        coins_text = self.small_font.render(f"Coins: {collected_coins}/{total_coins}", True, GOLD)
        self.screen.blit(coins_text, (SCREEN_WIDTH - 150, 50))
        
        # Instructions
        if self.player.x < 300:  # Show at start
            hint = self.small_font.render("Arrow Keys to move, Space to jump", True, WHITE)
            hint_rect = hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            
            # Background for readability
            bg_rect = pygame.Rect(hint_rect.x - 10, hint_rect.y - 5, 
                                 hint_rect.width + 20, hint_rect.height + 10)
            s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))
            self.screen.blit(s, bg_rect)
            
            self.screen.blit(hint, hint_rect)
    
    def draw_game_over(self):
        """Draw game over screen"""
        self.screen.fill(DARK_GRAY)
        
        # Title
        title = self.title_font.render("GAME OVER", True, RED)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Stats
        score_text = self.font.render(f"Final Score: {self.player.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 250))
        self.screen.blit(score_text, score_rect)
        
        level_text = self.font.render(f"Level Reached: {self.current_level}", True, WHITE)
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, 300))
        self.screen.blit(level_text, level_rect)
        
        # Options
        retry_text = self.font.render("Press R to Retry", True, GREEN)
        retry_rect = retry_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(retry_text, retry_rect)
        
        menu_text = self.font.render("Press M for Menu", True, BLUE)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, 450))
        self.screen.blit(menu_text, menu_rect)
    
    def draw_level_complete(self):
        """Draw level complete screen"""
        self.screen.fill(SKY_BLUE)
        
        # Title
        title = self.title_font.render("LEVEL COMPLETE!", True, GOLD)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        # Stars based on performance
        stars = 3
        if self.player.health < 50:
            stars = 2
        if self.player.health < 25:
            stars = 1
        
        # Draw stars
        star_y = 230
        for i in range(3):
            color = GOLD if i < stars else DARK_GRAY
            star_x = SCREEN_WIDTH // 2 - 60 + i * 60
            self.draw_star(star_x, star_y, 25, color)
        
        # Stats
        score_text = self.font.render(f"Score: {self.player.score}", True, BLACK)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 320))
        self.screen.blit(score_text, score_rect)
        
        health_text = self.font.render(f"Health Remaining: {self.player.health}%", True, BLACK)
        health_rect = health_text.get_rect(center=(SCREEN_WIDTH // 2, 370))
        self.screen.blit(health_text, health_rect)
        
        # Options
        if self.current_level < 3:
            next_text = self.font.render("Press SPACE for Next Level", True, BLUE)
            next_rect = next_text.get_rect(center=(SCREEN_WIDTH // 2, 450))
            self.screen.blit(next_text, next_rect)
        else:
            win_text = self.title_font.render("YOU WIN!", True, GOLD)
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, 450))
            self.screen.blit(win_text, win_rect)
        
        menu_text = self.small_font.render("Press M for Menu", True, DARK_GRAY)
        menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, 520))
        self.screen.blit(menu_text, menu_rect)
    
    def draw_paused(self):
        """Draw pause screen overlay"""
        # Draw the game in background
        self.draw_game()
        
        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Pause title
        title = self.title_font.render("PAUSED", True, WHITE)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 200))
        self.screen.blit(title, title_rect)
        
        # Options
        options = [
            ("Press ESC or P to Resume", GREEN),
            ("Press R to Restart Level", YELLOW),
            ("Press M for Main Menu", BLUE)
        ]
        
        y = 320
        for text, color in options:
            rendered = self.font.render(text, True, color)
            text_rect = rendered.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(rendered, text_rect)
            y += 50
        
        # Current stats
        stats_text = self.small_font.render(
            f"Level {self.current_level} | Score: {self.player.score} | Health: {self.player.health}%",
            True, LIGHT_GRAY
        )
        stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH // 2, 500))
        self.screen.blit(stats_text, stats_rect)
    
    def draw_star(self, x, y, size, color):
        """Draw a star shape"""
        points = []
        for i in range(10):
            angle = math.pi * 2 * i / 10 - math.pi / 2
            if i % 2 == 0:
                r = size
            else:
                r = size // 2
            px = x + math.cos(angle) * r
            py = y + math.sin(angle) * r
            points.append((px, py))
        pygame.draw.polygon(self.screen, color, points)
    
    def run(self):
        """Main game loop"""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if self.state == GameState.MENU:
                    self.handle_menu_input(event)
                
                elif self.state == GameState.GAME_OVER:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.start_level(self.current_level)
                        elif event.key == pygame.K_m:
                            self.state = GameState.MENU
                
                elif self.state == GameState.LEVEL_COMPLETE:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_SPACE and self.current_level < 3:
                            self.start_level(self.current_level + 1)
                        elif event.key == pygame.K_m:
                            self.state = GameState.MENU
                
                elif self.state == GameState.PAUSED:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                            self.state = GameState.PLAYING
                        elif event.key == pygame.K_m:
                            self.state = GameState.MENU
                        elif event.key == pygame.K_r:
                            self.start_level(self.current_level)
                
                elif self.state == GameState.PLAYING:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                            self.state = GameState.PAUSED
                    # Handle jump release for variable jump height
                    elif event.type == pygame.KEYUP:
                        if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                            self.player.release_jump()
            
            # Update
            if self.state == GameState.PLAYING:
                self.handle_game_input()
                self.update_game()
            
            # Draw
            if self.state == GameState.MENU:
                self.draw_menu()
            elif self.state == GameState.PLAYING:
                self.draw_game()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
            elif self.state == GameState.LEVEL_COMPLETE:
                self.draw_level_complete()
            elif self.state == GameState.PAUSED:
                self.draw_paused()
            
            # Update display
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
