import pygame
from asset_manager import GAME_ASSETS # Import GAME_ASSETS
from bullets import Bullet # Import Bullet class

class Player:
    def __init__(self, x, y):
        self.idle_sprite = GAME_ASSETS['reimu_idle']
        self.moving_sprites = GAME_ASSETS['reimu_moving']
        self.image = self.idle_sprite # Default
        
        # Load shooting sprites with fallback
        self.shooting_normal_sprite = GAME_ASSETS.get('reimu_shooting_normal', self.idle_sprite)
        self.shooting_focused_sprite = GAME_ASSETS.get('reimu_shooting_focused', self.idle_sprite)
        
        self.rect = self.image.get_rect(topleft=(x, y))
        
        self.speed = 5
        self.hitbox_radius = 5
        
        self.is_moving = False
        self.animation_index = 0
        self.animation_timer = 0
        self.animation_speed = 10 # Change frame every 10 game loops

        self.bullets = []
        self.shoot_cooldown = 10 # Frames
        self.time_since_last_shot = 0 # Frames
        
        # Load bullet images from GAME_ASSETS
        self.needle_bullet_image = GAME_ASSETS['bullet_reimu_needle']
        self.homing_amulet_image = GAME_ASSETS['bullet_reimu_homing_amulet']

        # Shooting visual state
        self.show_shooting_sprite_timer = 0
        self.show_shooting_sprite_duration = 5 # Frames

        # Invincibility
        self.is_invincible = False
        self.invincibility_timer = 0
        self.invincibility_duration = 120  # Frames, e.g., 2 seconds
        self.blink_toggle_interval = 10  # Frames, for blinking effect
        
        # Power
        self.power_level = 0
        self.max_power_level = 128


    def update(self, pressed_keys, screen_width, screen_height):
        self.is_moving = False # Reset at the beginning of update
        dx, dy = 0, 0

        # Movement
        if pressed_keys[pygame.K_UP]:
            dy -= self.speed
        if pressed_keys[pygame.K_DOWN]:
            dy += self.speed
        if pressed_keys[pygame.K_LEFT]:
            dx -= self.speed
        if pressed_keys[pygame.K_RIGHT]:
            dx += self.speed

        if dx != 0 or dy != 0:
            self.is_moving = True
            # Normalize diagonal movement
            if dx != 0 and dy != 0:
                dx *= 0.7071
                dy *= 0.7071
        
        self.rect.x += dx
        self.rect.y += dy

        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > screen_width:
            self.rect.right = screen_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > screen_height:
            self.rect.bottom = screen_height

        # Handle animation
        if self.is_moving:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_index = (self.animation_index + 1) % len(self.moving_sprites)
                self.image = self.moving_sprites[self.animation_index]
        else:
            self.image = self.idle_sprite
            self.animation_index = 0 # Reset animation
        
        # Shooting logic
        self.time_since_last_shot += 1
        is_shooting_key_pressed = pressed_keys[pygame.K_z] # Renamed to avoid conflict
        is_focused = pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]

        if is_shooting_key_pressed:
            if not is_focused and self.time_since_last_shot >= self.shoot_cooldown:
                self._fire_needle_shot()
                self.time_since_last_shot = 0
                self.show_shooting_sprite_timer = self.show_shooting_sprite_duration # Show shooting sprite
            elif is_focused and self.time_since_last_shot >= self.shoot_cooldown:
                self._fire_homing_shot()
                self.time_since_last_shot = 0
                self.show_shooting_sprite_timer = self.show_shooting_sprite_duration # Show shooting sprite
        
        # Bullet management
        for bullet in self.bullets[:]: # Iterate over a copy for safe removal
            bullet.update()
            if bullet.is_offscreen(screen_width, screen_height):
                self.bullets.remove(bullet)
        
        # Shooting Visual Timer Update
        if self.show_shooting_sprite_timer > 0:
            self.show_shooting_sprite_timer -= 1

        # Sprite Selection Logic
        # is_focused is already determined above
        if self.show_shooting_sprite_timer > 0:
            if is_focused:
                self.image = self.shooting_focused_sprite
            else:
                self.image = self.shooting_normal_sprite
        elif self.is_moving: # Check self.is_moving (set during movement input handling)
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_index = (self.animation_index + 1) % len(self.moving_sprites)
                self.image = self.moving_sprites[self.animation_index]
        else:
            self.image = self.idle_sprite
            self.animation_index = 0 # Reset animation when idle

        # Invincibility timer update
        if self.is_invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.is_invincible = False


    def _fire_needle_shot(self):
        bullet_speed_y = -10
        base_offset_x = 10
        bullets_to_fire = []
        # Central shots
        bullets_to_fire.append(Bullet(self.rect.centerx - base_offset_x, self.rect.top, 0, bullet_speed_y, self.needle_bullet_image))
        bullets_to_fire.append(Bullet(self.rect.centerx + base_offset_x, self.rect.top, 0, bullet_speed_y, self.needle_bullet_image))
        # Power-based additional shots
        if self.power_level >= 64:
            # Outer shots (wider spread)
            bullets_to_fire.append(Bullet(self.rect.centerx - base_offset_x * 2.5, self.rect.top, 0, bullet_speed_y, self.needle_bullet_image))
            bullets_to_fire.append(Bullet(self.rect.centerx + base_offset_x * 2.5, self.rect.top, 0, bullet_speed_y, self.needle_bullet_image))
        self.bullets.extend(bullets_to_fire)

    def _fire_homing_shot(self):
        bullet_speed_y = -7
        base_spread_dx = 1
        spawn_y = self.rect.top
        bullets_to_fire = []
        # Central homing shots (slight spread)
        bullets_to_fire.append(Bullet(self.rect.centerx - 5, spawn_y, -base_spread_dx, bullet_speed_y, self.homing_amulet_image))
        bullets_to_fire.append(Bullet(self.rect.centerx + 5, spawn_y, base_spread_dx, bullet_speed_y, self.homing_amulet_image))
        # Power-based additional homing shots
        if self.power_level >= 64:
            # Wider spread homing shots
            bullets_to_fire.append(Bullet(self.rect.centerx - 15, spawn_y, -base_spread_dx * 1.5, bullet_speed_y, self.homing_amulet_image))
            bullets_to_fire.append(Bullet(self.rect.centerx + 15, spawn_y, base_spread_dx * 1.5, bullet_speed_y, self.homing_amulet_image))
        self.bullets.extend(bullets_to_fire)

    def draw(self, surface, show_hitbox):
        # Blink effect: only draw if the timer is in a certain phase
        if self.is_invincible:
            if self.invincibility_timer % self.blink_toggle_interval < (self.blink_toggle_interval / 2):
                return  # Skip drawing the player to make it blink

        surface.blit(self.image, self.rect) # Draw the player sprite
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(surface)
            
        if show_hitbox:
            center_x = self.rect.centerx
            center_y = self.rect.centery
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), self.hitbox_radius)

    def handle_hit(self):
        if not self.is_invincible:
            self.is_invincible = True
            self.invincibility_timer = self.invincibility_duration
            return True # Hit was processed
        return False # Was already invincible

    def reset_position(self, x, y):
        self.rect.topleft = (x,y)
        self.image = self.idle_sprite # Reset to idle state
        self.animation_index = 0
        self.is_moving = False # Reset movement state

    def increase_power(self, amount=1):
        self.power_level = min(self.power_level + amount, self.max_power_level)
        print(f"Power level: {self.power_level}")
