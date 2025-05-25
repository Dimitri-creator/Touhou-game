import pygame

# Initialize Pygame's font module (can be done once globally, e.g., in main.py as well)
# For modularity, it's fine here if ui.py is always imported when UI is needed.
# If multiple modules use pygame.font, initializing in main.py might be cleaner.
pygame.font.init() 

UI_FONT_SIZE = 28
UI_FONT = pygame.font.Font(None, UI_FONT_SIZE)  # Uses default system font
TEXT_COLOR = (255, 255, 255)  # White

def draw_text(surface, text, x, y, font=UI_FONT, color=TEXT_COLOR):
    """
    Renders and blits text onto a surface.
    :param surface: The pygame.Surface to draw on.
    :param text: The string to render.
    :param x: The x-coordinate for the top-left of the text.
    :param y: The y-coordinate for the top-left of the text.
    :param font: The pygame.font.Font object to use.
    :param color: The color of the text.
    """
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

def draw_game_ui(surface, score, lives, bombs, power, graze, screen_width):
    """
    Draws all the game UI elements (Score, Lives, Bombs, Power, Graze) onto the screen.
    :param surface: The main game screen surface.
    :param score: Current player score.
    :param lives: Current player lives.
    :param bombs: Current player bombs.
    :param power: Current player power level.
    :param graze: Current player graze count.
    :param screen_width: The width of the game screen.
    """
    # Left-aligned UI elements
    draw_text(surface, f"Score: {score}", 10, 10)
    draw_text(surface, f"Power: {power} / 128", 10, 10 + UI_FONT_SIZE + 5)
    draw_text(surface, f"Graze: {graze}", 10, 10 + (UI_FONT_SIZE + 5) * 2)

    # Right-aligned UI elements
    # For right alignment, we need to calculate the width of the text first
    
    lives_text = f"Lives: {lives}"
    # Render once to get width for positioning, then draw_text handles rendering again
    lives_text_surface = UI_FONT.render(lives_text, True, TEXT_COLOR)
    lives_rect = lives_text_surface.get_rect()
    draw_text(surface, lives_text, screen_width - lives_rect.width - 10, 10)

    bombs_text = f"Bombs: {bombs}"
    # Render once to get width for positioning
    bombs_text_surface = UI_FONT.render(bombs_text, True, TEXT_COLOR)
    bombs_rect = bombs_text_surface.get_rect()
    draw_text(surface, bombs_text, screen_width - bombs_rect.width - 10, 10 + UI_FONT_SIZE + 5)

if __name__ == '__main__':
    # Optional: Basic test for the UI functions
    pygame.init() # Ensure Pygame is initialized if not already by font.init()

    screen_width_test = 800
    screen_height_test = 600
    screen_test = pygame.display.set_mode((screen_width_test, screen_height_test))
    pygame.display.set_caption("UI Test")

    # Test values
    test_score = 12345
    test_lives = 3
    test_bombs = 2
    test_power = 64
    test_graze = 100

    running_test = True
    clock = pygame.time.Clock()

    print("UI Test: Displaying Score, Lives, Bombs, Power, and Graze.")
    
    frame_count = 0
    test_duration_frames = 180 # Display for a few seconds

    while running_test and frame_count < test_duration_frames:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_test = False
        
        screen_test.fill((50, 50, 50)) # Dark Gray background

        # Draw the UI
        draw_game_ui(screen_test, test_score, test_lives, test_bombs, test_power, test_graze, screen_width_test)
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1

    print("UI Test finished.")
    pygame.quit()
