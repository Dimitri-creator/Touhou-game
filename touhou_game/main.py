import pygame
import random # Import random
from .player import Player # Import the Player class
from .enemies import ZakoEnemy, ReisenBoss # Import ZakoEnemy and ReisenBoss
from .items import Item # Import Item class
from .asset_manager import load_asset_config, preload_player_assets, preload_bullet_sprites, preload_enemy_sprites, preload_item_sprites, preload_sfx, GAME_ASSETS # Import asset functions and GAME_ASSETS
from .ui import draw_game_ui, UI_FONT, TEXT_COLOR, draw_text # Import UI drawing function and constants
from .sound_manager import init_mixer, play_sound, set_sfx_volume, get_sfx_volume # Import sound functions

# Initialize Pygame
pygame.init()
init_mixer() # Initialize the sound mixer

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Touhou Game Prototype"
DARK_GRAY = (50, 50, 50)

# Game State Constants
GAME_STATE_TITLE = "title_screen"
GAME_STATE_DIFFICULTY = "difficulty_select" # New state
GAME_STATE_GAMEPLAY = "gameplay"
GAME_STATE_OPTIONS = "options"
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

# Options Screen Variables
options_menu_texts = ["SFX Volume:", "BGM Volume:", "Back"]
selected_option_index = 0 
current_sfx_display_volume = int(get_sfx_volume() * 10)

# Difficulty Screen Variables
difficulty_options = ["Easy", "Normal", "Hard", "Lunatic"]
selected_difficulty_index = 0
game_difficulty = "Normal" # Default difficulty
ZAKO_ENEMY_HEALTH_BASE = {"Easy": 5, "Normal": 10, "Hard": 15, "Lunatic": 20}
current_zako_health = ZAKO_ENEMY_HEALTH_BASE[game_difficulty]


# Global Game Variables
game_player = None 
player_score = 0
player_lives = 3
player_bombs = 2
player_graze = 0
game_over = False 

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

# Asset Loading
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
if asset_config and "sfx" in asset_config:
    preload_sfx(asset_config['sfx'])
else:
    print("Error: Could not preload SFX. Check asset_config.json and its loading.")

# Screen and Clock
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)
clock = pygame.time.Clock()

def reset_game_state():
    global game_player, player_score, player_lives, player_bombs, player_graze, game_over
    global active_enemies, active_enemy_bullets, active_items
    global reisen_instance, reisen_boss_active, enemy_spawn_timer
    global current_zako_health, game_difficulty # Added for difficulty

    player_score = 0
    player_lives = 3
    player_bombs = 2
    player_graze = 0
    game_over = False
    
    current_zako_health = ZAKO_ENEMY_HEALTH_BASE[game_difficulty] # Update Zako health based on difficulty

    if game_player is None:
        essential_player_assets = ['reimu_idle', 'reimu_moving']
        essential_bullet_assets = ['bullet_reimu_needle', 'bullet_reimu_homing_amulet']
        all_player_essentials_loaded = all(asset in GAME_ASSETS for asset in essential_player_assets) and \
                                       all(asset in GAME_ASSETS for asset in essential_bullet_assets)
        if all_player_essentials_loaded:
            game_player = Player(PLAYER_START_X, PLAYER_START_Y)
        else:
            print("CRITICAL ERROR: Cannot create player - essential assets missing from GAME_ASSETS.")
            pygame.quit()
            exit()
    
    game_player.power_level = 0
    game_player.reset_position(PLAYER_START_X, PLAYER_START_Y)
    game_player.is_invincible = False
    game_player.invincibility_timer = 0
    game_player.bullets.clear()

    active_enemies.clear()
    active_enemy_bullets.clear()
    active_items.clear()

    reisen_instance = None
    reisen_boss_active = False
    enemy_spawn_timer = 0


def handle_title_screen_input():
    global selected_menu_index, current_game_state, running, selected_option_index, selected_difficulty_index
    
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
                    current_game_state = GAME_STATE_DIFFICULTY # Go to difficulty select
                    selected_difficulty_index = 0 # Reset for difficulty screen
                elif selected_menu_index == 1: # Options
                    current_game_state = GAME_STATE_OPTIONS
                    selected_option_index = 0 
                elif selected_menu_index == 2: # Quit
                    running = False

def draw_title_screen():
    screen.fill((0, 0, 30))
    title_surface = title_font.render("Touhou Project Clone", True, TEXT_COLOR_TITLE)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    screen.blit(title_surface, title_rect)
    menu_start_y = SCREEN_HEIGHT // 2
    for index, option_text in enumerate(menu_options):
        color = SELECTED_COLOR_MENU if index == selected_menu_index else TEXT_COLOR_MENU
        option_surface = menu_font.render(option_text, True, color)
        option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, menu_start_y + index * 60))
        screen.blit(option_surface, option_rect)

def handle_difficulty_screen_input():
    global current_game_state, selected_difficulty_index, game_difficulty, running
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_difficulty_index = (selected_difficulty_index - 1) % len(difficulty_options)
            elif event.key == pygame.K_DOWN:
                selected_difficulty_index = (selected_difficulty_index + 1) % len(difficulty_options)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_z:
                game_difficulty = difficulty_options[selected_difficulty_index]
                print(f"Difficulty selected: {game_difficulty}")
                reset_game_state() # Reset state using the new game_difficulty
                current_game_state = GAME_STATE_GAMEPLAY
            elif event.key == pygame.K_ESCAPE:
                current_game_state = GAME_STATE_TITLE

def draw_difficulty_screen():
    global selected_difficulty_index
    screen.fill((30, 0, 30))  # Dark purple background
    
    title_surface = title_font.render("Select Difficulty", True, TEXT_COLOR_TITLE)
    title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    screen.blit(title_surface, title_rect)

    menu_start_y = SCREEN_HEIGHT // 2
    for index, option_text in enumerate(difficulty_options):
        color = SELECTED_COLOR_MENU if index == selected_difficulty_index else TEXT_COLOR_MENU
        option_surface = menu_font.render(option_text, True, color)
        option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, menu_start_y + index * 60))
        screen.blit(option_surface, option_rect)


def handle_options_screen_input():
    global current_game_state, selected_option_index, current_sfx_display_volume, running
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                selected_option_index = (selected_option_index - 1) % len(options_menu_texts)
            elif event.key == pygame.K_DOWN:
                selected_option_index = (selected_option_index + 1) % len(options_menu_texts)
            elif event.key == pygame.K_LEFT:
                if options_menu_texts[selected_option_index] == "SFX Volume:":
                    current_sfx_display_volume = max(0, current_sfx_display_volume - 1)
                    set_sfx_volume(current_sfx_display_volume / 10.0)
                    play_sound("enemy_hit") 
            elif event.key == pygame.K_RIGHT:
                if options_menu_texts[selected_option_index] == "SFX Volume:":
                    current_sfx_display_volume = min(10, current_sfx_display_volume + 1)
                    set_sfx_volume(current_sfx_display_volume / 10.0)
                    play_sound("enemy_hit")
            elif event.key == pygame.K_RETURN or event.key == pygame.K_z:
                if options_menu_texts[selected_option_index] == "Back":
                    current_game_state = GAME_STATE_TITLE
            elif event.key == pygame.K_ESCAPE:
                current_game_state = GAME_STATE_TITLE

def draw_options_screen():
    global selected_option_index, current_sfx_display_volume 
    screen.fill((30, 30, 60)) 
    options_title_surface = title_font.render("Options", True, TEXT_COLOR_TITLE)
    options_title_rect = options_title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6))
    screen.blit(options_title_surface, options_title_rect)
    menu_start_y = SCREEN_HEIGHT // 3
    for index, option_text_label in enumerate(options_menu_texts):
        display_text = option_text_label
        if option_text_label == "SFX Volume:":
            display_text += f" < {current_sfx_display_volume} >"
        color = SELECTED_COLOR_MENU if index == selected_option_index else TEXT_COLOR_MENU
        option_surface = menu_font.render(display_text, True, color)
        option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, menu_start_y + index * 70))
        screen.blit(option_surface, option_rect)

def handle_game_over_input():
    global current_game_state, running
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_z:
                current_game_state = GAME_STATE_TITLE

def draw_game_over_screen():
    screen.fill(DARK_GRAY)
    game_over_text_surface = title_font.render("GAME OVER", True, (255, 0, 0))
    text_rect = game_over_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(game_over_text_surface, text_rect)
    instruction_font = menu_font
    instruction_text_surface = instruction_font.render("Press Enter or Z to Return to Title", True, TEXT_COLOR_MENU)
    instruction_rect = instruction_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
    screen.blit(instruction_text_surface, instruction_rect)

# Check essential assets before attempting to create Player for the first time
essential_assets_list = ['reimu_idle', 'reimu_moving', 'bullet_reimu_needle', 'bullet_reimu_homing_amulet', 
                         'enemy_zako_type1_default', 'item_point', 'item_power', 'enemy_reisen_boss_default']
all_essential_assets_loaded = all(asset in GAME_ASSETS for asset in essential_assets_list)

if all_essential_assets_loaded:
    if game_player is None:
         game_player = Player(PLAYER_START_X, PLAYER_START_Y)
else:
    print("CRITICAL ERROR: Essential assets not loaded at startup. Exiting.")
    pygame.quit()
    exit()

running = True
while running:
    if current_game_state == GAME_STATE_TITLE:
        handle_title_screen_input()
        draw_title_screen()
    elif current_game_state == GAME_STATE_DIFFICULTY: # New state handling
        handle_difficulty_screen_input()
        draw_difficulty_screen()
    elif current_game_state == GAME_STATE_GAMEPLAY:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        pressed_keys = pygame.key.get_pressed()

        if not reisen_boss_active and reisen_instance is None and player_score >= BOSS_SPAWN_SCORE:
            reisen_img = GAME_ASSETS.get('enemy_reisen_boss_default')
            if reisen_img:
                reisen_instance = ReisenBoss(SCREEN_WIDTH // 2, -reisen_img.get_height() // 2, 
                                             health=200, image_surface=reisen_img, 
                                             screen_width=SCREEN_WIDTH, screen_height=SCREEN_HEIGHT)
                reisen_boss_active = True
                print("Reisen Boss has spawned!")

        if not reisen_boss_active:
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= enemy_spawn_cooldown:
                enemy_spawn_timer = 0
                spawn_x = random.randint(50, SCREEN_WIDTH - 50)
                spawn_y = -30
                zako_image = GAME_ASSETS['enemy_zako_type1_default']
                active_enemies.append(ZakoEnemy(spawn_x, spawn_y, current_zako_health, zako_image, speed=2)) # Use current_zako_health

        game_player.update(pressed_keys, SCREEN_WIDTH, SCREEN_HEIGHT)

        for bullet in game_player.bullets[:]: 
            bullet_removed_this_frame = False
            if reisen_boss_active and reisen_instance and reisen_instance.health > 0 and \
               (reisen_instance.state == "active" or reisen_instance.state == "spell_card_active" or reisen_instance.state == "spell_card_intro"):
                if bullet.rect.colliderect(reisen_instance.rect):
                    if bullet in game_player.bullets: game_player.bullets.remove(bullet)
                    bullet_removed_this_frame = True
                    play_sound("enemy_hit")
                    if reisen_instance.take_damage(1):
                        reisen_instance.state = "defeating"
                        play_sound("enemy_destroy")
                        print("Reisen Defeated!")
                    if bullet_removed_this_frame: continue
            
            if not bullet_removed_this_frame:
                for enemy in active_enemies[:]:
                    if bullet.rect.colliderect(enemy.rect):
                        if bullet in game_player.bullets: game_player.bullets.remove(bullet)
                        play_sound("enemy_hit")
                        if enemy.take_damage(1):
                            if enemy in active_enemies: active_enemies.remove(enemy)
                            play_sound("enemy_destroy")
                            if random.random() < 0.75:
                                img = GAME_ASSETS.get('item_point'); active_items.append(Item(enemy.rect.centerx, enemy.rect.centery, "point", img)) if img else None
                            if random.random() < 0.25:
                                img = GAME_ASSETS.get('item_power'); active_items.append(Item(enemy.rect.centerx, enemy.rect.centery, "power", img)) if img else None
                        break
        
        for enemy in active_enemies[:]: 
            enemy.update() 
            if hasattr(enemy, 'fired_bullets_cache') and enemy.fired_bullets_cache:
                active_enemy_bullets.extend(enemy.fired_bullets_cache)
            if enemy.is_offscreen(SCREEN_WIDTH, SCREEN_HEIGHT):
                if enemy in active_enemies: active_enemies.remove(enemy)
        
        if reisen_boss_active and reisen_instance:
            if reisen_instance.health > 0:
                 reisen_instance.update(game_player.rect.centerx, game_player.rect.centery)
            if hasattr(reisen_instance, 'fired_bullets_cache') and reisen_instance.fired_bullets_cache:
                active_enemy_bullets.extend(reisen_instance.fired_bullets_cache)

        for bullet in active_enemy_bullets[:]:
            bullet.update()
            if bullet.is_offscreen(SCREEN_WIDTH, SCREEN_HEIGHT): active_enemy_bullets.remove(bullet)
                
        for item_obj in active_items[:]:
            item_obj.update()
            if item_obj.is_offscreen(SCREEN_HEIGHT): active_items.remove(item_obj)

        for bullet in active_enemy_bullets[:]:
            if bullet.rect.colliderect(game_player.rect): 
                if bullet in active_enemy_bullets: active_enemy_bullets.remove(bullet)
                if game_player.handle_hit():
                    player_lives -= 1
                    play_sound("player_get_hit")
                    print(f"Player Hit! Lives remaining: {player_lives}")
                    if player_lives < 0:
                        game_over = True 
                        current_game_state = GAME_STATE_GAME_OVER 
                        print("Game Over!")
                    else:
                        game_player.reset_position(PLAYER_START_X, PLAYER_START_Y)
                        active_enemy_bullets.clear()
                break 

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
        handle_options_screen_input() 
        draw_options_screen() 

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
