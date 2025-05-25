import pygame
import random # Import random
from player import Player # Import the Player class
from enemies import ZakoEnemy, ReisenBoss # Import ZakoEnemy and ReisenBoss
from items import Item # Import Item class
from asset_manager import load_asset_config, preload_player_assets, preload_bullet_sprites, preload_enemy_sprites, preload_item_sprites, GAME_ASSETS # Import asset functions and GAME_ASSETS
from ui import draw_game_ui, UI_FONT, TEXT_COLOR, draw_text # Import UI drawing function and constants

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Touhou Game Prototype"
DARK_GRAY = (50, 50, 50)

# Game State Constants
GAME_STATE_TITLE = "title_screen"
GAME_STATE_GAMEPLAY = "gameplay"
GAME_STATE_OPTIONS = "options" # For future
GAME_STATE_GAME_OVER = "game_over"
current_game_state = GAME_STATE_TITLE

# Title Screen Variables
title_font = pygame.font.Font(None, 80)
menu_font = pygame.font.Font(None, 50)
menu_options = ["Start Game", "Options", "Quit"]
selected_menu_index = 0
TEXT_COLOR_TITLE = (200, 200, 255) # Light blue for title
TEXT_COLOR_MENU = (220, 220, 220) # Off-white for menu
SELECTED_COLOR_MENU = (255, 255, 100) # Yellow for selected

# Global Game Variables (initialized to default/empty states)
game_player = None # Player object, will be initialized in reset_game_state
player_score = 0
player_lives = 3
player_bombs = 2
player_graze = 0
game_over = False # Will be set to True inside gameplay if player_lives < 0

active_enemies = []
active_enemy_bullets = []
active_items = []

reisen_instance = None
reisen_boss_active = False
enemy_spawn_timer = 0

BOSS_SPAWN_SCORE = 500
PLAYER_START_X = SCREEN_WIDTH // 2 - 16
PLAYER_START_Y = SCREEN_HEIGHT - 60
enemy_spawn_cooldown = 120

# Asset Loading (should happen once)
asset_config = load_asset_config()
print("Loaded Asset Configuration:")
print(asset_config)
if asset_config and "player" in asset_config and "reimu" in asset_config["player"]:
    preload_player_assets('reimu', asset_config["player"])
if asset_config and "bullet_sprites" in asset_config:
    preload_bullet_sprites(asset_config['bullet_sprites'])
if asset_config and "enemy_sprites" in asset_config:
    preload_enemy_sprites(asset_config['enemy_sprites'])
if asset_config and "item_sprites" in asset_config:
    preload_item_sprites(asset_config['item_sprites'])

# Screen and Clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)
clock = pygame.time.Clock()

def reset_game_state():
    global game_player, player_score, player_lives, player_bombs, player_graze, game_over
    global active_enemies, active_enemy_bullets, active_items
    global reisen_instance, reisen_boss_active, enemy_spawn_timer

    player_score = 0
    player_lives = 3
    player_bombs = 2
    player_graze = 0
    game_over = False

    if game_player is None:
        # Ensure essential assets are loaded before creating Player
        essential_player_assets = ['reimu_idle', 'reimu_moving']
        essential_bullet_assets = ['bullet_reimu_needle', 'bullet_reimu_homing_amulet']
        # No need to check enemy/item assets here as player creation doesn't directly depend on them
        all_player_essentials_loaded = all(asset in GAME_ASSETS for asset in essential_player_assets) and \
                                       all(asset in GAME_ASSETS for asset in essential_bullet_assets)
        if all_player_essentials_loaded:
            game_player = Player(PLAYER_START_X, PLAYER_START_Y)
        else:
            print("CRITICAL ERROR: Cannot create player - essential assets missing from GAME_ASSETS.")
            pygame.quit()
            exit() # Or handle more gracefully
    
    game_player.power_level = 0
    game_player.reset_position(PLAYER_START_X, PLAYER_START_Y)
    game_player.is_invincible = False
    game_player.invincibility_timer = 0
    game_player.bullets.clear() # Clear player's own bullets

    active_enemies.clear()
    active_enemy_bullets.clear()
    active_items.clear()

    reisen_instance = None
    reisen_boss_active = False
    enemy_spawn_timer = 0


def handle_title_screen_input():
    global selected_menu_index, current_game_state, running
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_menu_index = (selected_menu_index - 1) % len(menu_options)
            elif event.key == pygame.K_DOWN:
                selected_menu_index = (selected_menu_index + 1) % len(menu_options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_z:
                if selected_menu_index == 0: # Start Game
                    reset_game_state() # Reset state before starting gameplay
                    current_game_state = GAME_STATE_GAMEPLAY
                elif selected_menu_index == 1: # Options
                    print("Options selected - TBD")
                elif selected_menu_index == 2: # Quit
                    running = False
    # No need to return values if modifying globals directly

def draw_title_screen():
    screen.fill((0, 0, 30))  # Dark blue background
    
    title_surface = title_font.render("Touhou Project Clone", True, TEXT_COLOR_TITLE)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    screen.blit(title_surface, title_rect)

    menu_start_y = SCREEN_HEIGHT // 2
    for index, option_text in enumerate(menu_options):
        color = SELECTED_COLOR_MENU if index == selected_menu_index else TEXT_COLOR_MENU
        option_surface = menu_font.render(option_text, True, color)
        option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, menu_start_y + index * 60))
        screen.blit(option_surface, option_rect)

def handle_game_over_input():
    global current_game_state, running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_z:
                current_game_state = GAME_STATE_TITLE # Go back to title screen
            # No need to return values if modifying globals directly

def draw_game_over_screen():
    screen.fill(DARK_GRAY) # Or a specific game over background
    game_over_text_surface = title_font.render("GAME OVER", True, (255, 0, 0)) # Red
    text_rect = game_over_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(game_over_text_surface, text_rect)

    instruction_font = menu_font
    instruction_text_surface = instruction_font.render("Press Enter or Z to Return to Title", True, TEXT_COLOR_MENU)
    instruction_rect = instruction_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(instruction_text_surface, instruction_rect)


# Initial call to reset/initialize game_player and other game variables
# This ensures game_player is created before gameplay starts if we directly go to gameplay for testing
# However, with title screen, reset_game_state() will be called upon "Start Game"
# For robustness, let's ensure game_player is at least attempted to be created before the main loop
# if all assets are loaded.
if all_essential_assets_loaded: # This global check was from previous main.py structure
    if game_player is None: # If not created by a direct call to reset_game_state yet
         game_player = Player(PLAYER_START_X, PLAYER_START_Y) # Create a default player
         # This player instance will be properly reset by reset_game_state() when "Start Game" is chosen.
else:
    print("CRITICAL ERROR: Essential assets not loaded at startup. Exiting.")
    pygame.quit()
    exit()


running = True
while running:
    if current_game_state == GAME_STATE_TITLE:
        handle_title_screen_input()
        draw_title_screen()
    elif current_game_state == GAME_STATE_GAMEPLAY:
        # Gameplay event handling (minimal here, player input via get_pressed)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        pressed_keys = pygame.key.get_pressed()

        # Boss Spawning Logic
        if not reisen_boss_active and reisen_instance is None and player_score >= BOSS_SPAWN_SCORE:
            reisen_img = GAME_ASSETS.get('enemy_reisen_boss_default')
            if reisen_img:
                reisen_instance = ReisenBoss(SCREEN_WIDTH // 2, -reisen_img.get_height() // 2, 
                                             health=200, image_surface=reisen_img, 
                                             screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
                reisen_boss_active = True
                print("Reisen Boss has spawned!")

        # Enemy Spawning Logic (Zako)
        if not reisen_boss_active:
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= enemy_spawn_cooldown:
                enemy_spawn_timer = 0
                spawn_x = random.randint(50, SCREEN_WIDTH - 50)
                spawn_y = -30
                zako_image = GAME_ASSETS['enemy_zako_type1_default']
                active_enemies.append(ZakoEnemy(spawn_x, spawn_y, 10, zako_image, speed=2))

        # Update player
        game_player.update(pressed_keys, SCREEN_WIDTH, SCREEN_HEIGHT)

        # Player Bullet and Enemy Collision Detection
        for bullet in game_player.bullets[:]: 
            bullet_removed_this_frame = False
            if reisen_boss_active and reisen_instance and reisen_instance.health > 0 and \
               (reisen_instance.state == "active" or reisen_instance.state == "spell_card_active" or reisen_instance.state == "spell_card_intro"):
                if bullet.rect.colliderect(reisen_instance.rect):
                    if bullet in game_player.bullets: game_player.bullets.remove(bullet)
                    bullet_removed_this_frame = True
                    if reisen_instance.take_damage(1):
                        reisen_instance.state = "defeating"
                        print("Reisen Defeated!")
                    if bullet_removed_this_frame: continue
            
            if not bullet_removed_this_frame:
                for enemy in active_enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        if bullet in game_player.bullets: game_player.bullets.remove(bullet)
                        if enemy.take_damage(1):
                            if enemy in active_enemies: active_enemies.remove(enemy)
                            if random.random() < 0.75:
                                img = GAME_ASSETS.get('item_point'); active_items.append(Item(enemy.rect.centerx, enemy.rect.centery, "point", img)) if img else None
                            if random.random() < 0.25:
                                img = GAME_ASSETS.get('item_power'); active_items.append(Item(enemy.rect.centerx, enemy.rect.centery, "power", img)) if img else None
                        break
        
        # Update enemies and collect their bullets
        for enemy in active_enemies[:]: 
            enemy.update() 
            if hasattr(enemy, 'fired_bullets_cache') and enemy.fired_bullets_cache:
                active_enemy_bullets.extend(enemy.fired_bullets_cache)
            if enemy.is_offscreen(SCREEN_WIDTH, SCREEN_HEIGHT):
                if enemy in active_enemies: active_enemies.remove(enemy)
        
        # Update Boss if active
        if reisen_boss_active and reisen_instance:
            if reisen_instance.health > 0:
                 reisen_instance.update(game_player.rect.centerx, game_player.rect.centery)
            if hasattr(reisen_instance, 'fired_bullets_cache') and reisen_instance.fired_bullets_cache:
                active_enemy_bullets.extend(reisen_instance.fired_bullets_cache)

        # Enemy Bullet Update
        for bullet in active_enemy_bullets[:]:
            bullet.update()
            if bullet.is_offscreen(SCREEN_WIDTH, SCREEN_HEIGHT): active_enemy_bullets.remove(bullet)
                
        # Item Update
        for item_obj in active_items[:]:
            item_obj.update()
            if item_obj.is_offscreen(SCREEN_HEIGHT): active_items.remove(item_obj)

        # Player Collision with Enemy Bullets Loop
        for bullet in active_enemy_bullets[:]:
            if bullet.rect.colliderect(game_player.rect): 
                if bullet in active_enemy_bullets: active_enemy_bullets.remove(bullet)
                if game_player.handle_hit():
                    player_lives -= 1
                    print(f"Player Hit! Lives remaining: {player_lives}")
                    if player_lives < 0:
                        game_over = True # Set internal flag
                        current_game_state = GAME_STATE_GAME_OVER # Change state
                        print("Game Over!")
                    else:
                        game_player.reset_position(PLAYER_START_X, PLAYER_START_Y)
                        active_enemy_bullets.clear()
                break 

        # Player Collision with Items Loop
        for item_obj in active_items[:]:
            if game_player.rect.colliderect(item_obj.rect):
                collected_item_type = item_obj.item_type
                active_items.remove(item_obj)
                if collected_item_type == "power":
                    game_player.increase_power(amount=8)
                elif collected_item_type == "point":
                    player_score += 100
                print(f"Collected {collected_item_type} item! Score: {player_score}, Power: {game_player.power_level}")
                break

        # --- Drawing ---
        screen.fill(DARK_GRAY)
        for item_obj in active_items: item_obj.draw(screen)
        show_hitbox_flag = pressed_keys[pygame.K_LSHIFT] or pressed_keys[pygame.K_RSHIFT]
        game_player.draw(screen, show_hitbox_flag) 
        for enemy in active_enemies: enemy.draw(screen)
        for bullet in active_enemy_bullets: bullet.draw(screen)
        if reisen_boss_active and reisen_instance:
            reisen_instance.draw(screen)
            if reisen_instance.health > 0: reisen_instance.draw_health_bar(screen)
        draw_game_ui(screen, player_score, player_lives, player_bombs, game_player.power_level, player_graze, SCREEN_WIDTH)
        if reisen_boss_active and reisen_instance and (reisen_instance.state == "spell_card_intro" or reisen_instance.state == "spell_card_active"):
            spell_name_surf = UI_FONT.render(reisen_instance.current_spell_card_name, True, TEXT_COLOR)
            spell_name_rect = spell_name_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 5))
            screen.blit(spell_name_surf, spell_name_rect)

    elif current_game_state == GAME_STATE_GAME_OVER:
        handle_game_over_input()
        draw_game_over_screen()
    
    elif current_game_state == GAME_STATE_OPTIONS:
        # Placeholder for options screen
        screen.fill(DARK_GRAY)
        draw_text(screen, "Options - TBD", SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 30, font=title_font)
        # Handle input for options screen (e.g., back to title)
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: current_game_state = GAME_STATE_TITLE


    pygame.display.flip()
    clock.tick(60)

pygame.quit()
