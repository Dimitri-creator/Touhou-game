import pygame
import json
import os

class SoundManager:
    def __init__(self, config_path='config/sounds.json', default_sfx_volume=0.5, default_bgm_volume=0.3):
        if not pygame.mixer.get_init():
            pygame.mixer.init() # Initialize mixer if not already done

        self.config_path = config_path
        self._sfx_cache = {}
        self._bgm_cache = {} # Though BGM is usually streamed, pre-loading path is useful
        self._sound_map = self._load_config()

        self.sfx_volume = default_sfx_volume
        self.bgm_volume = default_bgm_volume
        
        # Apply initial BGM volume (Pygame's BGM volume is global)
        pygame.mixer.music.set_volume(self.bgm_volume)

    def _load_config(self):
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Sound configuration file not found at {self.config_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Warning: Could not parse sound configuration file at {self.config_path}")
            return {}

    def play_sfx(self, sfx_key, volume_multiplier=1.0):
        if sfx_key not in self._sfx_cache:
            sound_path = self._sound_map.get(sfx_key)
            if not sound_path:
                print(f"Warning: SFX key '{sfx_key}' not found in configuration.")
                return
            if not os.path.exists(sound_path):
                print(f"Warning: SFX file not found at '{sound_path}' for key '{sfx_key}'.")
                return
            
            try:
                self._sfx_cache[sfx_key] = pygame.mixer.Sound(sound_path)
            except pygame.error as e:
                print(f"Error loading SFX '{sfx_key}' from '{sound_path}': {e}")
                return
        
        sound = self._sfx_cache.get(sfx_key)
        if sound:
            sound.set_volume(self.sfx_volume * volume_multiplier)
            sound.play()

    def play_bgm(self, bgm_key, loop=-1, fade_ms=0):
        # Stop any currently playing music
        pygame.mixer.music.stop()
        pygame.mixer.music.unload() # Unload previous music

        music_path = self._sound_map.get(bgm_key)
        if not music_path:
            print(f"Warning: BGM key '{bgm_key}' not found in configuration.")
            return
        if not os.path.exists(music_path):
            print(f"Warning: BGM file not found at '{music_path}' for key '{bgm_key}'.")
            return

        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.bgm_volume) # Apply current BGM volume
            pygame.mixer.music.play(loops=loop, fade_ms=fade_ms)
            self._bgm_cache[bgm_key] = music_path # Cache path for reference
        except pygame.error as e:
            print(f"Error loading or playing BGM '{bgm_key}' from '{music_path}': {e}")

    def stop_bgm(self, fade_ms=0):
        pygame.mixer.music.fadeout(fade_ms)

    def set_sfx_volume(self, volume):
        """Sets the global SFX volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))
        # Individual sounds have their volume set at play time based on this master sfx_volume.

    def set_bgm_volume(self, volume):
        """Sets the BGM volume (0.0 to 1.0)."""
        self.bgm_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.bgm_volume)

# Example Usage (conceptual, would be in main.py or game states):
# sound_manager = SoundManager()
# sound_manager.play_sfx("player_shoot")
# sound_manager.play_bgm("stage1_theme")
# sound_manager.set_bgm_volume(0.5)
```

**Conceptual Integration of SoundManager in `main.py`:**

1.  **Initialization:**
    *   `sound_manager = SoundManager()` created globally after `pygame.init()`.
2.  **SFX Calls:**
    *   Player shoot: In `Player.shoot()`, after adding a bullet, call `sound_manager.play_sfx("sfx_player_shoot")`.
    *   Player bomb: In `Player.activate_spell_card()`, if successful, call `sound_manager.play_sfx("sfx_player_bomb")`.
    *   Enemy hit: In `BaseEnemy.take_damage()`, if health > 0, call `sound_manager.play_sfx("sfx_enemy_hit")`.
    *   Enemy explode: In `BaseEnemy.die()` (or specific enemy `die` methods), call `sound_manager.play_sfx("sfx_enemy_explode")`.
    *   Item get: In `main.py`'s player-item collision logic, call `sound_manager.play_sfx("sfx_item_get")`.
    *   Graze: In `main.py`'s graze detection logic, call `sound_manager.play_sfx("sfx_graze")`.
    *   Player hit: In `main.py`'s player-bullet collision logic, when player takes damage, call `sound_manager.play_sfx("sfx_player_hit")`.
    *   Spell Card Activate: In boss methods when a spell card starts (e.g., `Reisen.update` or `Kaguya.activate_spell_card`), call `sound_manager.play_sfx("sfx_spell_card_activate")`.
3.  **BGM Calls:**
    *   Title Screen: When `current_state` becomes `TITLE_SCREEN`, call `sound_manager.play_bgm("bgm_title")`.
    *   Stage Start: When `current_state` becomes `GAMEPLAY` (and it's a new game/stage), call `sound_manager.play_bgm("bgm_stage1")`.
    *   Boss Fights: When a boss (`reisen_instance` or `kaguya_instance`) becomes active, call `sound_manager.play_bgm("bgm_boss_reisen")` or `sound_manager.play_bgm("bgm_boss_kaguya")`.
    *   Game Clear/Over: May stop BGM or play a specific theme.
4.  **Volume Control (Options Screen):**
    *   The `OPTIONS_SCREEN` would have UI elements (e.g., sliders or text input, currently just text placeholders) that, when changed, call `sound_manager.set_sfx_volume()` and `sound_manager.set_bgm_volume()`.

This provides a solid structure for sound management. The actual calls would need to be inserted at the correct logical points in the game flow, primarily within `main.py` and the respective class methods.
