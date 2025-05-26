import pygame

# Screen dimensions (consider moving to a config file later)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Player colors
PLAYER_COLOR = (255, 0, 0)  # Fallback color if image fails
HITBOX_COLOR = (255, 255, 0) # Yellow for hitbox indicator
BULLET_COLOR = (255, 255, 255) # Fallback bullet color

class Player(pygame.sprite.Sprite):
    def __init__(self, asset_manager):
        super().__init__()
        self.asset_manager = asset_manager
        self.image = self.asset_manager.get_image("player_sprite", scale_to=(40, 48)) # Example size
        if not self.image: # Fallback if asset loading failed
            self.image = pygame.Surface([30, 30])
            self.image.fill(PLAYER_COLOR)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 30

        # Game attributes
        self.lives = 3
        self.bombs = 2
        self.power = 0
        self.score = 0
        self.graze = 0
        self.max_power = 128 # Example max power

        self.speed_normal = 5
        self.speed_focused = 2
        self.current_speed = self.speed_normal
        self.is_focused = False

        self.hitbox_radius = 3
        self.show_hitbox = False # Controlled by focus

        self.bullets = pygame.sprite.Group()
        self.shoot_delay = 100 # milliseconds
        self.last_shot_time = pygame.time.get_ticks()

        self.spell_card_cooldown = 3000 # 3 seconds
        self.last_spell_card_time = -self.spell_card_cooldown 
        self.trigger_screen_flash = False # Already present, ensure it's initialized

    def update(self, keys):
        self.handle_input(keys)
        self.rect.clamp_ip(screen.get_rect()) # Keep player on screen
        self.bullets.update() # Update bullet positions

    def handle_input(self, keys):
        # Movement
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx -= 1
        if keys[pygame.K_RIGHT]:
            dx += 1
        if keys[pygame.K_UP]:
            dy -= 1
        if keys[pygame.K_DOWN]:
            dy += 1

        # Normalize diagonal movement
        if dx != 0 and dy != 0:
            dx /= 1.414 # sqrt(2)
            dy /= 1.414 # sqrt(2)

        # Focused mode
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.current_speed = self.speed_focused
            self.is_focused = True
            self.show_hitbox = True
        else:
            self.current_speed = self.speed_normal
            self.is_focused = False
            self.show_hitbox = False

        self.rect.x += dx * self.current_speed
        self.rect.y += dy * self.current_speed
        
        # Keep player within bounds (already handled by clamp_ip, but good to be explicit)
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT


        # Attack
        if keys[pygame.K_z]: # 'Z' key for shooting
            self.shoot()

        # Spell Card (Bomb)
        if keys[pygame.K_x]: # 'X' key for spell card
            self.activate_spell_card()

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = current_time
            if self.is_focused:
                # Wide-range homing shot (simplified as a cone)
                for angle in [-30, -15, 0, 15, 30]: # 5 bullets in a cone
                    bullet = Bullet(self.rect.centerx, self.rect.top, self.asset_manager, angle, is_focused=True)
                    self.bullets.add(bullet)
            else:
                # Forward-concentrated shot (needles)
                bullet1 = Bullet(self.rect.centerx - 5, self.rect.top, self.asset_manager, 0, is_focused=False) # Slightly offset
                bullet2 = Bullet(self.rect.centerx + 5, self.rect.top, self.asset_manager, 0, is_focused=False)
                self.bullets.add(bullet1)
                self.bullets.add(bullet2)
    
    def activate_spell_card(self):
        current_time = pygame.time.get_ticks()
        if self.bombs > 0 and current_time - self.last_spell_card_time > self.spell_card_cooldown:
            self.last_spell_card_time = current_time
            self.bombs -= 1
            print(f"Fantasy Seal activated! Bombs left: {self.bombs}") 
            self.trigger_screen_flash = True 
            # Future: Could also clear bullets, make player invincible for a short time
            return True # Spell card used
        return False # Spell card not used

    def add_power(self, amount=1):
        self.power = min(self.power + amount, self.max_power)
        print(f"Power: {self.power}/{self.max_power}")

    def add_score(self, amount=100):
        self.score += amount
        # print(f"Score: {self.score}") # Can be too noisy, UI will show it

    def increment_graze(self):
        self.graze += 1
        # print(f"Graze: {self.graze}") # Can be too noisy

    def is_alive(self): # For main game loop to check Game Over condition
        return self.lives > 0

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        if self.show_hitbox:
            pygame.draw.circle(surface, HITBOX_COLOR, self.rect.center, self.hitbox_radius)
        self.bullets.draw(surface)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, asset_manager, angle=0, is_focused=False): # Angle in degrees, 0 is straight up
        super().__init__()
        self.asset_manager = asset_manager
        if is_focused:
            self.image = self.asset_manager.get_image("player_bullet_focused", scale_to=(8,16)) # Example size
        else:
            self.image = self.asset_manager.get_image("player_bullet_needle", scale_to=(6,12)) # Example size

        if not self.image: # Fallback
            self.image = pygame.Surface([4, 10])
            self.image.fill(BULLET_COLOR)
            
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed = 10
        
        # Convert angle to radians for math.sin/cos
        rad_angle = pygame.math.Vector2(0, -self.speed).rotate(-angle) # Rotate (0, -speed) vector
        self.velocity_x = rad_angle.x
        self.velocity_y = rad_angle.y


    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT or \
           self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.kill() # Remove bullet if it goes off-screen

# Need to define `screen` for clamp_ip. This is a bit of a hack.
# Ideally, screen dimensions should be passed or accessed globally.
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
