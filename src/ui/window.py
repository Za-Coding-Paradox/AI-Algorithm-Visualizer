import pygame

class ApplicationDisplayWindow:
    def __init__(self, pixel_width, window_title="AI Algorithm Visualizer"):
        self.pixel_width = pixel_width
        self.display_surface = pygame.display.set_mode((pixel_width, pixel_width))
        pygame.display.set_caption(window_title)

    def refresh_screen_content(self):
        """Standard Pygame display update call."""
        pygame.display.flip()

    def get_drawing_surface(self):
        """Returns the surface for other modules to draw on."""
        return self.display_surface
