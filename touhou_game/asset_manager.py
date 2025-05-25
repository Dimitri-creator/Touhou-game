import pygame
import json

GAME_ASSETS = {}

def load_asset_config(config_path="assets.json"):
    """
    Loads the asset configuration file.
    """
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print(f"Error: Asset configuration file not found at {config_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from {config_path}")
        return {}

def load_image(image_path, use_alpha=True):
    """
    Loads an image from the given path.
    """
    try:
        image = pygame.image.load(image_path)
        if use_alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()
        return image
    except pygame.error as e:
        print(f"Failed to load image: {image_path} - {e}")
        return None

def preload_player_assets(player_name, config):
    """
    Preloads player assets based on the configuration.
    Stores loaded assets in GAME_ASSETS.
    """
    if player_name not in config:
        print(f"Error: Player '{player_name}' not found in asset config.")
        return

    player_assets_config = config[player_name]
    # GAME_ASSETS[player_name] = {} # Old structure

    for key, value in player_assets_config.items():
        asset_key_name = f"{player_name}_{key}" # e.g., "reimu_idle"
        if isinstance(value, str): # Single image path
            image = load_image(value)
            if image:
                GAME_ASSETS[asset_key_name] = image
        elif isinstance(value, list): # List of image paths (e.g., for animations)
            images = []
            for path in value:
                image = load_image(path)
                if image:
                    images.append(image)
            if images: # Only add if some images were loaded
                GAME_ASSETS[asset_key_name] = images
    
if __name__ == '__main__':
    pygame.init() # Initialize Pygame for image loading in test
    # Example usage for testing (optional, can be removed or commented out)
    print("Testing asset manager...")
    
    # Create a dummy assets.json for testing if it doesn't exist
    # This is just for isolated testing of asset_manager.py
    try:
        with open("assets.json", "r") as f:
            json.load(f)
    except FileNotFoundError:
        print("Creating dummy assets.json for testing asset_manager.py")
        dummy_config_content = {
            "player": {
                "reimu": {
                    "idle": "assets/player/reimu_idle.png",
                    "moving": [
                        "assets/player/reimu_move_0.png",
                        "assets/player/reimu_move_1.png"
                    ]
                }
            }
        }
        with open("assets.json", "w") as f:
            json.dump(dummy_config_content, f, indent=4)
    
    config = load_asset_config() # Load from default "assets.json"
    print("\nLoaded asset config:")
    print(config)

    if config and "player" in config: # Check if "player" key exists
        print("\nPreloading Reimu assets...")
        # Pass the "reimu" specific part of the config: config["player"]
        # The function expects the config for a single player, e.g., config["player"]["reimu"]
        if "reimu" in config["player"]:
            preload_player_assets("reimu", config["player"]) 
            print("\nGAME_ASSETS after preloading Reimu:")
            # This will print object references, not the images themselves
            for asset_key, asset_value in GAME_ASSETS.items(): # Iterate directly over GAME_ASSETS
                if asset_key.startswith("reimu_"): # Filter for Reimu's assets
                    if isinstance(asset_value, list):
                         print(f"  {asset_key}: {len(asset_value)} images loaded (references: {asset_value})")
                    else:
                         print(f"  {asset_key}: {asset_value}")
        else:
            print("Error: 'reimu' key not found under 'player' in asset config.")
    else:
        print("\nSkipping preload_player_assets due to missing 'player' key in config entries.")

    # Test loading a non-existent image
    print("\nTesting loading a non-existent image:")
    non_existent_image = load_image("path/to/non_existent_image.png")
    print(f"Result of loading non-existent image: {non_existent_image}")

    pygame.quit() # Quit Pygame after testing
    print("\nAsset manager test finished.")


def preload_bullet_sprites(bullet_config):
    """
    Preloads bullet sprites based on the configuration.
    Stores loaded assets in GAME_ASSETS.
    """
    if not bullet_config:
        print("Error: Bullet sprite configuration is empty or not found.")
        return

    print("\nPreloading bullet sprites...")
    for key, path in bullet_config.items():
        asset_key_name = f"bullet_{key}" # e.g., "bullet_reimu_needle"
        image = load_image(path)
        if image:
            GAME_ASSETS[asset_key_name] = image
            print(f"  Loaded bullet sprite: {asset_key_name} from {path}")
        else:
            print(f"  Failed to load bullet sprite: {asset_key_name} from {path}")

# Update the test block in asset_manager.py
if __name__ == '__main__':
    pygame.init() # Initialize Pygame for image loading in test
    print("Testing asset manager...")
    
    # Create a dummy assets.json for testing if it doesn't exist
    dummy_assets_json_path = "assets.json"
    try:
        with open(dummy_assets_json_path, "r") as f:
            json.load(f)
    except FileNotFoundError:
        print(f"Creating dummy {dummy_assets_json_path} for testing asset_manager.py")
        dummy_config_content = {
            "player": {
                "reimu": {
                    "idle": "assets/player/reimu_idle.png",
                    "moving": [
                        "assets/player/reimu_move_0.png",
                        "assets/player/reimu_move_1.png"
                    ]
                }
            },
            "bullet_sprites": {
                "reimu_needle": "assets/bullets/reimu_needle.png",
                "reimu_homing_amulet": "assets/bullets/reimu_homing_amulet.png"
            }
        }
        with open(dummy_assets_json_path, "w") as f:
            json.dump(dummy_config_content, f, indent=4)
        
        # Create dummy image files for the test if they don't exist
        # These paths must match what's in dummy_config_content
        dummy_player_dir = "assets/player"
        dummy_bullet_dir = "assets/bullets"
        import os
        os.makedirs(dummy_player_dir, exist_ok=True)
        os.makedirs(dummy_bullet_dir, exist_ok=True)

        # Use a simple way to create tiny placeholder PNGs if imagemagick 'convert' isn't available or reliable
        def create_dummy_png(path, size=(10,10), color=(0,0,0)):
            try:
                s = pygame.Surface(size)
                s.fill(color)
                pygame.image.save(s, path)
                print(f"Created dummy PNG: {path}")
            except Exception as e:
                print(f"Could not create dummy PNG {path} using Pygame: {e}")

        # Check and create dummy images
        dummy_images_to_create = {
            "assets/player/reimu_idle.png": ((32,48), (0,0,255)), # blue
            "assets/player/reimu_move_0.png": ((32,48), (173,216,230)), # lightblue
            "assets/player/reimu_move_1.png": ((32,48), (0,255,255)), # cyan
            "assets/bullets/reimu_needle.png": ((5,15), (255,192,203)), # pink
            "assets/bullets/reimu_homing_amulet.png": ((10,10), (144,238,144)), # lightgreen
        }
        for img_path, (size, color) in dummy_images_to_create.items():
            if not os.path.exists(img_path):
                 create_dummy_png(img_path, size, color)


    config = load_asset_config(dummy_assets_json_path) 
    print("\nLoaded asset config:")
    print(config)

    if config and "player" in config:
        print("\nPreloading Reimu player assets...")
        if "reimu" in config["player"]:
            preload_player_assets("reimu", config["player"]) 
            print("\nGAME_ASSETS after preloading Reimu:")
            for asset_key, asset_value in GAME_ASSETS.items():
                if asset_key.startswith("reimu_"):
                    if isinstance(asset_value, list):
                         print(f"  {asset_key}: {len(asset_value)} images loaded")
                    else:
                         print(f"  {asset_key}: {asset_value}")
        else:
            print("Error: 'reimu' key not found under 'player' in asset config.")
    else:
        print("\nSkipping preload_player_assets due to missing 'player' key in config entries.")

    # Test preloading bullet sprites
    if config and "bullet_sprites" in config:
        preload_bullet_sprites(config["bullet_sprites"])
        print("\nGAME_ASSETS after preloading bullet sprites:")
        for asset_key, asset_value in GAME_ASSETS.items():
            if asset_key.startswith("bullet_"):
                print(f"  {asset_key}: {asset_value}")
    else:
        print("\nSkipping preload_bullet_sprites due to missing 'bullet_sprites' key in config.")


    # Test loading a non-existent image
    print("\nTesting loading a non-existent image:")
    non_existent_image = load_image("path/to/non_existent_image.png")
    print(f"Result of loading non-existent image: {non_existent_image}")
    
    pygame.quit()
    print("\nAsset manager test finished.")


def preload_item_sprites(item_config):
    """
    Preloads item sprites based on the configuration.
    Stores loaded assets in GAME_ASSETS.
    """
    if not item_config:
        print("Error: Item sprite configuration is empty or not found.")
        return

    print("\nPreloading item sprites...")
    for item_type, path in item_config.items(): # e.g., item_type = "point"
        asset_key_name = f"item_{item_type}" # e.g., "item_point"
        image = load_image(path)
        if image:
            GAME_ASSETS[asset_key_name] = image
            print(f"  Loaded item sprite: {asset_key_name} from {path}")
        else:
            print(f"  Failed to load item sprite: {asset_key_name} from {path}")

# Update the test block in asset_manager.py
if __name__ == '__main__':
    pygame.init() # Initialize Pygame for image loading in test
    print("Testing asset manager...")
    
    dummy_assets_json_path = "assets.json"
    try:
        with open(dummy_assets_json_path, "r") as f:
            json.load(f)
    except FileNotFoundError:
        print(f"Creating dummy {dummy_assets_json_path} for testing asset_manager.py")
        dummy_config_content = {
            "player": {
                "reimu": {
                    "idle": "assets/player/reimu_idle.png",
                    "moving": ["assets/player/reimu_move_0.png", "assets/player/reimu_move_1.png"]
                }
            },
            "bullet_sprites": {
                "reimu_needle": "assets/bullets/reimu_needle.png",
                "reimu_homing_amulet": "assets/bullets/reimu_homing_amulet.png"
            },
            "enemy_sprites": { 
                "zako_type1": {
                    "default": "assets/enemies/zako_type1_default.png"
                }
            },
            "item_sprites": { # Added for testing preload_item_sprites
                "point": "assets/items/point_item.png",
                "power": "assets/items/power_item.png"
            }
        }
        with open(dummy_assets_json_path, "w") as f:
            json.dump(dummy_config_content, f, indent=4)
        
        import os
        dummy_player_dir = "assets/player"
        dummy_bullet_dir = "assets/bullets"
        dummy_enemy_dir = "assets/enemies"
        dummy_item_dir = "assets/items" # Added
        os.makedirs(dummy_player_dir, exist_ok=True)
        os.makedirs(dummy_bullet_dir, exist_ok=True)
        os.makedirs(dummy_enemy_dir, exist_ok=True)
        os.makedirs(dummy_item_dir, exist_ok=True) # Added


        def create_dummy_png(path, size=(10,10), color=(0,0,0)):
            try:
                s = pygame.Surface(size)
                s.fill(color)
                pygame.image.save(s, path)
                print(f"Created dummy PNG: {path}")
            except Exception as e:
                print(f"Could not create dummy PNG {path} using Pygame: {e}")

        dummy_images_to_create = {
            "assets/player/reimu_idle.png": ((32,48), (0,0,255)),
            "assets/player/reimu_move_0.png": ((32,48), (173,216,230)),
            "assets/player/reimu_move_1.png": ((32,48), (0,255,255)),
            "assets/bullets/reimu_needle.png": ((5,15), (255,192,203)),
            "assets/bullets/reimu_homing_amulet.png": ((10,10), (144,238,144)),
            "assets/enemies/zako_type1_default.png": ((32,32), (128,0,128)),
            "assets/items/point_item.png": ((12,12), (0,0,255)), # blue for point
            "assets/items/power_item.png": ((12,12), (255,0,0)), # red for power
        }
        for img_path, (size, color) in dummy_images_to_create.items():
            if not os.path.exists(img_path):
                 create_dummy_png(img_path, size, color)

    config = load_asset_config(dummy_assets_json_path) 
    print("\nLoaded asset config:")
    print(config)

    # ... (player, bullet, enemy preload calls and print logic remain the same) ...
    if config and "player" in config:
        if "reimu" in config["player"]:
            preload_player_assets("reimu", config["player"]) 

    if config and "bullet_sprites" in config:
        preload_bullet_sprites(config["bullet_sprites"])

    if config and "enemy_sprites" in config:
        preload_enemy_sprites(config["enemy_sprites"])
        
    # Test preloading item sprites
    if config and "item_sprites" in config:
        preload_item_sprites(config["item_sprites"])
        print("\nGAME_ASSETS after preloading item sprites:")
        for asset_key, asset_value in GAME_ASSETS.items():
            if asset_key.startswith("item_"):
                print(f"  {asset_key}: {asset_value}")
    else:
        print("\nSkipping preload_item_sprites due to missing 'item_sprites' key in config.")

    print("\nTesting loading a non-existent image:")
    non_existent_image = load_image("path/to/non_existent_image.png")
    print(f"Result of loading non-existent image: {non_existent_image}")
    
    pygame.quit()
    print("\nAsset manager test finished.")


def preload_enemy_sprites(enemy_config):
    """
    Preloads enemy sprites based on the configuration.
    Stores loaded assets in GAME_ASSETS.
    """
    if not enemy_config:
        print("Error: Enemy sprite configuration is empty or not found.")
        return

    print("\nPreloading enemy sprites...")
    for enemy_type, sprites in enemy_config.items(): # e.g., enemy_type = "zako_type1"
        if not isinstance(sprites, dict):
            print(f"  Warning: Expected a dictionary of sprites for enemy type '{enemy_type}', got {type(sprites)}. Skipping.")
            continue
        for sprite_key, path in sprites.items(): # e.g., sprite_key = "default"
            asset_key_name = f"enemy_{enemy_type}_{sprite_key}" # e.g., "enemy_zako_type1_default"
            image = load_image(path)
            if image:
                GAME_ASSETS[asset_key_name] = image
                print(f"  Loaded enemy sprite: {asset_key_name} from {path}")
            else:
                print(f"  Failed to load enemy sprite: {asset_key_name} from {path}")

# Update the test block in asset_manager.py
if __name__ == '__main__':
    pygame.init() # Initialize Pygame for image loading in test
    print("Testing asset manager...")
    
    dummy_assets_json_path = "assets.json"
    try:
        with open(dummy_assets_json_path, "r") as f:
            json.load(f)
    except FileNotFoundError:
        print(f"Creating dummy {dummy_assets_json_path} for testing asset_manager.py")
        dummy_config_content = {
            "player": {
                "reimu": {
                    "idle": "assets/player/reimu_idle.png",
                    "moving": ["assets/player/reimu_move_0.png", "assets/player/reimu_move_1.png"]
                }
            },
            "bullet_sprites": {
                "reimu_needle": "assets/bullets/reimu_needle.png",
                "reimu_homing_amulet": "assets/bullets/reimu_homing_amulet.png"
            },
            "enemy_sprites": { # Added for testing preload_enemy_sprites
                "zako_type1": {
                    "default": "assets/enemies/zako_type1_default.png"
                }
            }
        }
        with open(dummy_assets_json_path, "w") as f:
            json.dump(dummy_config_content, f, indent=4)
        
        import os
        dummy_player_dir = "assets/player"
        dummy_bullet_dir = "assets/bullets"
        dummy_enemy_dir = "assets/enemies" # Added
        os.makedirs(dummy_player_dir, exist_ok=True)
        os.makedirs(dummy_bullet_dir, exist_ok=True)
        os.makedirs(dummy_enemy_dir, exist_ok=True) # Added

        def create_dummy_png(path, size=(10,10), color=(0,0,0)):
            try:
                s = pygame.Surface(size)
                s.fill(color)
                pygame.image.save(s, path)
                print(f"Created dummy PNG: {path}")
            except Exception as e:
                print(f"Could not create dummy PNG {path} using Pygame: {e}")

        dummy_images_to_create = {
            "assets/player/reimu_idle.png": ((32,48), (0,0,255)),
            "assets/player/reimu_move_0.png": ((32,48), (173,216,230)),
            "assets/player/reimu_move_1.png": ((32,48), (0,255,255)),
            "assets/bullets/reimu_needle.png": ((5,15), (255,192,203)),
            "assets/bullets/reimu_homing_amulet.png": ((10,10), (144,238,144)),
            "assets/enemies/zako_type1_default.png": ((32,32), (128,0,128)), # purple for zako
        }
        for img_path, (size, color) in dummy_images_to_create.items():
            if not os.path.exists(img_path):
                 create_dummy_png(img_path, size, color)

    config = load_asset_config(dummy_assets_json_path) 
    print("\nLoaded asset config:")
    print(config)

    if config and "player" in config:
        print("\nPreloading Reimu player assets...")
        if "reimu" in config["player"]:
            preload_player_assets("reimu", config["player"]) 
            # ... (print logic for player assets remains the same)
    # ... (other preload calls remain the same)

    # Test preloading bullet sprites
    if config and "bullet_sprites" in config:
        preload_bullet_sprites(config["bullet_sprites"])
        # ... (print logic for bullet assets remains the same)

    # Test preloading enemy sprites
    if config and "enemy_sprites" in config:
        preload_enemy_sprites(config["enemy_sprites"])
        print("\nGAME_ASSETS after preloading enemy sprites:")
        for asset_key, asset_value in GAME_ASSETS.items():
            if asset_key.startswith("enemy_"):
                print(f"  {asset_key}: {asset_value}")
    else:
        print("\nSkipping preload_enemy_sprites due to missing 'enemy_sprites' key in config.")

    print("\nTesting loading a non-existent image:")
    non_existent_image = load_image("path/to/non_existent_image.png")
    print(f"Result of loading non-existent image: {non_existent_image}")
    
    pygame.quit()
    print("\nAsset manager test finished.")
