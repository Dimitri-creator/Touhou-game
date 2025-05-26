import pygame
import json
import os

class AssetManager:
    """
    Manages game assets, loading them from paths defined in a configuration file.
    Caches loaded images to avoid redundant disk I/O and processing.
    """
    def __init__(self, config_path='config/assets.json', base_asset_path='assets/'):
        """
        Initializes the AssetManager.
        Args:
            config_path (str): Path to the JSON configuration file for assets.
            base_asset_path (str): The base directory where assets are stored. 
                                   (Note: config_path paths are currently absolute or relative to root)
        """
        self.config_path = config_path
        # self.base_asset_path = base_asset_path # Not strictly used if paths in JSON are full/relative to root
        self._cache = {}
        self._asset_map = self._load_config()
        self._default_placeholder_surface = self._create_default_placeholder()

    def _load_config(self):
        """
        Loads the asset configuration JSON file.
        Returns:
            dict: A dictionary mapping asset keys to file paths.
        How to add new assets:
        1. Add a new entry to the JSON file specified in `config_path`.
           The key is a unique identifier for the asset (e.g., "player_ship_level1").
           The value is the file path to the image (e.g., "assets/player/ship_lvl1.png").
        2. Ensure the image file exists at the specified path.
        """
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: Asset configuration file not found at {self.config_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Could not parse asset configuration file at {self.config_path}")
            return {}

    def _create_default_placeholder(self):
        """Creates a magenta square as a fallback placeholder image."""
        surface = pygame.Surface((30, 30))
        surface.fill((255, 0, 255)) # Magenta
        return surface

    def get_image(self, asset_key, scale_to=None, use_colorkey=False, colorkey_color=(0,0,0)):
        """
        Retrieves a Pygame Surface for the given asset key.
        Loads from disk if not cached, otherwise returns the cached surface.
        Optionally scales the image.
        Args:
            asset_key (str): The key for the asset, as defined in the config file.
            scale_to (tuple, optional): A tuple (width, height) to scale the image to.
                                        If None, original size is used.
            use_colorkey (bool): If True, sets a colorkey for transparency.
            colorkey_color (tuple): The RGB color to use for the colorkey (default is black).
        Returns:
            pygame.Surface: The loaded (and optionally scaled) image surface.
                            Returns a default placeholder if loading fails.
        How to change existing assets:
        1. Update the file path for the corresponding key in the JSON config file.
        2. Or, replace the image file at the existing path with a new image.
        """
        image_path = self._asset_map.get(asset_key)
        if not image_path:
            print(f"Error: Asset key '{asset_key}' not found in configuration.")
            return self._default_placeholder_surface

        # Create a unique cache key for scaled images
        cache_key = (asset_key, scale_to, use_colorkey) # Colorkey setting can change appearance

        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            # Check if the default placeholder itself is requested, to avoid recursion if it's missing
            if asset_key == "default_placeholder" and image_path == "assets/ui/default_placeholder.png":
                # Try to load the actual default placeholder file. If it fails, use the created magenta one.
                try:
                    loaded_image = pygame.image.load(image_path).convert_alpha()
                except pygame.error:
                    # This means the default_placeholder.png is missing or invalid.
                    # The magenta surface is already created, so just use it.
                    # No need to scale/colorkey the magenta square.
                    self._cache[cache_key] = self._default_placeholder_surface
                    return self._default_placeholder_surface
            else:
                 # For other assets, attempt to load them.
                if not os.path.exists(image_path):
                    print(f"Error: Image file not found at {image_path} for key '{asset_key}'. Using default placeholder.")
                    # Cache the default placeholder for this specific asset_key and scale_to combination
                    # to avoid repeated file not found errors for the same key.
                    self._cache[cache_key] = self._default_placeholder_surface
                    return self._default_placeholder_surface
                
                loaded_image = pygame.image.load(image_path)

            # Using convert_alpha() is generally good for images with transparency.
            # If images are opaque, .convert() might be slightly faster but less flexible.
            image_surface = loaded_image.convert_alpha()

            if use_colorkey:
                image_surface.set_colorkey(colorkey_color)

            if scale_to:
                image_surface = pygame.transform.scale(image_surface, scale_to)
            
            self._cache[cache_key] = image_surface
            return image_surface

        except pygame.error as e:
            print(f"Error loading image for key '{asset_key}' from path '{image_path}': {e}")
            # Cache the default placeholder for this key to avoid retrying load on every call
            self._cache[cache_key] = self._default_placeholder_surface
            return self._default_placeholder_surface

# Global instance (or pass it around)
# For simplicity in this example, a global instance can be created.
# In a larger game, dependency injection (passing asset_manager to classes) is often preferred.
# asset_manager = AssetManager()
