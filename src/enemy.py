import pygame
import random
from src.items import create_item, Item # For item drops

# Screen dimensions (consider moving to a config file later)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Enemy Colors (placeholders)
ZAKO_COLOR = (0, 0, 255)  # Blue for Zako
ENEMY_BULLET_COLOR = (255, 255, 0) # Fallback color

class BaseEnemy(pygame.sprite.Sprite):
    def __init__(self, position, health, asset_manager, sprite_key=None, sprite_size=(30,30), fallback_color=(100,100,100)):
        super().__init__()
        self.asset_manager = asset_manager
        if sprite_key:
            self.image = self.asset_manager.get_image(sprite_key, scale_to=sprite_size)
        else: # Fallback if no sprite_key provided (should ideally not happen for specific enemies)
            self.image = None 
            
        if not self.image:
            self.image = pygame.Surface(sprite_size)
            self.image.fill(fallback_color)
            
        self.rect = self.image.get_rect(center=position)
        self.health = health
        self.initial_health = health # For health bar consistency
        self.bullets = pygame.sprite.Group()

    def update(self):
        # Basic update logic (e.g., movement) to be implemented by subclasses
        self.bullets.update() # Update enemy bullets
        if self.health <= 0:
            self.die()

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.bullets.draw(surface)

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.die()
            return True # Indicates enemy was defeated
        return False # Indicates enemy is still alive

    def die(self):
        # Called when health reaches 0. Can be overridden for death animations/sounds.
        # For now, just removes the enemy. Item drops will be handled by ZakoEnemy.
        self.kill() # Removes sprite from all groups it's in

    def check_collision_with_bullets(self, player_bullets_group):
        # This method is a bit redundant if using pygame.sprite.groupcollide
        # but can be useful for specific logic per enemy.
        # For now, let groupcollide handle it in main.py
        pass


class ZakoEnemy(BaseEnemy):
    def __init__(self, position, asset_manager):
        super().__init__(position, health=3, asset_manager=asset_manager, 
                         sprite_key="enemy_zako", sprite_size=(32,32), fallback_color=ZAKO_COLOR)
        self.speed_y = 2 # Moves downwards
        self.shoot_delay = 1500 # milliseconds (1.5 seconds)
        self.last_shot_time = pygame.time.get_ticks() + random.randint(0, self.shoot_delay) # Randomize first shot

    def update(self):
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT: # Remove if it goes off screen
            self.kill()

        # Shooting
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot_time > self.shoot_delay:
            self.last_shot_time = current_time
            self.shoot()
        
        super().update() # Handles bullet updates and checks for death

    def shoot(self):
        # Simple downward shot
        bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, self.asset_manager)
        self.bullets.add(bullet)
        # Add this bullet to a global enemy bullet group in main.py for collision checks

    def die(self): # Override to handle item drops
        # Item drop logic
        drop_chance = 0.6 # 60% chance to drop any item
        if random.random() < drop_chance:
            # Determine item type (can be more sophisticated)
            item_type = random.choice(['score', 'power', 'bomb'])
            # The actual Item object needs to be created and added to a group in main.py
            # We can return the type and position for main.py to handle.
            self.dropped_item_info = {'type': item_type, 'position': self.rect.center}
        else:
            self.dropped_item_info = None
        
        super().die() # Calls self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, asset_manager, speed_x=0, speed_y=5, 
                 asset_key="enemy_bullet_default", sprite_size=(10,10), fallback_color=ENEMY_BULLET_COLOR):
        super().__init__()
        self.asset_manager = asset_manager
        self.image = self.asset_manager.get_image(asset_key, scale_to=sprite_size)
        self.grazed_by_player = False # For graze system
        
        if not self.image: # Fallback
            self.image = pygame.Surface(sprite_size)
            self.image.fill(fallback_color)
            # pygame.draw.circle(self.image, fallback_color, (sprite_size[0]//2, sprite_size[1]//2), sprite_size[0]//2)
            # self.image.set_colorkey((0,0,0)) # If using a square surf for circle and want transparency
            
        self.rect = self.image.get_rect(center=(x,y))
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0 or \
           self.rect.left > SCREEN_WIDTH or self.rect.right < 0:
            self.kill()

REISEN_COLOR = (128, 0, 128) # Fallback Purple for Reisen
REISEN_BULLET_COLOR = (255, 105, 180) # Fallback Hot Pink for Reisen's bullets

class Reisen(BaseEnemy):
    def __init__(self, position, asset_manager): # Expect asset_manager
        super().__init__(position, health=100, asset_manager=asset_manager,
                         sprite_key="enemy_reisen", sprite_size=(60,80), fallback_color=REISEN_COLOR)
        
        self.initial_entry_target_y = position[1]
        # self.rect.bottom = 0 # This is handled in BaseEnemy if sprite size is known, or re-adjust if needed
        if self.image: # Adjust if sprite loaded correctly
             self.rect = self.image.get_rect(center=position) # Recenter based on actual image
        self.rect.bottom = 0 # Start off screen from top, override initial centering if needed for entry
        self.entry_speed = 2

        self.is_active = False # Becomes true after entry animation
        
        self.spell_card_active = False
        self.spell_card_name = "Illusionary Blast" # Example name
        self.spell_card_duration = 15000 # 15 seconds
        self.spell_card_start_time = 0
        self.spell_card_health_threshold = self.health / 2 # Health at which spell card triggers
        self.spell_card_bonus_value = 50000 # Score bonus for clearing this spell
        self.spell_card_bonus_achieved = False # Flag to indicate bonus should be awarded

        self.current_pattern = 0
        self.pattern_timer = 0
        self.pattern_switch_delay = 5000 # Switch pattern every 5 seconds (non-spell)
        self.shoot_timer = 0
        self.shoot_delay_wave = 1000 # 1 second for wave
        self.shoot_delay_burst = 2000 # 2 seconds for targeted burst
        self.shoot_delay_spell = 200 # 0.2 seconds for spell card rings

        self.target_player_pos = (0,0) # For targeted burst

    def update(self, player_pos=None): # player_pos needed for targeted shots
        if not self.is_active:
            self.rect.y += self.entry_speed
            if self.rect.centery >= self.initial_entry_target_y:
                self.rect.centery = self.initial_entry_target_y
                self.is_active = True
                self.pattern_timer = pygame.time.get_ticks()
                self.shoot_timer = pygame.time.get_ticks()
            return # Don't do anything else until entry is complete

        current_time = pygame.time.get_ticks()

        # Spell Card Logic
        if self.health <= self.spell_card_health_threshold and not self.spell_card_active and self.health > 0: # Only trigger if alive
            self.spell_card_active = True
            self.spell_card_start_time = current_time
            self.spell_card_bonus_achieved = False # Reset bonus achieved flag for new activation
            print(f"Spell Card Activated: {self.spell_card_name}")
            self.shoot_timer = current_time 
        
        if self.spell_card_active:
            if current_time - self.spell_card_start_time > self.spell_card_duration or self.health <= 0:
                if self.health > 0 : # Survived the duration
                    self.spell_card_bonus_achieved = True
                    print(f"Spell Card '{self.spell_card_name}' bonus achieved (duration)!")
                # If health <= 0, bonus is handled by die() or main game logic checking health during spell
                self.spell_card_active = False 
                self.pattern_timer = current_time 
            else:
                if current_time - self.shoot_timer > self.shoot_delay_spell:
                    self.shoot_timer = current_time
                    self.shoot_spell_pattern()
        else: # Normal patterns
            if current_time - self.pattern_timer > self.pattern_switch_delay:
                self.pattern_timer = current_time
                self.current_pattern = (self.current_pattern + 1) % 2 # Cycle between 2 patterns
                self.shoot_timer = current_time # Reset shoot timer for new pattern

            if self.current_pattern == 0: # Wave Shot
                if current_time - self.shoot_timer > self.shoot_delay_wave:
                    self.shoot_timer = current_time
                    self.shoot_wave_pattern()
            elif self.current_pattern == 1: # Targeted Burst
                if player_pos: self.target_player_pos = player_pos
                if current_time - self.shoot_timer > self.shoot_delay_burst:
                    self.shoot_timer = current_time
                    self.shoot_targeted_burst(self.target_player_pos)
        
        super().update() # Handles bullet updates and checks for death

    def shoot_wave_pattern(self):
        num_bullets = 7
        spread_angle = 90 # degrees
        angle_step = spread_angle / (num_bullets -1) if num_bullets > 1 else 0
        start_angle = -spread_angle / 2

        for i in range(num_bullets):
            angle = start_angle + i * angle_step
            vec = pygame.math.Vector2(0, 1).rotate(angle) # Base vector pointing down, rotated
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery, self.asset_manager, vec.x * 3, vec.y * 3, 
                                 asset_key="reisen_bullet", sprite_size=(12,12), fallback_color=REISEN_BULLET_COLOR)
            self.bullets.add(bullet)

    def shoot_targeted_burst(self, player_pos):
        num_bullets = 5
        burst_radius = 10 # How far from initial target bullets spread
        
        direction = pygame.math.Vector2(player_pos) - pygame.math.Vector2(self.rect.center)
        if direction.length() == 0: # Avoid division by zero if player is exactly on Reisen
            direction = pygame.math.Vector2(0,1) # Default to shooting down
        direction = direction.normalize()

        for i in range(num_bullets):
            # Simple spread for now, can be more complex
            offset = pygame.math.Vector2(random.uniform(-burst_radius, burst_radius), random.uniform(-burst_radius, burst_radius))
            bullet_dir = direction + offset.normalize() * 0.2 # Slight random perturbation
            bullet_dir = bullet_dir.normalize()
            
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery, self.asset_manager, bullet_dir.x * 4, bullet_dir.y * 4, 
                                 asset_key="reisen_bullet", sprite_size=(12,12), fallback_color=REISEN_BULLET_COLOR)
            self.bullets.add(bullet)
            
    def shoot_spell_pattern(self):
        # "Illusionary Blast": Rings of bullets expanding outwards
        num_bullets_in_ring = 12
        angle_step = 360 / num_bullets_in_ring
        for i in range(num_bullets_in_ring):
            angle = i * angle_step
            vec = pygame.math.Vector2(1, 0).rotate(angle) # Base vector pointing right, rotated
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery, self.asset_manager, vec.x * 2.5, vec.y * 2.5, 
                                 asset_key="reisen_bullet", sprite_size=(14,14), fallback_color=REISEN_BULLET_COLOR) # Larger spell bullets
            self.bullets.add(bullet)

    def die(self):
        # Reisen specific death
        if self.spell_card_active and self.health <= 0: # Defeated during spell card
            self.spell_card_bonus_achieved = True
            print(f"Spell Card '{self.spell_card_name}' bonus achieved (defeat)!")
        
        print("Reisen defeated!")
        self.is_defeated_flag = True 
        super().die() 

    def draw(self, surface): # Override to prevent drawing if not fully entered
        if self.rect.bottom <= 0 and not self.is_active : # Not yet on screen
             return
        super().draw(surface)

KAGUYA_COLOR = (220, 220, 220) # Silvery white for Kaguya
KAGUYA_BULLET_COLOR_JEWEL = (255, 215, 0) # Gold for Jewel Scatter
KAGUYA_BULLET_COLOR_BRANCH = (34, 139, 34) # Forest Green for Bullet Branch
KAGUYA_BULLET_COLOR_LUNAR = (173, 216, 230) # Light Blue for Lunar Vortex
KAGUYA_BULLET_COLOR_RAINBOW = [(255,0,0), (255,165,0), (255,255,0), (0,128,0), (0,0,255), (75,0,130), (238,130,238)] # For Rainbow Bullets (fallback)
KAGUYA_BULLET_COLOR_FLAME = (255, 69, 0) # OrangeRed for Flame (fallback)

class Kaguya(BaseEnemy):
    def __init__(self, position, asset_manager):
        super().__init__(position, health=500, asset_manager=asset_manager,
                         sprite_key="enemy_kaguya", sprite_size=(80,100), fallback_color=KAGUYA_COLOR)
        
        self.entry_target_y = position[1]
        if self.image:
            self.rect = self.image.get_rect(center=position)
        self.rect.bottom = 0 # Start off-screen from the top
        self.entry_speed = 1.5
        self.is_active = False # Becomes true after entry animation

        self.current_phase = 1
        self.phase_health_thresholds = {
            1: self.initial_health * 0.75, # Phase 1 ends when health is 75%
            2: self.initial_health * 0.40, # Phase 2 ends when health is 40%
            3: 0 # Phase 3 ends when health is 0
        }
        self.spell_card_active = False
        self.current_spell_name = ""
        self.spell_card_duration = 0
        self.spell_card_start_time = 0
        self.current_spell_card_bonus_value = 0 # Stores the value for the *current* active spell
        self.spell_card_bonus_achieved = False  # Flag if current spell bonus is achieved
        
        # Timers for patterns
        self.pattern_timer = 0
        self.shoot_timer = 0
        
        # Phase-specific attributes
        self.phase_initialized = False # Flag to run setup once per phase

        # Placeholder for defeat
        self.is_defeated_flag = False

    def initialize_phase_attributes(self):
        """Called once at the start of each phase to set up patterns."""
        current_time = pygame.time.get_ticks()
        self.pattern_timer = current_time
        self.shoot_timer = current_time
        self.spell_card_active = False # Ensure spells from previous phase are off
        self.current_spell_name = ""
        
        if self.current_phase == 1:
            print("Kaguya Phase 1 Initialized")
            self.non_spell_shoot_delay = 1200 # ms for "Jewel Scatter"
            # Spell Card for Phase 1: "Divine Treasure 'Jewel Branch of Hourai -Rainbow Bullets-'"
            self.spell_health_trigger = self.initial_health * 0.85 # Triggers within phase 1
            self.spell_duration_phase1 = 12000 
            self.spell_shoot_delay_phase1 = 150 
            self.spell_name_phase1 = "Divine Treasure 'Jewel Branch of Hourai -Rainbow Bullets-'"
            self.spell_bonus_phase1 = 75000

        elif self.current_phase == 2:
            print("Kaguya Phase 2 Initialized")
            self.non_spell_shoot_delay = 1500 
            self.spell_health_trigger = self.initial_health * 0.55 
            self.spell_duration_phase2 = 15000 
            self.spell_shoot_delay_phase2 = 200 
            self.spell_name_phase2 = "Impossible Request 'Robe of the Fire Rat -Indestructible Flame-'"
            self.spell_bonus_phase2 = 100000

        elif self.current_phase == 3:
            print("Kaguya Phase 3 Initialized")
            self.non_spell_shoot_delay = 1000 
            self.spell_health_trigger = self.initial_health * 0.15 
            self.spell_duration_phase3 = 20000 
            self.spell_shoot_delay_phase3 = 100 
            self.spell_name_phase3 = "End of Imperishable Night"
            self.spell_bonus_phase3 = 150000
            
        self.phase_initialized = True

    def update(self, player_pos=None):
        if not self.is_active:
            self.rect.y += self.entry_speed
            if self.rect.centery >= self.entry_target_y:
                self.rect.centery = self.entry_target_y
                self.is_active = True
                self.phase_initialized = False # Initialize first phase
            return

        current_time = pygame.time.get_ticks()

        # Check for phase transition
        if self.health <= self.phase_health_thresholds[self.current_phase] and self.current_phase < 3:
            self.current_phase += 1
            self.phase_initialized = False
            print(f"Kaguya transitioning to Phase {self.current_phase}")
            # Placeholder for phase transition effect (e.g. main.py can flash screen)
            self.trigger_phase_transition_effect = True 
        
        if not self.phase_initialized:
            self.initialize_phase_attributes()

        # Handle spell card logic first
        if self.spell_card_active:
            # Check if spell card ends due to duration or Kaguya's health for the current phase ending
            phase_end_health_for_spell = self.phase_health_thresholds.get(self.current_phase, 0)
            if self.health <= phase_end_health_for_spell or \
               (current_time - self.spell_card_start_time > self.spell_card_duration):
                
                if self.health > phase_end_health_for_spell : # Survived the duration of the spell
                    self.spell_card_bonus_achieved = True
                    print(f"Kaguya Spell Card '{self.current_spell_name}' bonus achieved (duration)!")
                # If health <= phase_end_health_for_spell, bonus is handled by phase transition/die logic
                
                self.spell_card_active = False
                self.current_spell_name = ""
                self.pattern_timer = current_time 
                self.shoot_timer = current_time
                self.current_spell_card_bonus_value = 0 # Reset current bonus value
            else:
                # Spell card shooting logic based on phase
                if self.current_phase == 1 and current_time - self.shoot_timer > self.spell_shoot_delay_phase1:
                    self.shoot_timer = current_time
                    self.shoot_spell_jewel_branch()
                elif self.current_phase == 2 and current_time - self.shoot_timer > self.spell_shoot_delay_phase2:
                    self.shoot_timer = current_time
                    self.shoot_spell_fire_rat_robe(player_pos)
                elif self.current_phase == 3 and current_time - self.shoot_timer > self.spell_shoot_delay_phase3:
                    self.shoot_timer = current_time
                    self.shoot_spell_end_of_imperishable_night(player_pos)
        else: # Non-spell card logic
            # Check if it's time to activate a spell card
            if self.current_phase == 1 and self.health <= self.spell_health_trigger and self.health > self.phase_health_thresholds[1]:
                self.activate_spell_card(self.spell_name_phase1, self.spell_duration_phase1, self.spell_bonus_phase1)
            elif self.current_phase == 2 and self.health <= self.spell_health_trigger and self.health > self.phase_health_thresholds[2]:
                self.activate_spell_card(self.spell_name_phase2, self.spell_duration_phase2, self.spell_bonus_phase2)
            elif self.current_phase == 3 and self.health <= self.spell_health_trigger and self.health > self.phase_health_thresholds[3]: # health > 0
                self.activate_spell_card(self.spell_name_phase3, self.spell_duration_phase3, self.spell_bonus_phase3)
            else: # Regular non-spell attacks
                if current_time - self.shoot_timer > self.non_spell_shoot_delay:
                    self.shoot_timer = current_time
                    if self.current_phase == 1:
                        self.shoot_jewel_scatter(player_pos)
                    elif self.current_phase == 2:
                        self.shoot_bullet_branch()
                    elif self.current_phase == 3:
                        self.shoot_lunar_vortex(player_pos)
        
        super().update() # Handles bullet updates and checks for actual death (health <= 0)

    def activate_spell_card(self, name, duration, bonus_value):
        self.spell_card_active = True
        self.current_spell_name = name
        self.spell_card_duration = duration
        self.current_spell_card_bonus_value = bonus_value
        self.spell_card_bonus_achieved = False # Reset for new spell
        self.spell_card_start_time = pygame.time.get_ticks()
        self.shoot_timer = self.spell_card_start_time 
        print(f"Spell Card Activated: {self.current_spell_name} (Bonus: {self.current_spell_card_bonus_value})")

    # --- NON-SPELL PATTERNS ---
    def shoot_jewel_scatter(self, player_pos): # Phase 1
        print("Kaguya: Jewel Scatter")
        num_bullets = 15
        for _ in range(num_bullets):
            angle_offset = random.uniform(-45, 45) # Spread angle
            speed = random.uniform(2, 4)
            # Aim generally towards player but with spread
            vec_to_player = pygame.math.Vector2(player_pos) - pygame.math.Vector2(self.rect.center)
            if vec_to_player.length_squared() == 0: vec_to_player = pygame.math.Vector2(0,1)
            
            fire_vec = vec_to_player.rotate(angle_offset).normalize()
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery, self.asset_manager, fire_vec.x * speed, fire_vec.y * speed, 
                                 asset_key="kaguya_bullet_jewel", sprite_size=(10,10), fallback_color=KAGUYA_BULLET_COLOR_JEWEL)
            self.bullets.add(bullet)

    def shoot_bullet_branch(self): # Phase 2
        print("Kaguya: Bullet Branch")
        num_streams = 3
        bullets_per_stream = 8
        stream_angle_spread = 60 # Total spread for streams around a central axis
        initial_angle = random.uniform(0, 360) # Randomize main direction of branches
        
        for i in range(num_streams):
            base_angle = initial_angle + (i - num_streams//2) * (stream_angle_spread / (num_streams -1 if num_streams >1 else 1) )
            for j in range(bullets_per_stream):
                # Bullets in a stream, slightly offset angle for "branching"
                angle = base_angle + j * 5 # Small angle change per bullet in stream
                speed = 2.5 + j * 0.1 # Slightly increasing speed
                vec = pygame.math.Vector2(0,1).rotate(angle) # Example: rotate a base vector
                bullet = EnemyBullet(self.rect.centerx, self.rect.centery, self.asset_manager, vec.x * speed, vec.y * speed, 
                                     asset_key="kaguya_bullet_branch", sprite_size=(8,14), fallback_color=KAGUYA_BULLET_COLOR_BRANCH)
                self.bullets.add(bullet)

    def shoot_lunar_vortex(self, player_pos): # Phase 3
        print("Kaguya: Lunar Vortex")
        num_spirals = 4
        bullets_per_spiral_arm = 10
        self.vortex_angle = getattr(self, 'vortex_angle', 0) # Keep track of angle for rotation
        
        for i in range(num_spirals):
            base_angle = self.vortex_angle + (360 / num_spirals) * i
            for j in range(bullets_per_spiral_arm):
                angle = base_angle + j * 15 # Angle between bullets in an arm
                distance_from_center = 10 + j * 5 # Bullets appear further out along the arm
                speed = 2.0
                
                # Calculate initial position relative to Kaguya for spiral effect
                spawn_x = self.rect.centerx + distance_from_center * pygame.math.Vector2(1,0).rotate(angle).x
                spawn_y = self.rect.centery + distance_from_center * pygame.math.Vector2(1,0).rotate(angle).y
                
                # Bullets move outwards from their spawn
                dir_vec = (pygame.math.Vector2(spawn_x, spawn_y) - pygame.math.Vector2(self.rect.center)).normalize()
                
                bullet = EnemyBullet(spawn_x, spawn_y, self.asset_manager, dir_vec.x * speed, dir_vec.y * speed, 
                                     asset_key="kaguya_bullet_lunar", sprite_size=(12,12), fallback_color=KAGUYA_BULLET_COLOR_LUNAR)
                self.bullets.add(bullet)
        self.vortex_angle = (self.vortex_angle + 7) % 360 # Rotate the whole vortex for next shot

    # --- SPELL CARD PATTERNS ---
    def shoot_spell_jewel_branch(self): # Phase 1 Spell
        print(f"Kaguya Spell: {self.spell_name_phase1}")
        num_streams = 8
        angle_offset = random.uniform(0, 360 / num_streams)
        rainbow_keys = [
            "kaguya_bullet_rainbow_red", "kaguya_bullet_rainbow_orange", "kaguya_bullet_rainbow_yellow",
            "kaguya_bullet_rainbow_green", "kaguya_bullet_rainbow_blue", "kaguya_bullet_rainbow_indigo",
            "kaguya_bullet_rainbow_violet"
        ]
        for i in range(num_streams):
            angle = (360 / num_streams) * i + angle_offset
            asset_key = random.choice(rainbow_keys)
            fallback_color = KAGUYA_BULLET_COLOR_RAINBOW[i % len(KAGUYA_BULLET_COLOR_RAINBOW)] # Fallback if key is bad
            vec = pygame.math.Vector2(0,1).rotate(angle)
            for k in range(3):
                speed = 3 + k * 0.5
                bullet = EnemyBullet(self.rect.centerx + vec.x * k * 10, self.rect.centery + vec.y * k * 10, 
                                     self.asset_manager, vec.x * speed, vec.y * speed, 
                                     asset_key=asset_key, sprite_size=(10,10), fallback_color=fallback_color)
                self.bullets.add(bullet)

    def shoot_spell_fire_rat_robe(self, player_pos): # Phase 2 Spell
        print(f"Kaguya Spell: {self.spell_name_phase2}")
        num_bullets_in_wave = 20
        wave_angle_spread = 120 # How wide the wave is
        
        # Aim generally towards player
        vec_to_player = pygame.math.Vector2(player_pos) - pygame.math.Vector2(self.rect.center)
        if vec_to_player.length_squared() == 0: base_angle_deg = 90 # Shoots down
        else: base_angle_deg = vec_to_player.angle_to(pygame.math.Vector2(0,1))

        for i in range(num_bullets_in_wave):
            angle = base_angle_deg - wave_angle_spread/2 + (wave_angle_spread / (num_bullets_in_wave-1)) * i
            speed = random.uniform(2.5, 4.0)
            vec = pygame.math.Vector2(0,1).rotate(angle)
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery, self.asset_manager, vec.x * speed, vec.y * speed, 
                                 asset_key="kaguya_bullet_flame", sprite_size=(14,14), fallback_color=KAGUYA_BULLET_COLOR_FLAME)
            self.bullets.add(bullet)

    def shoot_spell_end_of_imperishable_night(self, player_pos): # Phase 3 Spell
        print(f"Kaguya Spell: {self.spell_name_phase3}")
        # 1. Fast aimed shots
        for _ in range(3):
            vec_to_player = pygame.math.Vector2(player_pos) - pygame.math.Vector2(self.rect.center)
            if vec_to_player.length_squared() == 0: vec_to_player = pygame.math.Vector2(0,1)
            fire_vec = vec_to_player.normalize()
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery, self.asset_manager, fire_vec.x * 5, fire_vec.y * 5, 
                                 asset_key="kaguya_bullet_jewel", sprite_size=(8,8), fallback_color=KAGUYA_BULLET_COLOR_JEWEL)
            self.bullets.add(bullet)
        
        # 2. Slower omnidirectional burst
        num_bullets_ring = 24
        angle_step = 360 / num_bullets_ring
        self.eoin_angle = getattr(self, 'eoin_angle', 0) 
        for i in range(num_bullets_ring):
            angle = i * angle_step + self.eoin_angle
            vec = pygame.math.Vector2(1, 0).rotate(angle)
            bullet = EnemyBullet(self.rect.centerx, self.rect.centery, self.asset_manager, vec.x * 2, vec.y * 2, 
                                 asset_key="kaguya_bullet_lunar", sprite_size=(12,12), fallback_color=KAGUYA_BULLET_COLOR_LUNAR)
            self.bullets.add(bullet)
        self.eoin_angle = (self.eoin_angle + 10) % 360


    def die(self):
        if not self.is_defeated_flag: 
            if self.spell_card_active and self.health <= 0: # Defeated during the final spell card
                 # Check if health is below the start of the current phase's spell trigger
                if self.health <= self.spell_health_trigger : # Ensures it was the *active* spell
                    self.spell_card_bonus_achieved = True
                    print(f"Kaguya Spell Card '{self.current_spell_name}' bonus achieved (final defeat)!")
            
            print("Kaguya FINAL DEFEAT!")
            self.is_defeated_flag = True 
        super().die()

    def draw(self, surface):
        if not self.is_active: # Not yet on screen
             return
        super().draw(surface)
        # Could add phase-specific visual changes here if desired
        # e.g. self.image.fill(NEW_COLOR_IF_PHASE_2)
