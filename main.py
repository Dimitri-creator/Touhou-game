import pygame

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Touhou Project Clone"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Game states
TITLE_SCREEN = 0
DIFFICULTY_SELECT = 1
OPTIONS_SCREEN = 2
GAMEPLAY = 3
GAME_OVER = 4 # Covers both Game Over and Game Clear for now

current_state = TITLE_SCREEN
selected_difficulty = "Normal" # Default difficulty

# Setup screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(SCREEN_TITLE)

import random

# Font for title screen
font = pygame.font.Font(None, 74)

# Import classes
from src.player import Player
from src.enemy import ZakoEnemy, EnemyBullet, Reisen, Kaguya 
from src.items import Item, create_item, TYPE_SCORE, TYPE_POWER, TYPE_BOMB
from src.assets import AssetManager # Import AssetManager

# Screen flash for player spell card & Kaguya phase transition
screen_flash_alpha = 0
screen_flash_duration = 15 
screen_flash_timer = 0
PHASE_TRANSITION_FLASH_DURATION = 30 # Longer flash for phase transitions

# Enemy spawning
enemy_spawn_delay = 2000 
last_enemy_spawn_time = 0 
reisen_spawn_time = 15000 # Reisen appears after 15 seconds (or set to 1000 for quick test)
reisen_instance = None
reisen_defeated_effect_timer = 0
REISEN_DEFEATED_EFFECT_DURATION = 120 

kaguya_instance = None
KAGUYA_SPAWN_DELAY_AFTER_REISEN = 3000 # Kaguya appears 3s after Reisen's defeat effect ends
kaguya_spawn_timer = 0 # Timer to track this delay
kaguya_defeat_effect_timer = 0
KAGUYA_DEFEAT_EFFECT_DURATION = 180 # 3 seconds for Kaguya's defeat

# UI Font
ui_font = None 
big_font = None 
menu_font = None # For menu items

# Menu settings
menu_options_title = ["Game Start", "Options", "Quit"]
menu_options_difficulty = ["Easy", "Normal", "Hard", "Lunatic"]
menu_options_options_page = ["BGM Volume: [||||----]", "SFX Volume: [|||-----]", "Screen: [Windowed]", "Controls: View/Edit", "Reset Data", "Back"]
menu_options_game_over = ["Retry", "Quit to Title"]
menu_options_game_clear = ["Play Again", "Quit to Title"]

current_menu_selection = 0
menu_cursor_image = None # Will be loaded by AssetManager

def draw_text(surface, text, font, color, center_x, y_pos, is_selected=False, asset_manager=None):
    """Helper to draw text, optionally with a cursor."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(center_x, y_pos))
    
    if is_selected:
        cursor_spacing = 20 # Space between cursor and text
        if menu_cursor_image:
            cursor_rect = menu_cursor_image.get_rect(centery=text_rect.centery)
            cursor_rect.right = text_rect.left - cursor_spacing
            surface.blit(menu_cursor_image, cursor_rect)
        else: # Fallback text cursor
            cursor_surf = font.render(">", True, color)
            cursor_rect = cursor_surf.get_rect(centery=text_rect.centery)
            cursor_rect.right = text_rect.left - cursor_spacing
            surface.blit(cursor_surf, cursor_rect)
            
    surface.blit(text_surface, text_rect)

def draw_menu(surface, options, current_selection, font, color, start_y, asset_manager):
    """Draws a generic navigable menu."""
    for i, option_text in enumerate(options):
        draw_text(surface, option_text, font, color, SCREEN_WIDTH // 2, start_y + i * 50, 
                  is_selected=(i == current_selection), asset_manager=asset_manager)

def draw_title_screen_layout(asset_manager):
    screen.fill(BLACK)
    # Game Title/Logo
    logo_image = asset_manager.get_image("ui_logo", scale_to=(400,100))
    if logo_image:
        logo_rect = logo_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(logo_image, logo_rect)
    else: # Fallback text title
        draw_text(screen, "Touhou Clone Game", big_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, asset_manager=asset_manager)
    
    draw_menu(screen, menu_options_title, current_menu_selection, menu_font, WHITE, SCREEN_HEIGHT // 2, asset_manager)

def draw_difficulty_select_layout(asset_manager):
    screen.fill(BLACK)
    draw_text(screen, "Select Difficulty", big_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, asset_manager=asset_manager)
    draw_menu(screen, menu_options_difficulty, current_menu_selection, menu_font, WHITE, SCREEN_HEIGHT // 2, asset_manager)

def draw_options_screen_layout(asset_manager):
    screen.fill(BLACK)
    draw_text(screen, "Options", big_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 6, asset_manager=asset_manager)
    draw_menu(screen, menu_options_options_page, current_menu_selection, menu_font, WHITE, SCREEN_HEIGHT // 3, asset_manager)

def draw_game_over_layout(asset_manager, is_clear):
    screen.fill(BLACK)
    message = "Game Clear!" if is_clear else "Game Over"
    options = menu_options_game_clear if is_clear else menu_options_game_over
    
    draw_text(screen, message, big_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4, asset_manager=asset_manager)
    # Display Score (Placeholder, needs actual score variable)
    # score_text = f"Score: {player.score}" # Assuming player has a score attribute
    # draw_text(screen, score_text, ui_font, WHITE, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50)
    
    draw_menu(screen, options, current_menu_selection, menu_font, WHITE, SCREEN_HEIGHT // 2 + 50, asset_manager)


def draw_health_bar(surface, current_health, max_health, x, y, width, height, color, phase_thresholds=None, current_phase_val=None):
    if current_health < 0: current_health = 0
    
    # Current health fill
    fill_width = (current_health / max_health) * width
    fill_rect = pygame.Rect(x, y, fill_width, height)
    pygame.draw.rect(surface, color, fill_rect)

    # Draw full bar outline
    outline_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, WHITE, outline_rect, 2)


    # Draw phase markers on health bar for Kaguya
    if phase_thresholds:
        for phase_num, threshold_health in phase_thresholds.items():
            # Only draw markers for phases that are not yet passed (or the current one's start)
            # and for thresholds that are not 0 (final defeat)
            if threshold_health > 0 and threshold_health < max_health :
                 # Check if this phase is "above" the current health, or if it's a future phase start
                if current_health < threshold_health or (current_phase_val and phase_num >= current_phase_val):
                    marker_x = x + (threshold_health / max_health) * width
                    pygame.draw.line(surface, WHITE, (marker_x, y), (marker_x, y + height), 2)


def draw_spell_card_name(surface, text):
    if not ui_font or not text: return
    text_surface = ui_font.render(text, True, WHITE)
    # Position to the right of the health bar, or centered if no health bar shown
    text_rect = text_surface.get_rect(topright=(SCREEN_WIDTH - 10, 10)) # Aligned to top-right
    surface.blit(text_surface, text_rect)


def main():
    global current_state, current_menu_selection, selected_difficulty
    global screen_flash_alpha, screen_flash_timer
    global last_enemy_spawn_time
    global reisen_instance, reisen_defeated_effect_timer
    global kaguya_instance, kaguya_spawn_timer, kaguya_defeat_effect_timer
    global ui_font, big_font, menu_font, menu_cursor_image # Add menu_font
    
    game_start_time = 0 
    asset_manager = AssetManager() 

    running = True
    clock = pygame.time.Clock()

    player = Player(asset_manager) 
    
    ui_font = pygame.font.Font(None, 30) 
    big_font = pygame.font.Font(None, 74)
    menu_font = pygame.font.Font(None, 48) # Initialize menu_font
    menu_cursor_image = asset_manager.get_image("ui_menu_cursor", scale_to=(30,30))

    # Sprite groups
    enemies = pygame.sprite.Group() 
    items = pygame.sprite.Group()
    all_player_bullets = player.bullets 
    all_enemy_bullets = pygame.sprite.Group()

    def reset_game_state():
        nonlocal game_start_time, player, enemies, items, all_player_bullets, all_enemy_bullets
        nonlocal reisen_instance, reisen_defeated_effect_timer
        nonlocal kaguya_instance, kaguya_spawn_timer, kaguya_defeat_effect_timer
        
        game_start_time = 0 
        player = Player(asset_manager) # Pass asset_manager
        all_player_bullets = player.bullets
        enemies.empty()
        items.empty()
        all_enemy_bullets.empty()
        reisen_instance = None
        reisen_defeated_effect_timer = 0
        kaguya_instance = None
        kaguya_spawn_timer = 0
        kaguya_defeat_effect_timer = 0
        # Ensure screen flash is also reset
        global screen_flash_timer, screen_flash_alpha
        screen_flash_timer = 0
        screen_flash_alpha = 0


    while running:
        current_time_ticks = pygame.time.get_ticks() 
        
        if current_state == GAMEPLAY and game_start_time == 0:
            game_start_time = current_time_ticks
            last_enemy_spawn_time = current_time_ticks 

        gameplay_duration = current_time_ticks - game_start_time if game_start_time > 0 else 0
        keys = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if current_state == TITLE_SCREEN:
                    if event.key == pygame.K_RETURN:
                        reset_game_state() # Resets player, bosses, timers etc.
                        current_state = GAMEPLAY # Default to gameplay for now
                        # current_menu_selection = 0 # Reset for difficulty if it's the next state
                        print(f"Starting game with difficulty: {selected_difficulty}")
                    elif current_state == DIFFICULTY_SELECT:
                        if menu_options_difficulty[current_menu_selection] == "Easy": selected_difficulty = "Easy"
                        elif menu_options_difficulty[current_menu_selection] == "Normal": selected_difficulty = "Normal"
                        elif menu_options_difficulty[current_menu_selection] == "Hard": selected_difficulty = "Hard"
                        elif menu_options_difficulty[current_menu_selection] == "Lunatic": selected_difficulty = "Lunatic"
                        print(f"Difficulty selected: {selected_difficulty}")
                        current_state = GAMEPLAY
                        reset_game_state() # Full reset before gameplay starts with new difficulty
                        game_start_time = 0 # Ensure timer resets for gameplay
                        last_enemy_spawn_time = pygame.time.get_ticks() # Reset spawn timer for Zako
                    elif current_state == OPTIONS_SCREEN:
                        if menu_options_options_page[current_menu_selection] == "Back":
                            current_state = TITLE_SCREEN
                            current_menu_selection = 0 # Reset for title screen menu
                    elif current_state == GAME_OVER:
                        is_clear = not (kaguya_instance and kaguya_instance.alive()) # Simplified clear check
                        options = menu_options_game_clear if is_clear else menu_options_game_over
                        action = options[current_menu_selection]
                        if action == "Retry" or action == "Play Again":
                            reset_game_state()
                            current_state = DIFFICULTY_SELECT # Or GAMEPLAY if no difficulty screen
                            current_menu_selection = 0
                        elif action == "Quit to Title":
                            reset_game_state()
                            current_state = TITLE_SCREEN
                            current_menu_selection = 0


        # Update game state
        if current_state == GAMEPLAY:
            # Player lives and bombs are now attributes of the Player class
            # player.score, player.power, player.graze need to be added if not already
            # For now, these are conceptual.
            
            if not hasattr(player, 'lives'): player.lives = 3 # Initialize if not present
            if not hasattr(player, 'bombs'): player.bombs = 2 # Initialize if not present

            player.update(keys) # Player update might use bombs, affecting player.bombs

            if hasattr(player, 'trigger_screen_flash') and player.trigger_screen_flash:
                screen_flash_alpha = 200 
                screen_flash_timer = screen_flash_duration
                player.trigger_screen_flash = False

            # --- Boss Logic --- (Reisen and Kaguya)
            if not reisen_instance and not kaguya_instance and gameplay_duration > reisen_spawn_time and \
               reisen_defeated_effect_timer == 0 and kaguya_spawn_timer == 0 and kaguya_defeat_effect_timer == 0:
                reisen_instance = Reisen(position=(SCREEN_WIDTH // 2, 100), asset_manager=asset_manager)
            
            if reisen_instance and reisen_instance.alive():
                reisen_instance.update(player.rect.center) 
                for bullet in reisen_instance.bullets: all_enemy_bullets.add(bullet)
                reisen_instance.bullets.empty()
            elif reisen_instance and not reisen_instance.alive() and reisen_defeated_effect_timer == 0:
                reisen_defeated_effect_timer = REISEN_DEFEATED_EFFECT_DURATION
                for _ in range(10): items.add(create_item(reisen_instance.rect.center, asset_manager, TYPE_SCORE))
                items.add(create_item(reisen_instance.rect.center, asset_manager, TYPE_BOMB))
                items.add(create_item(reisen_instance.rect.center, asset_manager, TYPE_POWER))
            
            if reisen_defeated_effect_timer > 0:
                reisen_defeated_effect_timer -=1
                if reisen_defeated_effect_timer == 0:
                    if reisen_instance: reisen_instance.kill()
                    reisen_instance = None
                    kaguya_spawn_timer = current_time_ticks 

            # Kaguya
            if not kaguya_instance and not reisen_instance and kaguya_spawn_timer > 0 and \
               (current_time_ticks - kaguya_spawn_timer > KAGUYA_SPAWN_DELAY_AFTER_REISEN) and kaguya_defeat_effect_timer == 0:
                kaguya_instance = Kaguya(position=(SCREEN_WIDTH // 2, 150), asset_manager=asset_manager)
                kaguya_spawn_timer = 0 

            if kaguya_instance and kaguya_instance.alive():
                kaguya_instance.update(player.rect.center)
                if hasattr(kaguya_instance, 'trigger_phase_transition_effect') and kaguya_instance.trigger_phase_transition_effect:
                    screen_flash_alpha = 180 # Phase transition flash can be less intense or different color
                    screen_flash_timer = PHASE_TRANSITION_FLASH_DURATION
                    kaguya_instance.trigger_phase_transition_effect = False
                for bullet in kaguya_instance.bullets: all_enemy_bullets.add(bullet)
                kaguya_instance.bullets.empty()
            elif kaguya_instance and not kaguya_instance.alive() and kaguya_defeat_effect_timer == 0: 
                kaguya_defeat_effect_timer = KAGUYA_DEFEAT_EFFECT_DURATION
                for _ in range(20): items.add(create_item(kaguya_instance.rect.center, asset_manager, TYPE_SCORE))
                for _ in range(3): items.add(create_item(kaguya_instance.rect.center, asset_manager, TYPE_POWER))

            if kaguya_defeat_effect_timer > 0:
                kaguya_defeat_effect_timer -=1
                if kaguya_defeat_effect_timer == 0:
                    if kaguya_instance: kaguya_instance.kill()
                    kaguya_instance = None
                    current_state = GAME_OVER 

            # Zako Enemy Spawning
            if not reisen_instance and not kaguya_instance and kaguya_spawn_timer == 0 and \
               reisen_defeated_effect_timer == 0 and kaguya_defeat_effect_timer == 0:
                 if current_time_ticks - last_enemy_spawn_time > enemy_spawn_delay: # Ensure last_enemy_spawn_time is valid
                    last_enemy_spawn_time = current_time_ticks
                    enemies.add(ZakoEnemy(position=(random.randint(50, SCREEN_WIDTH - 50), 0), asset_manager=asset_manager))

            enemies.update() 
            items.update() # Items might give power, score
            all_enemy_bullets.update() 

            for enemy in enemies: 
                for bullet in enemy.bullets: all_enemy_bullets.add(bullet) 
                enemy.bullets.empty() 

            # Collision Detection
            for bullet in list(all_player_bullets): 
                hit_zako = pygame.sprite.spritecollide(bullet, enemies, False, pygame.sprite.collide_rect_ratio(0.8))
                for zako in hit_zako:
                    if bullet.alive(): bullet.kill() 
                    if zako.take_damage(1): 
                        if hasattr(zako, 'dropped_item_info') and zako.dropped_item_info:
                            items.add(create_item(zako.dropped_item_info['position'], asset_manager, zako.dropped_item_info['type']))
                
                if reisen_instance and reisen_instance.alive() and reisen_instance.is_active:
                    if pygame.sprite.collide_rect(bullet, reisen_instance): 
                        if bullet.alive(): bullet.kill()
                        reisen_instance.take_damage(1)
                
                if kaguya_instance and kaguya_instance.alive() and kaguya_instance.is_active:
                    if pygame.sprite.collide_rect(bullet, kaguya_instance):
                        if bullet.alive(): bullet.kill()
                        kaguya_instance.take_damage(1) 

            player_hitbox_rect = pygame.Rect(0,0, player.hitbox_radius*2, player.hitbox_radius*2)
            player_hitbox_rect.center = player.rect.center
            
            # Graze detection (conceptual)
            # graze_radius_squared = (player.hitbox_radius + 5)**2 # Example graze radius
            # for bullet in all_enemy_bullets:
            #    dist_sq = (bullet.rect.centerx - player.rect.centerx)**2 + (bullet.rect.centery - player.rect.centery)**2
            #    if dist_sq < graze_radius_squared and not player_hitbox_rect.colliderect(bullet.rect):
            #        player.graze +=1 # Assuming player.graze attribute
            #        print(f"Graze! Count: {player.graze}") # Add to UI later

            for bullet in all_enemy_bullets: # Actual hit detection
                if player_hitbox_rect.colliderect(bullet.rect):
                    if player.show_hitbox: # Only vulnerable if hitbox is shown 
                        print("Player hit!")
                        bullet.kill() 
                        player.lives -= 1
                        if player.lives <= 0:
                            current_state = GAME_OVER 
                            current_menu_selection = 0 # Reset for game over menu
                        # Add invincibility frames later

        # Render screen
        screen.fill(BLACK) 

        if current_state == TITLE_SCREEN:
            draw_title_screen_layout(asset_manager)
        elif current_state == DIFFICULTY_SELECT:
            draw_difficulty_select_layout(asset_manager)
        elif current_state == OPTIONS_SCREEN:
            draw_options_screen_layout(asset_manager)
        elif current_state == GAMEPLAY:
            player.draw(screen) 
            enemies.draw(screen) 
            
            active_boss_instance = kaguya_instance if kaguya_instance else reisen_instance
            if active_boss_instance and active_boss_instance.alive():
                active_boss_instance.draw(screen)
                health_color = (255,0,0) 
                phase_thresholds_for_bar = None
                current_phase_for_bar = None

                if isinstance(active_boss_instance, Kaguya):
                    health_color = (200,0,200) 
                    phase_thresholds_for_bar = active_boss_instance.phase_health_thresholds
                    current_phase_for_bar = active_boss_instance.current_phase
                elif isinstance(active_boss_instance, Reisen):
                     pass 

                draw_health_bar(screen, active_boss_instance.health, active_boss_instance.initial_health,
                                SCREEN_WIDTH * 0.15, 35, SCREEN_WIDTH * 0.7, 20, health_color,
                                phase_thresholds_for_bar, current_phase_for_bar)
                
                if active_boss_instance.spell_card_active and active_boss_instance.current_spell_name:
                    draw_spell_card_name(screen, f"{active_boss_instance.current_spell_name}")

            # In-Game UI Text (Score, Lives, Bombs etc.)
            # Conceptual: these values would come from player object or game manager
            # draw_text(screen, f"Score: {getattr(player, 'score', 0)}", ui_font, WHITE, 100, 10, asset_manager=asset_manager)
            # draw_text(screen, f"Lives: {getattr(player, 'lives', 3)}", ui_font, WHITE, SCREEN_WIDTH - 100, 10, asset_manager=asset_manager)
            # draw_text(screen, f"Bombs: {getattr(player, 'bombs', 2)}", ui_font, WHITE, SCREEN_WIDTH - 100, 40, asset_manager=asset_manager)
            # draw_text(screen, f"Power: {getattr(player, 'power', 0)}/128", ui_font, WHITE, 100, 40, asset_manager=asset_manager)
            # draw_text(screen, f"Graze: {getattr(player, 'graze', 0)}", ui_font, WHITE, 100, 70, asset_manager=asset_manager)


            if reisen_defeated_effect_timer > 0 and reisen_defeated_effect_timer % 20 < 10 : 
                defeat_flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                defeat_flash_surface.fill((255,0,0, 100)) 
                screen.blit(defeat_flash_surface, (0,0))
            
            if kaguya_defeat_effect_timer > 0 and kaguya_defeat_effect_timer % 15 < 8: 
                defeat_flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                defeat_flash_surface.fill((255,255,255, 120)) 
                screen.blit(defeat_flash_surface, (0,0))

            items.draw(screen)
            all_enemy_bullets.draw(screen) 

        elif current_state == GAME_OVER:
            is_clear = player.lives > 0 and not (kaguya_instance and kaguya_instance.alive()) # Simplified: if player alive & Kaguya gone
            # More robust check: if Kaguya was spawned and defeated, it's a clear.
            if hasattr(main, 'kaguya_was_spawned_flag_for_clear_check') and main.kaguya_was_spawned_flag_for_clear_check and \
               not (kaguya_instance and kaguya_instance.alive()) and player.lives > 0:
                is_clear = True
            elif player.lives <=0:
                is_clear = False # Definitely not a clear if player is out of lives

            draw_game_over_layout(asset_manager, is_clear)

        if screen_flash_timer > 0:
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA) # Flash is white
            flash_surface.fill((255, 255, 255, screen_flash_alpha)) # White flash as base
            # Potentially change color based on source of flash if needed here
            screen.blit(flash_surface, (0,0))
            screen_flash_timer -= 1
            if screen_flash_timer > 0 :
                 screen_flash_alpha = int(screen_flash_alpha * 0.9) # Fade out
            else:
                screen_flash_alpha = 0

        pygame.display.flip()
        clock.tick(60)  # Limit to 60 FPS

    pygame.quit()

if __name__ == '__main__':
    main()
