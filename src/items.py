import pygame
import random

# Screen dimensions (consider moving to a config file later)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Item Colors (placeholders for fallback)
SCORE_ITEM_COLOR = (0, 255, 0)
POWER_ITEM_COLOR = (255, 0, 0)
BOMB_ITEM_COLOR = (0, 0, 255)

# Item Types
TYPE_SCORE = 'score'
TYPE_POWER = 'power'
TYPE_BOMB = 'bomb'

class Item(pygame.sprite.Sprite):
    def __init__(self, position, item_type, asset_manager):
        super().__init__()
        self.item_type = item_type
        self.asset_manager = asset_manager
        self.size = 16 # Default visual size if using sprites

        asset_key = f"item_{self.item_type}" # e.g., "item_score"
        self.image = self.asset_manager.get_image(asset_key, scale_to=(self.size, self.size))

        if not self.image: # Fallback
            self.image = pygame.Surface([10, 10])
            color = (100,100,100)
            if self.item_type == TYPE_SCORE: color = SCORE_ITEM_COLOR
            elif self.item_type == TYPE_POWER: color = POWER_ITEM_COLOR
            elif self.item_type == TYPE_BOMB: color = BOMB_ITEM_COLOR
            self.image.fill(color)

        self.rect = self.image.get_rect(center=position)
        self.speed = 2 
        self.attraction_speed = 7 # Speed when attracted to player
        self.is_attracted = False

    def update(self, player_pos=None, is_player_at_top=False):
        if is_player_at_top:
            self.is_attracted = True # Once attracted, stays attracted (or until collected)

        if self.is_attracted and player_pos:
            # Move towards player
            direction_x = player_pos[0] - self.rect.centerx
            direction_y = player_pos[1] - self.rect.centery
            
            # Normalize
            distance = (direction_x**2 + direction_y**2)**0.5
            if distance > 0: # Avoid division by zero
                norm_x = direction_x / distance
                norm_y = direction_y / distance
                
                self.rect.x += norm_x * self.attraction_speed
                self.rect.y += norm_y * self.attraction_speed
            
        else: # Default downward movement
            self.rect.y += self.speed
            
        if self.rect.top > SCREEN_HEIGHT: # Remove if it goes off screen
            self.kill()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

def create_item(position, asset_manager, item_type=None):
    """Helper function to create a specific item type or a random one if not specified."""
    if item_type is None:
        item_type = random.choice([TYPE_SCORE, TYPE_POWER, TYPE_BOMB])
    return Item(position, item_type, asset_manager)
