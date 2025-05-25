import pygame

class Enemy:
    def __init__(self, x, y, health, image_surface):
        """
        Initializes a base enemy object.
        :param x: The initial x-coordinate of the enemy's center.
        :param y: The initial y-coordinate of the enemy's center.
        :param health: The initial health of the enemy.
        :param image_surface: The pygame.Surface object representing the enemy's image.
        """
        self.image = image_surface
        self.rect = self.image.get_rect(center=(x, y))
        self.health = health

    def update(self):
        """
        Updates the enemy's position or state.
        Default behavior: move straight down slowly.
        """
        self.rect.y += 1 # Basic default movement

    def draw(self, surface):
        """
        Draws the enemy on the given surface.
        :param surface: The pygame.Surface to draw the enemy on.
        """
        surface.blit(self.image, self.rect)

    def take_damage(self, amount):
        """
        Decrements the enemy's health by the given amount.
        :param amount: The amount of damage to inflict.
        :return: True if health is depleted (<= 0), False otherwise.
        """
        self.health -= amount
        return self.health <= 0

    def is_offscreen(self, screen_width, screen_height):
        """
        Checks if the enemy is off the bottom of the screen.
        More comprehensive checks can be added if enemies move in other directions.
        :param screen_width: The width of the game screen.
        :param screen_height: The height of the game screen.
        :return: True if the enemy is offscreen, False otherwise.
        """
        return self.rect.top > screen_height # Simple check for enemies moving downwards
        # A more comprehensive check:
        # return (self.rect.bottom < 0 or
        #         self.rect.top > screen_height or
        #         self.rect.right < 0 or
        #         self.rect.left > screen_width)

import math # For potential future use with sine wave
import random # For staggering shots
from .bullets import Bullet # Import Bullet class


class ZakoEnemy(Enemy):
    def __init__(self, x, y, health, image_surface, movement_pattern="straight_down", speed=2):
        """
        Initializes a Zako (basic) enemy.
        :param x: Initial x-coordinate.
        :param y: Initial y-coordinate.
        :param health: Enemy health.
        :param image_surface: Pygame surface for the enemy's image.
        :param movement_pattern: String defining the movement type (e.g., "straight_down").
        :param speed: Movement speed.
        """
        super().__init__(x, y, health, image_surface)
        self.movement_pattern = movement_pattern
        self.speed = speed
        # self.spawn_x = x 
        # self.frames_alive = 0 

        self.shoot_cooldown = 180  # Fire every 3 seconds
        self.time_since_last_shot = random.randint(0, self.shoot_cooldown) # Random initial delay
        
        self.enemy_bullet_surface = pygame.Surface((10, 10)) # Slightly larger than needle
        self.enemy_bullet_surface.fill((255, 255, 0))  # Yellow
        
        self.fired_bullets_cache = [] # To store bullets fired in current frame


    def update(self):
        """
        Updates the ZakoEnemy's position based on its movement pattern and handles shooting.
        """
        # Movement logic (as before)
        if self.movement_pattern == "straight_down":
            self.rect.y += self.speed
        # elif self.movement_pattern == "sine_wave_down":
        #     self.rect.y += self.speed
        #     self.rect.x = self.spawn_x + math.sin(self.frames_alive / 20) * 30
        #     self.frames_alive += 1
        else:
            self.rect.y += self.speed
            
        # Base Enemy.update() is currently just self.rect.y += 1, so not calling super().update()
        # to avoid double movement if Zako has specific movement. If base Enemy.update()
        # had other important logic (e.g. status effects), we might call it.

        # Shooting logic
        self.fired_bullets_cache.clear()
        self.time_since_last_shot += 1
        if self.time_since_last_shot >= self.shoot_cooldown:
            self._fire_bullet()
            self.time_since_last_shot = 0

    def _fire_bullet(self):
        """
        Fires a single bullet downwards from the enemy's bottom center.
        """
        bullet_speed_y = 3  # Slower than player bullets
        spawn_x = self.rect.centerx
        spawn_y = self.rect.bottom
        
        new_bullet = Bullet(spawn_x, spawn_y, 0, bullet_speed_y, self.enemy_bullet_surface)
        self.fired_bullets_cache.append(new_bullet)

class ReisenBoss(Enemy):
    def __init__(self, x, y, health, image_surface, screen_width, screen_height):
        super().__init__(x, y, health, image_surface)
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = "entering"
        self.max_health = health  # Store for health bar
        self.target_y = 100
        self.entry_speed = 2
        self.movement_speed_x = 2
        self.movement_direction = 1
        self.fired_bullets_cache = []

        # Non-spell attack attributes
        self.non_spell_attack_cooldown = 75
        self.time_since_last_non_spell_attack = 0
        self.non_spell_pattern_index = 0 # New attribute
        
        # Spell Card attributes
        self.non_spell_duration = 600  # 10 seconds
        self.active_state_timer = 0
        self.current_spell_card_name = "Illusionary Blast (Placeholder)"
        self.spell_card_intro_duration = 60  # 1 second
        self.spell_card_active_duration = 900  # 15 seconds
        self.spell_card_attack_cooldown = 90  # 1.5 seconds between bursts
        self.time_since_last_spell_attack = 0
        self.spell_state_timer = 0  # Generic timer for intro/active phases of spell

        # Ensure a bullet surface is available (can be shared or specific)
        if not hasattr(self, 'enemy_bullet_surface'):
            self.enemy_bullet_surface = pygame.Surface((10, 10))
            self.enemy_bullet_surface.fill((255, 0, 255)) # Default magenta if not set by Zako
        self.spell_bullet_surface = self.enemy_bullet_surface # For this spell, use the same surface


    def update(self, player_x=None, player_y=None): # Modified signature
        self.fired_bullets_cache.clear()
        if self.state == "entering":
            self.rect.y += self.entry_speed
            if self.rect.centery >= self.target_y:
                self.rect.centery = self.target_y
                self.state = "active"
                self.active_state_timer = 0 # Start non-spell timer
                self.time_since_last_non_spell_attack = 0 # Initialize for active state
        elif self.state == "active":
            # Basic side-to-side movement
            self.rect.x += self.movement_speed_x * self.movement_direction
            if self.rect.left <= 0 or self.rect.right >= self.screen_width:
                self.movement_direction *= -1
                self.rect.x += self.movement_speed_x * self.movement_direction
            
            # Non-spell attack logic
            self.time_since_last_non_spell_attack += 1
            if self.time_since_last_non_spell_attack >= self.non_spell_attack_cooldown:
                if player_x is not None and player_y is not None: # Ensure player coords are available
                    if self.non_spell_pattern_index == 0:
                        self._fire_non_spell_pattern_1(player_x, player_y)
                    else: # Index is 1
                        self._fire_non_spell_pattern_2(player_x, player_y) # player_x, player_y might not be used by pattern 2
                
                self.time_since_last_non_spell_attack = 0
                self.non_spell_pattern_index = (self.non_spell_pattern_index + 1) % 2 # Alternate between 0 and 1

            # Spell card transition logic
            self.active_state_timer += 1 # This timer still tracks duration of non-spell phase
            if self.active_state_timer >= self.non_spell_duration:
                self.state = "spell_card_intro"
                self.active_state_timer = 0 # Reset for next non-spell phase
                self.spell_state_timer = 0 # Reset for intro
                print(f"Boss starting spell: {self.current_spell_card_name}")
        
        elif self.state == "spell_card_intro":
            self.spell_state_timer += 1
            if self.spell_state_timer >= self.spell_card_intro_duration:
                self.state = "spell_card_active"
                self.spell_state_timer = 0 # Reset for active duration
                self.time_since_last_spell_attack = 0 # Start firing immediately or with short delay
        
        elif self.state == "spell_card_active":
            # Movement (can be same or different for spell card)
            self.rect.x += self.movement_speed_x * self.movement_direction
            if self.rect.left <= 0 or self.rect.right >= self.screen_width:
                self.movement_direction *= -1
                self.rect.x += self.movement_speed_x * self.movement_direction
            
            self.spell_state_timer += 1
            self.time_since_last_spell_attack += 1
            
            if self.time_since_last_spell_attack >= self.spell_card_attack_cooldown:
                self._fire_spell_card_pattern()
                self.time_since_last_spell_attack = 0
                
            if self.spell_state_timer >= self.spell_card_active_duration:
                self.state = "active" # Transition back to normal active state
                self.spell_state_timer = 0
                self.active_state_timer = 0 # Reset non-spell timer
                print(f"Boss finished spell: {self.current_spell_card_name}")

        elif self.state == "defeating":
            # Placeholder for defeat effects
            pass

    def _fire_spell_card_pattern(self):
        num_bullets = 12
        angle_step = 360 / num_bullets
        bullet_speed = 3
        bullet_surf = getattr(self, 'spell_bullet_surface', self.enemy_bullet_surface)

        for i in range(num_bullets):
            angle = math.radians(i * angle_step)
            dx = math.cos(angle) * bullet_speed
            dy = math.sin(angle) * bullet_speed
            self.fired_bullets_cache.append(Bullet(self.rect.centerx, self.rect.centery, dx, dy, bullet_surf))

    def _fire_non_spell_pattern_1(self, player_x, player_y):
        bullet_speed = 4
        num_bullets_in_spread = 3
        spread_angle_deg = 20  # Total angle for the spread in degrees
        bullet_surf = getattr(self, 'spell_bullet_surface', self.enemy_bullet_surface)

        angle_to_player = math.atan2(player_y - self.rect.centery, player_x - self.rect.centerx)

        if num_bullets_in_spread == 1:
            start_angle_rad = angle_to_player
            angle_offset_step_rad = 0
        else:
            spread_angle_rad = math.radians(spread_angle_deg)
            start_angle_rad = angle_to_player - spread_angle_rad / 2
            angle_offset_step_rad = spread_angle_rad / (num_bullets_in_spread - 1)

        for i in range(num_bullets_in_spread):
            current_angle_rad = start_angle_rad + i * angle_offset_step_rad
            dx = math.cos(current_angle_rad) * bullet_speed
            dy = math.sin(current_angle_rad) * bullet_speed
            self.fired_bullets_cache.append(Bullet(self.rect.centerx, self.rect.centery, dx, dy, bullet_surf))

    def _fire_non_spell_pattern_2(self, player_x, player_y): # player_x, player_y might not be used
        bullet_speed = 3.5
        bullet_surf = getattr(self, 'spell_bullet_surface', self.enemy_bullet_surface)
        # Pattern: Two streams of bullets at fixed downward angles
        fixed_angles_deg = [-75, -105] # Angles relative to positive X-axis (0 deg right, -90 deg down)
                                        # So, -75 is slightly right-down, -105 is slightly left-down

        spawn_x_offset = 20 # Offset from boss center to spawn bullets
        spawn_y_abs = self.rect.centery + self.rect.height // 4

        for i in range(2): # Fire two bullets, one for each stream
            angle_rad = math.radians(fixed_angles_deg[i])
            dx = math.cos(angle_rad) * bullet_speed
            dy = math.sin(angle_rad) * bullet_speed
            # Spawn bullets from slightly different positions for visual clarity
            current_spawn_x = self.rect.centerx + (spawn_x_offset if i == 0 else -spawn_x_offset)
            self.fired_bullets_cache.append(Bullet(current_spawn_x, spawn_y_abs, dx, dy, bullet_surf))

    def draw_health_bar(self, surface):
        bar_margin_x = 100
        bar_margin_y = 20
        bar_width = self.screen_width - (2 * bar_margin_x)
        bar_height = 20
        bg_color = (50, 50, 50)  # Dark gray
        fg_color = (255, 0, 0)  # Red
        
        health_ratio = 0
        if self.max_health > 0 : # Avoid division by zero if max_health is somehow 0
             health_ratio = max(0, self.health / self.max_health)

        bg_rect = pygame.Rect(bar_margin_x, bar_margin_y, bar_width, bar_height)
        fg_width = bar_width * health_ratio
        fg_rect = pygame.Rect(bar_margin_x, bar_margin_y, fg_width, bar_height)
        
        pygame.draw.rect(surface, bg_color, bg_rect)
        pygame.draw.rect(surface, fg_color, fg_rect)
        # Optional: Draw boss name or health value as text
