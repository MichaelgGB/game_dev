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
- Procedurally generated sound effects
"""

import pygame
import random
import math
import array
from enum import Enum

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

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


# Sound generation functions
def generate_sound(frequency, duration, volume=0.3, wave_type='square'):
    """Generate a simple sound wave"""
    sample_rate = 22050
    n_samples = int(sample_rate * duration)
    
    buf = array.array('h', [0] * n_samples)
    max_amplitude = int(32767 * volume)
    
    for i in range(n_samples):
        t = i / sample_rate
        
        if wave_type == 'square':
            # Square wave
            val = max_amplitude if math.sin(2 * math.pi * frequency * t) > 0 else -max_amplitude
        elif wave_type == 'sine':
            # Sine wave
            val = int(max_amplitude * math.sin(2 * math.pi * frequency * t))
        elif wave_type == 'sawtooth':
            # Sawtooth wave
            val = int(max_amplitude * (2 * (t * frequency - math.floor(t * frequency + 0.5))))
        else:
            val = 0
        
        # Apply envelope (fade out)
        envelope = 1.0 - (i / n_samples) * 0.7
        buf[i] = int(val * envelope)
    
    # Create stereo by duplicating the buffer
    stereo_buf = array.array('h')
    for sample in buf:
        stereo_buf.append(sample)
        stereo_buf.append(sample)
    
    return pygame.mixer.Sound(buffer=stereo_buf)


def generate_jump_sound():
    """Generate a rising pitch jump sound"""
    sample_rate = 22050
    duration = 0.15
    n_samples = int(sample_rate * duration)
    
    buf = array.array('h', [0] * n_samples)
    volume = 0.25
    max_amplitude = int(32767 * volume)
    
    for i in range(n_samples):
        t = i / sample_rate
        progress = i / n_samples
        # Rising frequency from 200 to 600 Hz
        frequency = 200 + progress * 400
        val = max_amplitude if math.sin(2 * math.pi * frequency * t) > 0 else -max_amplitude
        # Quick fade out
        envelope = 1.0 - progress * 0.5
        buf[i] = int(val * envelope)
    
    stereo_buf = array.array('h')
    for sample in buf:
        stereo_buf.append(sample)
        stereo_buf.append(sample)
    
    return pygame.mixer.Sound(buffer=stereo_buf)


def generate_coin_sound():
    """Generate a pleasant coin collect sound (two quick notes)"""
    sample_rate = 22050
    duration = 0.2
    n_samples = int(sample_rate * duration)
    
    buf = array.array('h', [0] * n_samples)
    volume = 0.2
    max_amplitude = int(32767 * volume)
    
    for i in range(n_samples):
        t = i / sample_rate
        progress = i / n_samples
        
        # Two notes: E5 then G5
        if progress < 0.5:
            frequency = 659  # E5
        else:
            frequency = 784  # G5
        
        val = int(max_amplitude * math.sin(2 * math.pi * frequency * t))
        envelope = 1.0 - progress * 0.8
        buf[i] = int(val * envelope)
    
    stereo_buf = array.array('h')
    for sample in buf:
        stereo_buf.append(sample)
        stereo_buf.append(sample)
    
    return pygame.mixer.Sound(buffer=stereo_buf)


def generate_damage_sound():
    """Generate a harsh damage sound"""
    sample_rate = 22050
    duration = 0.25
    n_samples = int(sample_rate * duration)
    
    buf = array.array('h', [0] * n_samples)
    volume = 0.3
    max_amplitude = int(32767 * volume)
    
    for i in range(n_samples):
        t = i / sample_rate
        progress = i / n_samples
        # Falling frequency with noise
        frequency = 300 - progress * 200
        noise = random.uniform(-0.3, 0.3)
        val = int(max_amplitude * (math.sin(2 * math.pi * frequency * t) + noise))
        val = max(-max_amplitude, min(max_amplitude, val))
        envelope = 1.0 - progress
        buf[i] = int(val * envelope)
    
    stereo_buf = array.array('h')
    for sample in buf:
        stereo_buf.append(sample)
        stereo_buf.append(sample)
    
    return pygame.mixer.Sound(buffer=stereo_buf)


def generate_level_complete_sound():
    """Generate a triumphant level complete jingle"""
    sample_rate = 22050
    duration = 0.8
    n_samples = int(sample_rate * duration)
    
    buf = array.array('h', [0] * n_samples)
    volume = 0.25
    max_amplitude = int(32767 * volume)
    
    # Notes: C E G C (arpeggio)
    notes = [(523, 0.0, 0.2), (659, 0.15, 0.2), (784, 0.3, 0.2), (1047, 0.45, 0.35)]
    
    for i in range(n_samples):
        t = i / sample_rate
        val = 0
        
        for freq, start, dur in notes:
            if start <= t < start + dur:
                note_progress = (t - start) / dur
                envelope = 1.0 - note_progress * 0.7
                val += int(max_amplitude * math.sin(2 * math.pi * freq * t) * envelope)
        
        buf[i] = max(-32767, min(32767, val))
    
    stereo_buf = array.array('h')
    for sample in buf:
        stereo_buf.append(sample)
        stereo_buf.append(sample)
    
    return pygame.mixer.Sound(buffer=stereo_buf)


def generate_menu_select_sound():
    """Generate a simple menu selection blip"""
    return generate_sound(440, 0.08, 0.2, 'sine')


def generate_menu_move_sound():
    """Generate a menu navigation sound"""
    return generate_sound(330, 0.05, 0.15, 'sine')


def generate_game_over_sound():
    """Generate a sad game over sound"""
    sample_rate = 22050
    duration = 0.6
    n_samples = int(sample_rate * duration)
    
    buf = array.array('h', [0] * n_samples)
    volume = 0.25
    max_amplitude = int(32767 * volume)
    
    # Descending notes
    notes = [(392, 0.0, 0.2), (330, 0.2, 0.2), (262, 0.4, 0.2)]
    
    for i in range(n_samples):
        t = i / sample_rate
        val = 0
        
        for freq, start, dur in notes:
            if start <= t < start + dur:
                note_progress = (t - start) / dur
                envelope = 1.0 - note_progress * 0.5
                val += int(max_amplitude * math.sin(2 * math.pi * freq * t) * envelope)
        
        buf[i] = max(-32767, min(32767, val))
    
    stereo_buf = array.array('h')
    for sample in buf:
        stereo_buf.append(sample)
        stereo_buf.append(sample)
    
    return pygame.mixer.Sound(buffer=stereo_buf)


# Generate all sounds at startup
class Sounds:
    """Container for all game sounds"""
    def __init__(self):
        self.enabled = True
        try:
            self.jump = generate_jump_sound()
            self.coin = generate_coin_sound()
            self.damage = generate_damage_sound()
            self.level_complete = generate_level_complete_sound()
            self.menu_select = generate_menu_select_sound()
            self.menu_move = generate_menu_move_sound()
            self.game_over = generate_game_over_sound()
        except Exception as e:
            print(f"Sound initialization failed: {e}")
            self.enabled = False
    
    def play(self, sound_name):
        if self.enabled and hasattr(self, sound_name):
            sound = getattr(self, sound_name)
            sound.play()


# Initialize sounds
sounds = Sounds()


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
        
        # Enhanced animation properties
        self.squash_stretch = 1.0  # 1.0 = normal, <1 = squash, >1 = stretch
        self.squash_velocity = 0  # For smooth squash animation
        self.landing_timer = 0  # Frames since landing
        self.idle_breath_timer = 0  # For breathing animation
        self.run_bob = 0  # Vertical bobbing while running
        
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
                    # Landing impact - trigger squash
                    if not was_on_ground:
                        self.squash_stretch = 0.7  # Squash on landing
                        self.landing_timer = 10
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
        
        # Update squash/stretch animation (spring back to normal)
        target_stretch = 1.0
        if self.state == "jump" and self.vel_y < -5:
            target_stretch = 1.2  # Stretch when jumping up
        elif self.state == "jump" and self.vel_y > 5:
            target_stretch = 0.85  # Slight squash when falling
        self.squash_stretch += (target_stretch - self.squash_stretch) * 0.2
        
        # Landing timer countdown
        if self.landing_timer > 0:
            self.landing_timer -= 1
        
        # Idle breathing animation
        self.idle_breath_timer += 0.08
        
        # Run bobbing
        if self.state == "run":
            self.run_bob = math.sin(self.animation_frame * math.pi / 2) * 2
        else:
            self.run_bob = 0
        
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
        sounds.play('jump')
    
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
            sounds.play('damage')
            if self.health < 0:
                self.health = 0
    
    def draw(self, screen, camera_x):
        screen_x = self.x - camera_x
        
        # Draw player with animation
        color = BLUE
        if self.invincible > 0 and self.invincible % 10 < 5:
            color = LIGHT_GRAY  # Flashing effect when invincible
        
        # Calculate squash/stretch dimensions
        stretch_y = self.squash_stretch
        stretch_x = 1.0 / stretch_y  # Inverse for volume preservation
        
        # Base position with run bob and breathing
        breath_offset = math.sin(self.idle_breath_timer) * 1.5 if self.state == "idle" else 0
        base_y = self.y + self.run_bob + breath_offset
        
        # Body dimensions with squash/stretch
        body_width = int(20 * stretch_x)
        body_height = int(25 * stretch_y)
        body_x = screen_x + 5 + (20 - body_width) // 2
        body_y = base_y + 10 + (25 - body_height)  # Anchor to bottom
        
        # Body
        body_rect = pygame.Rect(body_x, body_y, body_width, body_height)
        pygame.draw.rect(screen, color, body_rect, border_radius=5)
        
        # Head with squash/stretch
        head_size = int(8 * stretch_x)
        head_x = screen_x + 15
        head_y = base_y + 5 - (8 - head_size) + (1 - stretch_y) * 5
        pygame.draw.circle(screen, color, (int(head_x), int(head_y)), head_size)
        
        # Eyes (blink occasionally)
        eye_offset = 2 if self.facing_right else -2
        blink = (self.animation_timer == 0 and self.animation_frame == 0)
        if not blink:
            pygame.draw.circle(screen, WHITE, (int(head_x + eye_offset), int(head_y)), 2)
            # Pupil
            pygame.draw.circle(screen, BLACK, (int(head_x + eye_offset + (1 if self.facing_right else -1)), int(head_y)), 1)
        
        # Arms animation
        arm_y = base_y + 15
        if self.state == "run":
            arm_swing = math.sin(self.animation_frame * math.pi / 2) * 8
            pygame.draw.line(screen, color, (screen_x + 10, arm_y), 
                           (screen_x + 3, arm_y + 5 + arm_swing), 3)
            pygame.draw.line(screen, color, (screen_x + 20, arm_y), 
                           (screen_x + 27, arm_y + 5 - arm_swing), 3)
        elif self.state == "jump":
            # Arms up when jumping, down when falling
            arm_up = -8 if self.vel_y < 0 else 5
            pygame.draw.line(screen, color, (screen_x + 10, arm_y), 
                           (screen_x + 3, arm_y + arm_up), 3)
            pygame.draw.line(screen, color, (screen_x + 20, arm_y), 
                           (screen_x + 27, arm_y + arm_up), 3)
        else:
            # Idle arm sway
            idle_sway = math.sin(self.idle_breath_timer * 0.5) * 2
            pygame.draw.line(screen, color, (screen_x + 10, arm_y), 
                           (screen_x + 7, arm_y + 7 + idle_sway), 3)
            pygame.draw.line(screen, color, (screen_x + 20, arm_y), 
                           (screen_x + 23, arm_y + 7 - idle_sway), 3)
        
        # Legs animation
        leg_y = base_y + 35
        if self.state == "run":
            # More dynamic run cycle
            leg_phase = self.animation_frame * math.pi / 2
            leg1_swing = math.sin(leg_phase) * 8
            leg2_swing = math.sin(leg_phase + math.pi) * 8
            pygame.draw.line(screen, color, (screen_x + 12, leg_y), 
                           (screen_x + 8 + leg1_swing * 0.5, leg_y + 7 + abs(leg1_swing) * 0.3), 4)
            pygame.draw.line(screen, color, (screen_x + 18, leg_y), 
                           (screen_x + 22 + leg2_swing * 0.5, leg_y + 7 + abs(leg2_swing) * 0.3), 4)
        elif self.state == "jump":
            # Tucked legs when jumping up, extended when falling
            if self.vel_y < 0:
                pygame.draw.line(screen, color, (screen_x + 12, leg_y), 
                               (screen_x + 8, leg_y + 3), 4)
                pygame.draw.line(screen, color, (screen_x + 18, leg_y), 
                               (screen_x + 22, leg_y + 3), 4)
            else:
                pygame.draw.line(screen, color, (screen_x + 12, leg_y), 
                               (screen_x + 10, leg_y + 8), 4)
                pygame.draw.line(screen, color, (screen_x + 18, leg_y), 
                               (screen_x + 20, leg_y + 8), 4)
        else:
            # Idle stance
            pygame.draw.line(screen, color, (screen_x + 12, leg_y), 
                           (screen_x + 11, leg_y + 7), 4)
            pygame.draw.line(screen, color, (screen_x + 18, leg_y), 
                           (screen_x + 19, leg_y + 7), 4)
        
        # Landing dust particles (drawn by game class via landing_timer)


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
        self.sparkle_timer = random.uniform(0, math.pi * 2)  # Random start phase
        self.sparkles = []  # List of sparkle positions and timers
        
    def update(self):
        self.bob_offset = math.sin(self.rotation) * 5
        self.rotation += self.bob_speed
        self.sparkle_timer += 0.15
        
        # Generate sparkles occasionally
        if random.random() < 0.05 and not self.collected:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(5, 15)
            self.sparkles.append({
                'x': math.cos(angle) * dist,
                'y': math.sin(angle) * dist,
                'life': 20,
                'size': random.uniform(1, 3)
            })
        
        # Update sparkles
        for sparkle in self.sparkles[:]:
            sparkle['life'] -= 1
            sparkle['y'] -= 0.5  # Float upward
            if sparkle['life'] <= 0:
                self.sparkles.remove(sparkle)
        
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
            
            # Draw sparkles behind coin
            for sparkle in self.sparkles:
                sx = screen_x + 10 + sparkle['x']
                sy = y + 10 + sparkle['y']
                alpha = int((sparkle['life'] / 20) * 255)
                size = int(sparkle['size'] * (sparkle['life'] / 20))
                if size > 0:
                    # Draw sparkle as small star/cross
                    spark_color = (255, 255, 200, alpha)
                    s = pygame.Surface((size * 4, size * 4), pygame.SRCALPHA)
                    pygame.draw.line(s, spark_color, (size * 2, 0), (size * 2, size * 4), 1)
                    pygame.draw.line(s, spark_color, (0, size * 2), (size * 4, size * 2), 1)
                    screen.blit(s, (sx - size * 2, sy - size * 2))
            
            # Draw coin with rotation effect
            scale = abs(math.cos(self.rotation))
            width = int(self.width * scale)
            if width < 2:
                width = 2
            
            # Glow effect
            glow_size = 24 + math.sin(self.sparkle_timer) * 3
            glow_surf = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (255, 215, 0, 30), (int(glow_size), int(glow_size)), int(glow_size))
            screen.blit(glow_surf, (screen_x + 10 - glow_size, y + 10 - glow_size))
            
            # Outer circle
            pygame.draw.ellipse(screen, GOLD, (screen_x + (self.width - width) // 2, 
                                                y, width, self.height))
            # Inner circle
            if width > 8:
                pygame.draw.ellipse(screen, YELLOW, (screen_x + (self.width - width) // 2 + 3, 
                                                     y + 3, width - 6, self.height - 6))
            
            # Shine highlight
            if width > 6:
                shine_x = screen_x + (self.width - width) // 2 + 4
                pygame.draw.circle(screen, WHITE, (int(shine_x), int(y + 5)), 2)


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
        self.walk_cycle = 0  # For walking animation
        self.angry = False  # True when player is nearby
        self.angry_timer = 0
        self.squash = 1.0  # For squash animation when turning
        
        # Cache rect for performance
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
    def update(self, platforms, player_x=None):
        # Check if player is nearby for angry mode
        if player_x is not None:
            distance_to_player = abs(self.x - player_x)
            self.angry = distance_to_player < 150
            if self.angry:
                self.angry_timer += 1
            else:
                self.angry_timer = 0
        
        # Move back and forth
        old_direction = self.direction
        self.x += self.speed * self.direction
        
        # Turn around at patrol limits
        if self.x > self.start_x + self.patrol_distance:
            self.direction = -1
        elif self.x < self.start_x:
            self.direction = 1
        
        # Squash effect when turning
        if old_direction != self.direction:
            self.squash = 0.7
        self.squash += (1.0 - self.squash) * 0.2
        
        # Animation - walk cycle
        self.animation_frame += 1
        self.walk_cycle += 0.3
        
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
        
        # Walking bob
        walk_bob = abs(math.sin(self.walk_cycle)) * 3
        body_y = self.y - walk_bob
        
        # Squash/stretch effect
        body_width = int(self.width * (1 / self.squash))
        body_height = int(self.height * self.squash)
        body_x = screen_x + (self.width - body_width) // 2
        body_y_adjusted = body_y + (self.height - body_height)
        
        # Body color - redder when angry
        if self.angry:
            anger_pulse = math.sin(self.angry_timer * 0.3) * 0.5 + 0.5
            body_color = (220, int(50 - anger_pulse * 30), int(50 - anger_pulse * 30))
        else:
            body_color = RED
        
        # Body with squash
        pygame.draw.rect(screen, body_color, (body_x, body_y_adjusted, body_width, body_height), 
                        border_radius=5)
        
        # Eyes - angry when player is near
        eye_y = body_y_adjusted + 8
        eye_size = 4 if self.angry else 3
        
        if self.angry:
            # Angry eyes - slanted eyebrows, red glow
            # Left eye
            pygame.draw.circle(screen, YELLOW, (int(screen_x + 8), int(eye_y)), eye_size)
            pygame.draw.circle(screen, RED, (int(screen_x + 8), int(eye_y)), 2)  # Angry pupil
            # Right eye
            pygame.draw.circle(screen, YELLOW, (int(screen_x + 22), int(eye_y)), eye_size)
            pygame.draw.circle(screen, RED, (int(screen_x + 22), int(eye_y)), 2)  # Angry pupil
            # Angry eyebrows
            pygame.draw.line(screen, BLACK, (screen_x + 4, eye_y - 5), (screen_x + 12, eye_y - 2), 2)
            pygame.draw.line(screen, BLACK, (screen_x + 26, eye_y - 5), (screen_x + 18, eye_y - 2), 2)
        else:
            # Normal eyes with slight movement
            eye_offset = math.sin(self.animation_frame * 0.1) * 1.5
            pygame.draw.circle(screen, YELLOW, (int(screen_x + 10), int(eye_y + eye_offset)), eye_size)
            pygame.draw.circle(screen, YELLOW, (int(screen_x + 20), int(eye_y - eye_offset)), eye_size)
            # Pupils looking in movement direction
            pupil_offset = 1 if self.direction > 0 else -1
            pygame.draw.circle(screen, BLACK, (int(screen_x + 10 + pupil_offset), int(eye_y + eye_offset)), 1)
            pygame.draw.circle(screen, BLACK, (int(screen_x + 20 + pupil_offset), int(eye_y - eye_offset)), 1)
        
        # Spikes - animate up and down
        for i in range(3):
            spike_offset = math.sin(self.walk_cycle + i) * 2
            spike_x = screen_x + 5 + i * 10
            spike_y = body_y_adjusted - spike_offset
            points = [(spike_x, spike_y), (spike_x + 5, spike_y - 7), (spike_x + 10, spike_y)]
            pygame.draw.polygon(screen, ORANGE, points)
        
        # Feet animation
        foot_y = body_y_adjusted + body_height - 2
        foot_offset1 = math.sin(self.walk_cycle) * 4
        foot_offset2 = math.sin(self.walk_cycle + math.pi) * 4
        pygame.draw.ellipse(screen, (150, 40, 40), (screen_x + 3 + foot_offset1, foot_y, 8, 5))
        pygame.draw.ellipse(screen, (150, 40, 40), (screen_x + 19 + foot_offset2, foot_y, 8, 5))


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
        
        # UI Animation state
        self.score_popups = []  # List of {x, y, text, timer, color}
        self.health_shake = 0  # Shake intensity for health bar
        self.last_health = 100  # Track health changes
        
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
        self.score_popups = []
        self.health_shake = 0
        self.last_health = 100
        self.state = GameState.PLAYING
    
    def add_score_popup(self, x, y, text, color=GOLD):
        """Add a floating score popup"""
        self.score_popups.append({
            'x': x,
            'y': y,
            'text': text,
            'timer': 60,
            'color': color,
            'scale': 1.5  # Start bigger, shrink to normal
        })
    
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
                sounds.play('menu_move')
            elif event.key == pygame.K_DOWN:
                self.menu_selection = (self.menu_selection + 1) % len(self.menu_options)
                sounds.play('menu_move')
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                sounds.play('menu_select')
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
                sounds.play('coin')
                # Add score popup
                screen_x = coin.x - self.camera_x
                self.add_score_popup(screen_x, coin.y - 20, "+10", GOLD)
        
        # Update enemies
        for enemy in self.level.enemies:
            enemy.update(self.level.platforms, self.player.x)
            if enemy.check_collision(self.player):
                self.create_particles(self.player.x + 15, self.player.y + 20, RED, 10)
        
        # Check for health change (for UI shake)
        if self.player.health < self.last_health:
            self.health_shake = 15  # Start shake
            damage = self.last_health - self.player.health
            screen_x = self.player.x - self.camera_x
            self.add_score_popup(screen_x, self.player.y - 30, f"-{damage}", RED)
        self.last_health = self.player.health
        
        # Update health shake
        if self.health_shake > 0:
            self.health_shake -= 1
        
        # Update score popups
        for popup in self.score_popups:
            popup['timer'] -= 1
            popup['y'] -= 1.5  # Float upward
            popup['scale'] = max(1.0, popup['scale'] - 0.03)  # Shrink to normal
        self.score_popups = [p for p in self.score_popups if p['timer'] > 0]
        
        # Update particles (optimized - use list comprehension instead of remove in loop)
        for particle in self.particles:
            particle.update()
        self.particles = [p for p in self.particles if p.life > 0]
        
        # Create landing dust particles
        if self.player.landing_timer == 9:  # Just landed
            for _ in range(5):
                angle = random.uniform(math.pi * 0.6, math.pi * 0.9)
                speed = random.uniform(1, 3)
                velocity = (math.cos(angle) * speed * (1 if random.random() > 0.5 else -1), 
                           math.sin(angle) * speed * -0.5)
                self.particles.append(Particle(
                    self.player.x + 15, 
                    self.player.y + self.player.height - 5,
                    LIGHT_GRAY, velocity
                ))
        
        # Check win condition
        if self.player.x >= self.level.goal_x:
            all_coins_collected = all(coin.collected for coin in self.level.coins)
            if all_coins_collected:
                self.state = GameState.LEVEL_COMPLETE
                sounds.play('level_complete')
        
        # Check game over
        if self.player.health <= 0:
            self.state = GameState.GAME_OVER
            sounds.play('game_over')
    
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
        # Health bar with shake effect
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = 20
        
        # Apply shake offset
        shake_x = 0
        shake_y = 0
        if self.health_shake > 0:
            shake_x = random.randint(-3, 3)
            shake_y = random.randint(-2, 2)
        
        # Background
        pygame.draw.rect(self.screen, DARK_GRAY, (bar_x - 2 + shake_x, bar_y - 2 + shake_y, bar_width + 4, bar_height + 4))
        pygame.draw.rect(self.screen, BLACK, (bar_x + shake_x, bar_y + shake_y, bar_width, bar_height))
        
        # Health
        health_width = int((self.player.health / self.player.max_health) * bar_width)
        health_color = GREEN if self.player.health > 50 else (ORANGE if self.player.health > 25 else RED)
        
        # Pulse effect when low health
        if self.player.health <= 25:
            pulse = abs(math.sin(pygame.time.get_ticks() * 0.005)) * 0.3 + 0.7
            health_color = (int(health_color[0] * pulse), int(health_color[1] * pulse), int(health_color[2] * pulse))
        
        pygame.draw.rect(self.screen, health_color, (bar_x + shake_x, bar_y + shake_y, health_width, bar_height))
        
        # Health text
        health_text = self.small_font.render(f"Health: {self.player.health}/{self.player.max_health}", 
                                             True, WHITE)
        self.screen.blit(health_text, (bar_x + 5 + shake_x, bar_y + 1 + shake_y))
        
        # Score with animated display
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
        
        # Draw score popups
        for popup in self.score_popups:
            alpha = int((popup['timer'] / 60) * 255)
            font_size = int(24 * popup['scale'])
            popup_font = pygame.font.Font(None, font_size)
            
            # Create text with alpha
            text_surface = popup_font.render(popup['text'], True, popup['color'])
            text_surface.set_alpha(alpha)
            
            # Center the text on popup position
            text_rect = text_surface.get_rect(center=(popup['x'], popup['y']))
            self.screen.blit(text_surface, text_rect)
        
        # Instructions
        if self.player.x < 300:  # Show at start
            hint = self.small_font.render("Arrow Keys to move, Space to jump, P to pause", True, WHITE)
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
