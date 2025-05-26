import pygame

class BulletPool:
    def __init__(self, bullet_class, initial_size=100, asset_manager=None, default_asset_key=None, default_sprite_size=None):
        """
        Initializes the bullet pool.
        Args:
            bullet_class: The class of bullet to pool (e.g., EnemyBullet, PlayerBullet).
            initial_size (int): The initial number of bullets to create.
            asset_manager: The asset manager instance for loading bullet sprites.
            default_asset_key: The default asset key for bullets from this pool.
            default_sprite_size: The default sprite size for bullets.
        """
        self.bullet_class = bullet_class
        self.asset_manager = asset_manager
        self.default_asset_key = default_asset_key
        self.default_sprite_size = default_sprite_size
        
        self.pool = []
        self.active_bullets = pygame.sprite.Group() # Group for active bullets from this pool

        for _ in range(initial_size):
            # Create bullet instance. It needs necessary args like asset_manager.
            # This assumes bullet_class can be instantiated with just asset_manager initially,
            # and then reset/re-initialized.
            # A more robust pool might need a factory method if bullet constructors are complex.
            if self.asset_manager and self.default_asset_key:
                 # Simplified: assumes bullet_class constructor takes asset_manager, x, y, speed_x, speed_y, asset_key, sprite_size
                 # For pooling, we might make a simpler constructor or a dedicated re-init method.
                bullet = self.bullet_class(0, 0, self.asset_manager, 0, 0, self.default_asset_key, self.default_sprite_size)
            else: # Fallback if no asset manager for some reason (e.g. player bullets before AM was passed)
                bullet = self.bullet_class(0,0) # This would need adjustment based on actual bullet classes
            
            bullet.active = False # Add 'active' flag to your bullet classes
            self.pool.append(bullet)

    def get_bullet(self):
        """Gets an inactive bullet from the pool or creates a new one if none are available."""
        for bullet in self.pool:
            if not bullet.active:
                return bullet
        
        # Optional: Expand the pool if no inactive bullets are found
        # print("Bullet pool depleted, creating new bullet.")
        if self.asset_manager and self.default_asset_key:
            bullet = self.bullet_class(0, 0, self.asset_manager, 0, 0, self.default_asset_key, self.default_sprite_size)
        else:
            bullet = self.bullet_class(0,0) # Adjust as needed

        bullet.active = False # Should be set to active when configured and used
        self.pool.append(bullet)
        return bullet

    def release_bullet(self, bullet):
        """Marks a bullet as inactive and returns it to the pool."""
        bullet.active = False
        bullet.kill() # Remove from all sprite groups (including self.active_bullets if added there)
        # Potentially call a bullet.reset() method here if bullets have complex state
        # For example: bullet.reset(0, 0, 0, 0, some_default_asset_key)

    def update_active(self, *args, **kwargs):
        """Updates all active bullets that were dispensed by this pool."""
        # This method assumes bullets added to self.active_bullets when obtained
        # Alternatively, the main game loop manages updates for all bullets globally.
        # This is more for if the pool itself manages its active bullets group.
        for bullet in list(self.active_bullets): # Iterate over a copy if bullets can be removed
            if bullet.active:
                bullet.update(*args, **kwargs)
            else: # Bullet was deactivated (e.g. off-screen, hit target)
                self.active_bullets.remove(bullet) # No longer managed by pool's active group

# --- Modifications needed in bullet classes (e.g., src/enemy.py EnemyBullet, src/player.py Bullet) ---
# 1. Add `self.active = False` in `__init__`.
# 2. Add a `reset(self, x, y, speed_x, speed_y, asset_key, sprite_size, ...other_params)` method:
#    This method would re-initialize the bullet's state:
#    self.rect.x = x
#    self.rect.y = y
#    self.speed_x = speed_x
#    self.speed_y = speed_y
#    self.image = self.asset_manager.get_image(asset_key, scale_to=sprite_size) # Or however sprite is set
#    self.grazed_by_player = False # If applicable
#    self.active = True
#    # Add to relevant sprite groups (e.g., all_enemy_bullets in main.py)

# --- Conceptual Integration in Player/Enemy classes ---
# Instead of: `bullet = EnemyBullet(...)`, `self.bullets.add(bullet)`
# It would be:
# `pooled_bullet = enemy_bullet_pool.get_bullet()`
# `if pooled_bullet:`
# `  pooled_bullet.reset(self.rect.centerx, self.rect.bottom, speed_x, speed_y, "specific_bullet_key", (size_x,size_y))`
# `  self.bullets.add(pooled_bullet)`
# `  all_enemy_bullets_group_in_main.add(pooled_bullet)` # Important for global collision & drawing

# When a bullet is to be destroyed (e.g., in its own update method when off-screen):
# `self.active = False`
# `bullet_pool_instance.release_bullet(self)` # This bullet now calls its pool to release itself
# `self.kill()` would still be called to remove from Pygame groups, but release_bullet handles pool state.
# The `kill()` method in the bullet might be a good place to call `bullet_pool_instance.release_bullet(self)`.
# Ensure the bullet has a reference to its pool or the pool is globally accessible.
```

**Textual Description of Object Pooling Integration:**

1.  **Bullet Class Changes:**
    *   Add `active = False` attribute to `Player.Bullet` and `EnemyBullet`.
    *   Add a `reset(self, x, y, asset_manager, angle_or_speeds, asset_key, sprite_size, **kwargs)` method. This method would:
        *   Set `self.rect.centerx/bottom` or `self.rect.x/y`.
        *   Set velocity/speed components.
        *   Update `self.image` using `asset_manager.get_image(asset_key, scale_to=sprite_size)`.
        *   Reset any other state (e.g., `self.grazed_by_player = False`).
        *   Set `self.active = True`.
    *   Modify the `update()` method of bullets: if a bullet goes off-screen or hits a target, instead of just `self.kill()`, it would first set `self.active = False`, then call `its_pool.release_bullet(self)`, and then `self.kill()`. This requires bullets to know their pool or for `main.py` to manage this.

2.  **BulletPool Class (`src/bullet_pool.py`):**
    *   `__init__(self, bullet_class, initial_size, asset_manager, ...)`: Pre-creates `initial_size` bullets of `bullet_class`, sets them as inactive, and stores them.
    *   `get_bullet(self)`: Finds an inactive bullet, calls its `reset()` method with necessary parameters (position, speed, type, etc.), adds it to a general "active bullets" sprite group (managed by `main.py`), and returns it. If no inactive bullets, can optionally create more or log.
    *   `release_bullet(self, bullet)`: Called when a bullet becomes inactive. It effectively returns the bullet to the pool (simply marking it `active = False` is enough if `get_bullet` iterates).

3.  **Shooter Classes (`Player`, `ZakoEnemy`, `Reisen`, `Kaguya`):**
    *   Each shooter class (or `main.py` on their behalf) would hold references to relevant `BulletPool` instances (e.g., `player_needle_pool`, `enemy_basic_pool`).
    *   When shooting, instead of `bullet = BulletClass(...)`, they'd call `bullet = bullet_pool.get_bullet()`. Then, they'd call `bullet.reset(params...)` to configure it for that specific shot.
    *   The bullet would then be added to `self.bullets` (if the enemy tracks its own) AND to the global `all_player_bullets` or `all_enemy_bullets` group in `main.py`.

4.  **`main.py` Changes:**
    *   Instantiate `BulletPool`s for different types of bullets.
    *   Modify the bullet `update()` methods (or the collision checks in `main.py`) so that when a bullet is "killed," it's released back to its pool. For example, when `bullet.kill()` is called in `main.py` after a collision, `bullet_pool.release_bullet(bullet)` would also be called.

This makes bullet creation/destruction much cheaper, reducing garbage collection overhead and improving performance with many bullets.

**3. Precise Collision Detection (Review and Confirm)**

*   **Review from previous `main.py` structure:**
    *   **Player bullets vs. Enemies:** `pygame.sprite.spritecollide(bullet, enemies, False, pygame.sprite.collide_rect_ratio(0.8))` and `pygame.sprite.collide_rect(bullet, reisen_instance/kaguya_instance)`. This uses rectangle-based collision, which is generally fine for enemies, especially if sprites are somewhat rectangular. `collide_rect_ratio` helps.
    *   **Enemy bullets vs. Player:** The last attempt showed a custom check:
        ```python
        player_hitbox_rect = pygame.Rect(0,0, player.hitbox_radius*2, player.hitbox_radius*2)
        player_hitbox_rect.center = player.rect.center
        # ... loop through all_enemy_bullets ...
        if player_hitbox_rect.colliderect(bullet.rect):
            # ... player hit ...
        ```
        This is good! It uses a specific small rectangle (`player_hitbox_rect`) derived from `player.hitbox_radius` and centered on the player's visual rect, then checks collision with the enemy bullet's `rect`. This is a precise enough method for a small, central hitbox.
    *   **Player vs. Items:** `pygame.sprite.spritecollide(player, items, True, pygame.sprite.collide_rect_ratio(0.8))`. This uses the player's full visual `rect` for item collection, which is generally fine and more forgiving for the player.

*   **Confirmation/Notes:**
    *   The current approach for enemy bullets vs. player hitbox is good and more precise than using the player's full visual rectangle. No immediate changes are needed here.
    *   Using `collide_rect_ratio` or simple `collide_rect` for player bullets vs. enemies and player vs. items is standard and acceptable. More pixel-perfect collision (`pygame.sprite.collide_mask`) is an option for the future if visual sprites become very non-rectangular and precise hits are critical, but it's more computationally expensive.

**4. Sound Manager Implementation (Basic Structure)**

**New File: `config/sounds.json` (Conceptual)**
```json
{
    "sfx_player_shoot": "assets/sounds/sfx/player_shoot.wav",
    "sfx_player_bomb": "assets/sounds/sfx/player_bomb.wav",
    "sfx_enemy_hit": "assets/sounds/sfx/enemy_hit.wav",
    "sfx_enemy_explode": "assets/sounds/sfx/enemy_explode.wav",
    "sfx_item_get": "assets/sounds/sfx/item_get.wav",
    "sfx_graze": "assets/sounds/sfx/graze.wav",
    "sfx_player_hit": "assets/sounds/sfx/player_hit.wav",
    "sfx_spell_card_activate": "assets/sounds/sfx/spell_card_activate.wav",
    "bgm_title": "assets/sounds/bgm/title_theme.ogg",
    "bgm_stage1": "assets/sounds/bgm/stage1_theme.ogg",
    "bgm_boss_reisen": "assets/sounds/bgm/reisen_theme.ogg",
    "bgm_boss_kaguya": "assets/sounds/bgm/kaguya_theme.ogg"
}
```
*(User would need to create placeholder `.wav`/`.ogg` files in these paths, or the SoundManager will just print errors when trying to load them).*

**New File: `src/sound.py`**
