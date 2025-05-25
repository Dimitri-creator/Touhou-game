import pygame

class Bullet:
    def __init__(self, x, y, dx, dy, image_surface):
        """
        Initializes a bullet object.
        :param x: The initial x-coordinate of the bullet's center.
        :param y: The initial y-coordinate of the bullet's center.
        :param dx: The horizontal speed component of the bullet.
        :param dy: The vertical speed component of the bullet.
        :param image_surface: The pygame.Surface object representing the bullet's image.
        """
        self.image = image_surface
        self.rect = self.image.get_rect(center=(x, y))
        self.dx = dx
        self.dy = dy

    def update(self):
        """
        Updates the bullet's position based on its speed.
        """
        self.rect.x += self.dx
        self.rect.y += self.dy

    def draw(self, surface):
        """
        Draws the bullet on the given surface.
        :param surface: The pygame.Surface to draw the bullet on.
        """
        surface.blit(self.image, self.rect)

    def is_offscreen(self, screen_width, screen_height):
        """
        Checks if the bullet is completely off the screen.
        :param screen_width: The width of the game screen.
        :param screen_height: The height of the game screen.
        :return: True if the bullet is offscreen, False otherwise.
        """
        return (self.rect.bottom < 0 or
                self.rect.top > screen_height or
                self.rect.right < 0 or
                self.rect.left > screen_width)

if __name__ == '__main__':
    # Optional: Basic test for the Bullet class
    pygame.init()

    # Create a dummy screen for testing
    screen_width_test = 800
    screen_height_test = 600
    screen_test = pygame.display.set_mode((screen_width_test, screen_height_test))
    pygame.display.set_caption("Bullet Class Test")

    # Create a dummy bullet image (a small red square)
    dummy_bullet_image = pygame.Surface((10, 10))
    dummy_bullet_image.fill((255, 0, 0)) # Red color

    # Create a bullet instance
    bullet = Bullet(screen_width_test // 2, screen_height_test // 2, 0, -5, dummy_bullet_image) # Shoots upwards

    # Create another bullet that will go offscreen quickly
    offscreen_bullet = Bullet(10, 10, -20, 0, dummy_bullet_image) # Shoots left

    bullets_on_screen = [bullet, offscreen_bullet]

    running_test = True
    clock = pygame.time.Clock()

    print("Bullet Test: A red bullet should move upwards from the center.")
    print("Another red bullet should move quickly to the left and disappear.")

    test_duration_frames = 120 # Run test for about 2 seconds at 60 FPS
    frame_count = 0

    while running_test and frame_count < test_duration_frames:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_test = False
        
        screen_test.fill((50, 50, 50)) # Dark Gray

        # Update and draw bullets
        for b in list(bullets_on_screen): # Iterate over a copy for safe removal
            b.update()
            b.draw(screen_test)
            if b.is_offscreen(screen_width_test, screen_height_test):
                print(f"Bullet at ({b.rect.x}, {b.rect.y}) went offscreen.")
                bullets_on_screen.remove(b)
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1

    print(f"Test finished. {len(bullets_on_screen)} bullets remaining on screen (should be 1 if test ran long enough).")
    pygame.quit()
