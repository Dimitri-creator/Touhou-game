import pygame

class Item:
    def __init__(self, x, y, item_type, image_surface, speed_y=2):
        """
        Initializes an item object.
        :param x: The initial x-coordinate of the item's center.
        :param y: The initial y-coordinate of the item's center.
        :param item_type: String identifier for the item type (e.g., "point", "power").
        :param image_surface: The pygame.Surface object representing the item's image.
        :param speed_y: The vertical speed at which the item falls.
        """
        self.item_type = item_type
        self.image = image_surface
        self.rect = self.image.get_rect(center=(x, y))
        self.speed_y = speed_y

    def update(self):
        """
        Updates the item's position by moving it downwards.
        """
        self.rect.y += self.speed_y

    def draw(self, surface):
        """
        Draws the item on the given surface.
        :param surface: The pygame.Surface to draw the item on.
        """
        surface.blit(self.image, self.rect)

    def is_offscreen(self, screen_height):
        """
        Checks if the item is off the bottom of the screen.
        :param screen_height: The height of the game screen.
        :return: True if the item is offscreen, False otherwise.
        """
        return self.rect.top > screen_height

if __name__ == '__main__':
    # Optional: Basic test for the Item class
    pygame.init()

    screen_width_test = 800
    screen_height_test = 600
    screen_test = pygame.display.set_mode((screen_width_test, screen_height_test))
    pygame.display.set_caption("Item Class Test")

    # Create dummy item images
    point_item_image = pygame.Surface((12, 12))
    pygame.draw.circle(point_item_image, (0, 0, 255), (6, 6), 6) # Blue circle
    point_item_image.set_colorkey((0,0,0)) # Make black background transparent for circle

    power_item_image = pygame.Surface((12, 12))
    power_item_image.fill((255, 0, 0)) # Red square

    # Create item instances
    item1 = Item(screen_width_test // 2, 50, "point", point_item_image)
    item2 = Item(screen_width_test // 2 + 50, 50, "power", power_item_image, speed_y=3)
    
    items_on_screen = [item1, item2]

    running_test = True
    clock = pygame.time.Clock()

    print("Item Test: A blue circle (point) and a red square (power) should fall downwards.")
    
    test_duration_frames = 180 # Run for about 3 seconds
    frame_count = 0

    while running_test and frame_count < test_duration_frames:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running_test = False
        
        screen_test.fill((50, 50, 50)) # Dark Gray

        for item_obj in list(items_on_screen):
            item_obj.update()
            item_obj.draw(screen_test)
            if item_obj.is_offscreen(screen_height_test):
                print(f"Item '{item_obj.item_type}' went offscreen.")
                items_on_screen.remove(item_obj)
        
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1

    print(f"Test finished. {len(items_on_screen)} items remaining on screen.")
    pygame.quit()
